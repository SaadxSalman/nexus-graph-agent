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

export async function generateMetadata({ params }: { params: { id: string } }) {
  const board = await getBoard(params.id);
  return {
    title: `Nexus | ${board.title}`,
    description: `Manage tasks for ${board.title} in real-time.`,
  };
}