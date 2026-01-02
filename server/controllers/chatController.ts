// server/controllers/chatController.ts
export const handleMessage = async (msgData) => {
  // 1. Save to MongoDB
  const newMessage = await Chat.create(msgData);
  // 2. Broadcast to Room
  io.to(msgData.boardId).emit("new-message", newMessage);
};