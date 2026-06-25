const express = require("express");
const { checkout } = require("../controllers/checkoutController");

const router = express.Router();

router.post("/api/checkout", async (req, res, next) => {
  try {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;
    const result = await checkout(name, email, password, courseId, cardNumber);
    if (!result.success) {
      return res.status(result.status).json({ error: result.error });
    }
    res.status(200).json({ msg: "Sucesso", enrollment_id: result.enrollmentId });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
