// client/hooks/use-notifications.ts
socket.on("mention", (data) => {
  toast({
    title: "New Mention",
    description: `${data.sender} mentioned you in ${data.taskTitle}`,
  });
});