const { wrap, getDb } = require("./db");

async function create(userId, courseId) {
  const pdb = wrap(getDb());
  const result = await pdb.run(
    "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
    [userId, courseId]
  );
  return result.lastID;
}

async function createPayment(enrollmentId, amount, status) {
  const pdb = wrap(getDb());
  await pdb.run(
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
    [enrollmentId, amount, status]
  );
}

module.exports = { create, createPayment };
