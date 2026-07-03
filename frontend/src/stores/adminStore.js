import { create } from "zustand";
export const useAdminStore = create((set) => ({
  systemMetrics: null, agentHealth: [], dataSourceHealth: [], modelMetrics: [],
  setSystemMetrics: (data) => set({ systemMetrics: data }),
  setAgentHealth: (data) => set({ agentHealth: data }),
}));
