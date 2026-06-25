const express = require("express");
const { deleteUser } = require("../controllers/userController");

const router = express.Router();

router.delete("/api/users/:id", async (req, res, next) => {
  try {
    const result = await deleteUser(req.params.id);
    if (!result.success) {
      return res.status(result.status).json({ error: result.error });
    }
    res.json({ message: "Usuario deletado com sucesso" });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
