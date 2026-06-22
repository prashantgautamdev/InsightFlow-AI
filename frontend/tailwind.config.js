/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0A0A0F",
        surface: "#13131A",
        "surface-glass": "rgba(255,255,255,0.04)",
        border: "rgba(255,255,255,0.08)",
        primary: {
          DEFAULT: "#7C3AED",
          light: "#A78BFA",
          dark: "#5B21B6",
        },
        accent: {
          cyan: "#22D3EE",
          pink: "#F472B6",
          green: "#34D399",
        },
        muted: "#94A3B8",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(circle at top, var(--tw-gradient-stops))",
        "gradient-hero": "linear-gradient(135deg, #7C3AED 0%, #22D3EE 100%)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      backdropBlur: { xs: "2px" },
    },
  },
  plugins: [],
};
