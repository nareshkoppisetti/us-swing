import { create } from "zustand";
export const useAlertStore = create((set) => ({
  alerts: [],
  addAlert: (alert) => set((s) => ({ alerts: [alert, ...s.alerts] })),
  acknowledgeAlert: (id) => set((s) => ({
    alerts: s.alerts.map((a) => a.id === id ? { ...a, status: "acknowledged" } : a)
  })),
}));
