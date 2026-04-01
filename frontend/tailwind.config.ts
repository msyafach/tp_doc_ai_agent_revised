import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  "#f0fdf4",
          100: "#dcfce7",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
        },
        brand: {
          grey:  "#6B6B6B",
          green: "#508C4F",
          blue:  "#0096C6",
          DEFAULT: "#508C4F",
          light: "#6B9B6A",
          dark:  "#3D6B3C",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
