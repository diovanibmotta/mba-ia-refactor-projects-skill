const { wrap, getDb } = require("./db");

async function log(action) {
  const pdb = wrap(getDb());
  await pdb.run(
    "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
    [action]
  );
}

module.exports = { log };
