// client/components/board/board-container.tsx
const onDragEnd = (result: any) => {
  const { destination, source, type } = result;
  if (!destination) return;

  // Logic to reorder locally
  const newBoardData = reorderTasks(boardData, source, destination);
  
  // 1. Update UI Optimistically
  setBoardData(newBoardData);

  // 2. Sync with MongoDB
  updateTaskOrderMutation.mutate({
    taskId: result.draggableId,
    newColumnId: destination.droppableId,
    newIndex: destination.index
  });
};