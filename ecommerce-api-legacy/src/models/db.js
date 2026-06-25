const sqlite3 = require("sqlite3").verbose();
const { promisify } = require("util");

let instance = null;

function getDb() {
  if (!instance) {
    instance = new sqlite3.Database(":memory:");
  }
  return instance;
}

function wrap(db) {
  return {
    get: promisify(db.get.bind(db)),
    all: promisify(db.all.bind(db)),
    run: (sql, params = []) =>
      new Promise((resolve, reject) => {
        db.run(sql, params, function (err) {
          if (err) reject(err);
          else resolve({ lastID: this.lastID, changes: this.changes });
        });
      }),
    serialize: (fn) => db.serialize(fn),
  };
}

module.exports = { getDb, wrap };
