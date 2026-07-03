import { create } from 'zustand'

export const useUIStore = create((set) => ({
  sidebarOpen: true,
  searchPanelOpen: false,
  selectedSymbol: null,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  openSearch: () => set({ searchPanelOpen: true }),
  closeSearch: () => set({ searchPanelOpen: false, selectedSymbol: null }),
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol, searchPanelOpen: !!symbol }),
}))
