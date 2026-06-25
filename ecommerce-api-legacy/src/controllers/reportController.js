const courseModel = require("../models/courseModel");

async function getFinancialReport() {
  const rows = await courseModel.getAllWithRevenue();

  const courseMap = {};
  for (const row of rows) {
    if (!courseMap[row.id]) {
      courseMap[row.id] = { course: row.title, revenue: 0, students: [] };
    }
    if (row.student_name) {
      if (row.payment_status === "PAID") {
        courseMap[row.id].revenue += row.payment_amount || 0;
      }
      courseMap[row.id].students.push({
        student: row.student_name,
        paid: row.payment_amount || 0,
      });
    }
  }

  return Object.values(courseMap);
}

module.exports = { getFinancialReport };
