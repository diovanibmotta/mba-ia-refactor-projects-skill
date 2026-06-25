module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  smtpUser: process.env.SMTP_USER || "",
  secretKey: process.env.SECRET_KEY || "dev-only-change-in-production",
  port: parseInt(process.env.PORT || "3000"),
  nodeEnv: process.env.NODE_ENV || "development",
};
