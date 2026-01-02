// client/hooks/use-boards.ts
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

export const useBoards = (workspaceId: string) => {
  return useQuery({
    queryKey: ["boards", workspaceId],
    queryFn: async () => {
      const { data } = await axios.get(`/api/workspaces/${workspaceId}/boards`);
      return data;
    },
    enabled: !!workspaceId,
  });
};