// client/hooks/use-rename-board.ts
export const useRenameBoard = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateBoardTitle,
    onMutate: async (newBoard) => {
      await queryClient.cancelQueries({ queryKey: ['boards'] });
      const previousBoards = queryClient.getQueryData(['boards']);
      queryClient.setQueryData(['boards'], (old: any) => 
        old.map((b: any) => b.id === newBoard.id ? { ...b, title: newBoard.title } : b)
      );
      return { previousBoards };
    },
    onError: (err, newBoard, context) => {
      queryClient.setQueryData(['boards'], context?.previousBoards);
    },
  });
};