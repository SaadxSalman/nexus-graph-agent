// server/state.ts
const activeUsers = new Map(); // boardId -> Set of userIds

socket.on("join-board", ({ boardId, user }) => {
  activeUsers.get(boardId).add(user);
  io.to(boardId).emit("presence-update", Array.from(activeUsers.get(boardId)));
});