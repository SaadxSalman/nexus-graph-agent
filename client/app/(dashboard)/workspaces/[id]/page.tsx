// client/app/(dashboard)/workspaces/[id]/page.tsx
import { Suspense } from "react";
import { BoardSkeleton } from "@/components/board/skeleton";

export default function BoardPage() {
  return (
    <div className="flex flex-col gap-4">
      <BoardHeader />
      <Suspense fallback={<BoardSkeleton />}>
        <KanbanBoard /> {/* Data-heavy component */}
      </Suspense>
    </div>
  );
}