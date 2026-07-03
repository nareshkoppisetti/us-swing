import { create } from "zustand";

export const usePredictionStore = create((set) => ({
  predictions: {},           // keyed by `${symbol}:${horizon}`
  activePredictions: [],

  setPrediction: (symbol, horizon, data) =>
    set((s) => ({
      predictions: { ...s.predictions, [`${symbol}:${horizon}`]: data },
    })),

  setActivePredictions: (list) => set({ activePredictions: list }),

  getPrediction: (symbol, horizon) => (state) =>
    state.predictions[`${symbol}:${horizon}`] ?? null,
}));
