const bcrypt = require("bcrypt");
const { wrap, getDb } = require("./db");

async function findByEmail(email) {
  const pdb = wrap(getDb());
  return pdb.get("SELECT id, name, email FROM users WHERE email = ?", [email]);
}

async function create(name, email, password) {
  const pdb = wrap(getDb());
  const hash = await bcrypt.hash(password || "changeme", 10);
  const result = await pdb.run(
    "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
    [name, email, hash]
  );
  return { id: result.lastID, name, email };
}

async function deleteById(userId) {
  const pdb = wrap(getDb());
  await pdb.run("DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [userId]);
  await pdb.run("DELETE FROM enrollments WHERE user_id = ?", [userId]);
  await pdb.run("DELETE FROM audit_logs WHERE action LIKE ?", [`%por ${userId}%`]);
  await pdb.run("DELETE FROM users WHERE id = ?", [userId]);
}

module.exports = { findByEmail, create, deleteById };
