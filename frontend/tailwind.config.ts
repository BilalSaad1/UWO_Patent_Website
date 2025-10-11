import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/pages/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: { western: { purple: "#4F2683" } },
      fontFamily: {
        sans: [
          "Helvetica Neue","Helvetica","Arial","ui-sans-serif","system-ui",
          "Segoe UI","Roboto","Noto Sans","Liberation Sans",
          "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol",
        ],
      },
      borderRadius: { xl: "0.75rem" },
    },
  },
  plugins: [],
} satisfies Config;