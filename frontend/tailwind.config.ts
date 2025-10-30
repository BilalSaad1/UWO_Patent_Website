import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        
        uwo: {
          purple: "#4F2683",     
          purpleLight: "#6b42a1", 
          lilac: "#F4EEFF",       
          gray: "#6B7280",
        },
      },
      boxShadow: {
        card: "0 6px 18px rgba(0,0,0,0.08)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.5)",
      },
      borderRadius: {
        pill: "9999px",
      },
    },
  },
  plugins: [],
};
export default config;