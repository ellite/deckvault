/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./src/**/*.{astro,html,js,ts}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#5375fc",
          dark: "#405fd6",
          light: "#6d9cff",
        },
        surface: {
          DEFAULT: "#ffffff",
          dark: "#0f1f38",
        },
        bg: {
          DEFAULT: "#f0f9f8",
          dark: "#0a1628",
        },
        border: {
          DEFAULT: "#d0e9e6",
          dark: "#1e3a5f",
        },
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
      },
    },
  },
};
