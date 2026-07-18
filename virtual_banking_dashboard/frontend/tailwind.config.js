/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        banking: {
          dark: '#030712',
          card: '#111827',
          accent: '#3b82f6',
          border: '#1f2937',
          text: '#f3f4f6'
        }
      }
    },
  },
  plugins: [],
}
