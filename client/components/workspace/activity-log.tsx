// client/components/workspace/activity-log.tsx
"use client";

import { useActivityLogs } from "@/hooks/use-activity-logs";
import { useInView } from "react-intersection-observer";
import { useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";

export const ActivityLog = ({ workspaceId }: { workspaceId: string }) => {
  const { ref, inView } = useInView();
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useActivityLogs(workspaceId);

  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, fetchNextPage]);

  return (
    <div className="flex flex-col gap-y-4">
      {data?.pages.map((page) =>
        page.logs.map((log: any) => (
          <div key={log._id} className="p-3 border-b text-sm">
            {log.content}
          </div>
        ))
      )}
      
      {/* The sentinel element */}
      <div ref={ref}>
        {isFetchingNextPage && <Skeleton className="h-10 w-full" />}
      </div>
    </div>
  );
};