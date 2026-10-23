/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Manrope', 'Plus Jakarta Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        studio: {
          dark: '#0F172A',
          slate: '#1E293B',
          muted: '#64748B',
          cobalt: '#0047FF',
        }
      }
    },
  },
  plugins: [],
}
