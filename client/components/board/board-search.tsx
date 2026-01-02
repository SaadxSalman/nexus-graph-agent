// client/components/board/board-search.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

interface BoardSearchProps {
  value: string;
  onChange: (value: string) => void;
}

export const BoardSearch = ({ value, onChange }: BoardSearchProps) => {
  return (
    <div className="relative w-full max-w-sm">
      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Filter tasks by name or tag..."
        value={value}
        onChange={(e) => onChange(e.target.target.value)}
        className="pl-8"
      />
    </div>
  );
};