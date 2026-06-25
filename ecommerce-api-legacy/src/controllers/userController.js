const userModel = require("../models/userModel");

async function deleteUser(userId) {
  if (!userId) {
    return { success: false, status: 400, error: "User ID is required" };
  }
  await userModel.deleteById(userId);
  return { success: true };
}

module.exports = { deleteUser };
