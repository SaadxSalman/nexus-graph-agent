// client/components/board/board-container.tsx
"use client";

import { useMemo, useState } from "react";
import { BoardSearch } from "./board-search";

export const BoardContainer = ({ initialTasks }: { initialTasks: any[] }) => {
  const [searchQuery, setSearchQuery] = useState("");

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
      {/* Pass filteredTasks to your Kanban Columns here */}
    </div>
  );
};