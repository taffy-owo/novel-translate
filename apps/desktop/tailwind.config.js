/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          900: "#171717",
          700: "#3f3f46",
          500: "#71717a"
        }
      }
    }
  },
  plugins: []
};
