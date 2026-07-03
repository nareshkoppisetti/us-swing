import { create } from "zustand";
export const useSymbolStore = create((set) => ({
  currentSymbol: null, ohlcv: null, agentOutputs: [], predictions: [],
  setSymbol: (symbol) => set({ currentSymbol: symbol }),
  setSymbolData: (data) => set(data),
}));
