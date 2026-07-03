import { create } from "zustand";
export const useAgentStore = create((set) => ({
  agentStatuses: {},    // { [agentId]: { status, lastRun, score } }
  agentOutputs: {},     // { [agentId]: AgentOutput }
  setAgentStatus: (id, status) => set((s) => ({
    agentStatuses: { ...s.agentStatuses, [id]: status }
  })),
  setAgentOutput: (id, output) => set((s) => ({
    agentOutputs: { ...s.agentOutputs, [id]: output }
  })),
}));
