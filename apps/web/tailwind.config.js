/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#080907",
          subtle: "#0D0F0B",
        },
        surface: {
          1: "#11130F",
          2: "#171914",
          raised: "#1D2019",
          hover: "#22261E",
        },
        hairline: {
          DEFAULT: "#22261E",
          strong: "#2D3227",
          subtle: "#191B15",
        },
        lime: {
          DEFAULT: "#D7F52F",
          bright: "#E2FA4D",
          dim: "#A4BF1F",
          glow: "rgba(215, 245, 47, 0.15)",
          muted: "rgba(215, 245, 47, 0.08)",
        },
        content: {
          primary: "#F2F3EC",
          secondary: "#A0A397",
          muted: "#717568",
          subtle: "#4B4F43",
        },
        semantic: {
          red: "#EF4444",
          amber: "#F59E0B",
          green: "#10B981",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          '"Geist"',
          '"Inter"',
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          '"SF Mono"',
          '"JetBrains Mono"',
          '"Fira Code"',
          "Consolas",
          "monospace",
        ],
      },
      boxShadow: {
        "lime-glow": "0 0 24px -4px rgba(215, 245, 47, 0.25)",
        "lime-sm": "0 0 12px -2px rgba(215, 245, 47, 0.35)",
        card: "0 4px 20px -2px rgba(0, 0, 0, 0.5)",
      },
      borderRadius: {
        "2xl": "18px",
        "3xl": "24px",
      },
    },
  },
  plugins: [],
};
