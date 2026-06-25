const userModel = require("../models/userModel");
const courseModel = require("../models/courseModel");
const enrollmentModel = require("../models/enrollmentModel");
const auditModel = require("../models/auditModel");

const VISA_PREFIX = "4";

async function checkout(name, email, password, courseId, cardNumber) {
  if (!name || !email || !courseId || !cardNumber) {
    return { success: false, status: 400, error: "Missing required fields: name, email, courseId, cardNumber" };
  }

  const course = await courseModel.findActiveById(courseId);
  if (!course) {
    return { success: false, status: 404, error: "Course not found or inactive" };
  }

  const paymentStatus = cardNumber.startsWith(VISA_PREFIX) ? "PAID" : "DENIED";
  if (paymentStatus === "DENIED") {
    return { success: false, status: 400, error: "Payment denied" };
  }

  let user = await userModel.findByEmail(email);
  if (!user) {
    user = await userModel.create(name, email, password);
  }

  const enrollmentId = await enrollmentModel.create(user.id, courseId);
  await enrollmentModel.createPayment(enrollmentId, course.price, paymentStatus);
  await auditModel.log(`Checkout course ${courseId} by user ${user.id}`);

  return { success: true, enrollmentId, course: course.title, user: user.name };
}

module.exports = { checkout };
