/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#A67C00",
          50: "#fef9e7",
          100: "#fdf0c7",
          200: "#fbdf8d",
          300: "#f8c953",
          400: "#f5b11d",
          500: "#A67C00",
          600: "#8f6800",
          700: "#775400",
          800: "#5f4200",
          900: "#473000",
          950: "#2f1e00",
        },
        "primary-dark": "#805d00",
        success: "#059669",
        dark: "#181d24",
        "dark-light": "#1f252d",
        "dark-lighter": "#2a3038",
        orange: {
          DEFAULT: "#A67C00",
          50: "#fef9e7",
          100: "#fdf0c7",
          200: "#fbdf8d",
          300: "#f8c953",
          400: "#f5b11d",
          500: "#A67C00",
          600: "#8f6800",
          700: "#775400",
          800: "#5f4200",
          900: "#473000",
          950: "#2f1e00",
        },
      },
      fontFamily: {
        lato: ["Lato", "sans-serif"],
        inter: ["Inter", "sans-serif"],
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        "spin-slow": "spin 3s linear infinite",
        "bounce-slow": "bounce 2s infinite",
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          "0%": { transform: "translateY(100%)" },
          "100%": { transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(0)" },
        },
      },
      boxShadow: {
        glow: "0 0 20px rgba(166, 124, 0, 0.3)",
        "glow-lg": "0 0 30px rgba(166, 124, 0, 0.4)",
        modern: "0 4px 20px rgba(0, 0, 0, 0.08)",
        "modern-lg": "0 8px 30px rgba(0, 0, 0, 0.12)",
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
  ],
};
