const settings = require("../config/settings");

function errorHandler(err, req, res, next) {
  console.error(`[ERROR] ${err.name}: ${err.message}`);
  const message =
    settings.nodeEnv === "production" ? "Internal server error" : err.message;
  res.status(err.status || 500).json({ error: message });
}

module.exports = { errorHandler };
