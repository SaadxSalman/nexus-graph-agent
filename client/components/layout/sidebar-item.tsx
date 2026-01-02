// client/components/layout/sidebar-item.tsx
"use client";

import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { fetchBoard } from "@/lib/api/boards"; // Centralized API call

interface SidebarItemProps {
  id: string;
  title: string;
  href: string;
}

export const SidebarItem = ({ id, title, href }: SidebarItemProps) => {
  const queryClient = useQueryClient();

  const handleMouseEnter = () => {
    // Prefetch the board data into TanStack Query cache
    queryClient.prefetchQuery({
      queryKey: ["board", id],
      queryFn: () => fetchBoard(id),
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 mins
    });
  };

  return (
    <Link 
      href={href}
      onMouseEnter={handleMouseEnter}
      className="flex items-center gap-x-2 p-2 hover:bg-accent rounded-md transition"
    >
      <span className="truncate">{title}</span>
    </Link>
  );
};