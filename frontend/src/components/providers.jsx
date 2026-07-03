'use client'
import { createContext, useContext, useEffect, useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

// ── Query Client ───────────────────────────────────────────────────────────────
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

// ── Theme context ──────────────────────────────────────────────────────────────
const ThemeContext = createContext({ theme: 'light', toggleTheme: () => {} })
export const useTheme = () => useContext(ThemeContext)

export function Providers({ children }) {
  const [theme, setTheme] = useState('dark')
  useEffect(() => {
    const storedTheme = localStorage.getItem('usa-swing-theme') || 'dark'
    setTheme(storedTheme)
    document.documentElement.classList.toggle('dark', storedTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const next = theme === 'light' ? 'dark' : 'light'
    setTheme(next)
    localStorage.setItem('usa-swing-theme', next)
    document.documentElement.classList.toggle('dark', next === 'dark')
  }


  return (
    <QueryClientProvider client={queryClient}>
      <ThemeContext.Provider value={{ theme, toggleTheme }}>
        <>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: theme === 'dark' ? '#1A1D27' : '#fff',
                color: theme === 'dark' ? '#F0F2F5' : '#1A1D27',
                border: `1px solid ${theme === 'dark' ? '#2A2D3E' : '#E9ECEF'}`,
                fontFamily: "'DM Sans', sans-serif",
              },
            }}
          />
        </>
      </ThemeContext.Provider>
    </QueryClientProvider>
  )
}

// Export queryClient for direct use in lib/api.js if needed
export { queryClient }
