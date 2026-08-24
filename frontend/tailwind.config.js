/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0a0e14",
        surface: "#121821",
        "surface-alt": "#1a212c",
        edge: "#262f3d",
        cyan: {
          400: "#22d3ee",
          500: "#06b6d4",
        },
        risk: {
          low: "#34d399",
          medium: "#facc15",
          high: "#f59e0b",
          critical: "#f43f5e",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}
