const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const bcrypt = require("bcrypt");
const settings = require("./config/settings");
const { getDb } = require("./models/db");
const checkoutRoutes = require("./routes/checkoutRoutes");
const reportRoutes = require("./routes/reportRoutes");
const userRoutes = require("./routes/userRoutes");
const { errorHandler } = require("./middlewares/errorHandler");

const app = express();
app.use(express.json());

async function initDb() {
  const db = getDb();
  await new Promise((resolve) => {
    db.serialize(async () => {
      db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
      db.run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
      db.run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
      db.run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
      db.run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

      const seedPass = await bcrypt.hash("123456", 10);
      db.run("INSERT OR IGNORE INTO users (id, name, email, pass) VALUES (1, 'Leonan', 'leonan@fullcycle.com.br', ?)", [seedPass]);
      db.run("INSERT OR IGNORE INTO courses (id, title, price, active) VALUES (1, 'Clean Architecture', 997.00, 1)");
      db.run("INSERT OR IGNORE INTO courses (id, title, price, active) VALUES (2, 'Docker', 497.00, 1)");
      db.run("INSERT OR IGNORE INTO enrollments (id, user_id, course_id) VALUES (1, 1, 1)");
      db.run("INSERT OR IGNORE INTO payments (id, enrollment_id, amount, status) VALUES (1, 1, 997.00, 'PAID')", resolve);
    });
  });
}

app.use(checkoutRoutes);
app.use(reportRoutes);
app.use(userRoutes);
app.use(errorHandler);

async function start() {
  await initDb();
  app.listen(settings.port, () => {
    console.log(`LMS API running on port ${settings.port}`);
  });
}

start().catch(console.error);

module.exports = app;
