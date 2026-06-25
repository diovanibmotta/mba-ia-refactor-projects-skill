const { wrap, getDb } = require("./db");

async function findActiveById(courseId) {
  const pdb = wrap(getDb());
  return pdb.get("SELECT id, title, price FROM courses WHERE id = ? AND active = 1", [courseId]);
}

async function getAllWithRevenue() {
  const pdb = wrap(getDb());
  return pdb.all(`
    SELECT c.id, c.title, c.price,
           u.name AS student_name,
           p.amount AS payment_amount, p.status AS payment_status
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u ON u.id = e.user_id
    LEFT JOIN payments p ON p.enrollment_id = e.id
    ORDER BY c.id
  `);
}

module.exports = { findActiveById, getAllWithRevenue };
