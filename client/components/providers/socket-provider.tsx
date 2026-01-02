// client/components/providers/socket-provider.tsx
socket.on("disconnect", (reason) => {
  if (reason === "io server disconnect") {
    socket.connect(); // Manually reconnect
  }
});