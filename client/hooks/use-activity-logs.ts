// client/hooks/use-activity-logs.ts
import { useInfiniteQuery } from "@tanstack/react-query";
import axios from "axios";

export const useActivityLogs = (workspaceId: string) => {
  return useInfiniteQuery({
    queryKey: ["activity", workspaceId],
    queryFn: async ({ pageParam = 1 }) => {
      const { data } = await axios.get(`/api/workspaces/${workspaceId}/logs?page=${pageParam}`);
      return data; // Expected return: { logs: [], nextPage: number | null }
    },
    getNextPageParam: (lastPage) => lastPage.nextPage ?? undefined,
    initialPageParam: 1,
  });
};