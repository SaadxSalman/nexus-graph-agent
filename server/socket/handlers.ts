// server/socket/handlers.ts
socket.on("join-board", (boardId) => {
  socket.join(boardId);
});

socket.on("typing", ({ boardId, userName }) => {
  socket.to(boardId).emit("user-typing", { userName });
});