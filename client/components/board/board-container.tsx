"use client";

import { useMemo, useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { socket } from "@/lib/socket"; // Adjust this path to your socket instance
import { BoardSearch } from "./board-search";
import { DragDropContext, DropResult } from "@hello-pangea/dnd";

interface BoardContainerProps {
  initialTasks: any[];
  boardId: string;
}

export const BoardContainer = ({ initialTasks, boardId }: BoardContainerProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const queryClient = useQueryClient();

  // 1. Setup Socket Listener
  useEffect(() => {
    socket.on("task-moved", (data) => {
      // Refresh data from server when another user moves a card
      queryClient.invalidateQueries({ queryKey: ["boards", boardId] });
    });

    return () => {
      socket.off("task-moved");
    };
  }, [boardId, queryClient]);

  // 2. Handle Drag End
  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;

    // Emit the move to the server
    socket.emit("move-task", {
      boardId,
      result,
    });

    // Note: You might want to perform an optimistic update here 
    // using queryClient.setQueryData to make the UI feel instant.
  };

  const filteredTasks = useMemo(() => {
    if (!searchQuery) return initialTasks;
    
    return initialTasks.filter(task => 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.tags?.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  }, [initialTasks, searchQuery]);

  return (
    <div className="space-y-4">
      <BoardSearch value={searchQuery} onChange={setSearchQuery} />
      
      <DragDropContext onDragEnd={onDragEnd}>
        {/* Wrap your Columns/Board sections here */}
        <div className="flex gap-4">
           {/* Render your filteredTasks within Droppable columns here */}
        </div>
      </DragDropContext>
    </div>
  );
};