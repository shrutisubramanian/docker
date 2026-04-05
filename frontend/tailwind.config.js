/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0c",
        panel: "#121214",
        neon: "#00ff66",
        cyber: {
          50: "#f0fff4",
          100: "#dcffe9",
          200: "#bcffd5",
          300: "#86ffb4",
          400: "#4bff8c",
          500: "#00ff66",
          600: "#00d952",
          700: "#00aa41",
          800: "#068537",
          900: "#076d2f",
          950: "#003d17",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Inconsolata", "monospace"],
      },
      boxShadow: {
        'neon': '0 0 10px rgba(0, 255, 102, 0.4), 0 0 20px rgba(0, 255, 102, 0.2)',
      }
    },
  },
  plugins: [],
}
