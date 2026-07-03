/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,jsx,ts,tsx}',
    './src/components/**/*.{js,jsx,ts,tsx}',
    './src/app/**/*.{js,jsx,ts,tsx}',
    './src/lib/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          green: '#2A7A6F',
          'green-light': '#3A9E8F',
          'green-dark': '#1B5E20',
          'green-muted': '#E8F5E9',
          red: '#B5451B',
          'red-light': '#D4622E',
          'red-dark': '#B71C1C',
          'red-muted': '#FFEBEE',
        },
        surface: {
          light: '#FFFFFF',
          muted: '#F8F9FA',
          border: '#E9ECEF',
          dark: '#0F1117',
          'dark-card': '#1A1D27',
          'dark-border': '#2A2D3E',
        },
        // Keep compatibility with existing frontend code
        background: 'var(--bg-primary)',
        card: 'var(--bg-card)',
        bullish: '#22c55e',
        bearish: '#ef4444',
        neutral: '#eab308',
        accent: '#3b82f6',
      },
      fontFamily: {
        display: ['Georgia', 'serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-green': 'pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
      },
      keyframes: {
        'pulse-green': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}
