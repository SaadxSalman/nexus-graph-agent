// client/hooks/use-workspace-store.ts
import { create } from 'zustand';

interface WorkspaceStore {
  activeWorkspaceId: string | null;
  setActiveWorkspace: (id: string) => void;
}

export const useWorkspaceStore = create<WorkspaceStore>((set) => ({
  activeWorkspaceId: null,
  setActiveWorkspace: (id) => set({ activeWorkspaceId: id }),
}));