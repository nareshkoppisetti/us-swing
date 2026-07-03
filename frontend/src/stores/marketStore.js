import { create } from "zustand";
export const useMarketStore = create((set) => ({
  regime: null, breadthScore: null, vixLevel: null,
  setMarketData: (data) => set(data),
}));
