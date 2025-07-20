/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",      // Templates Jinja (FastAPI)
    "./static/**/*.html",         // HTML estático si tenés
    "./static/js/**/*.js",        // JS con clases dinámicas
    "./static/css/**/*.css"       // Opcional, si querés purgar también estilos custom
  ],
  theme: {
    extend: {
      keyframes: {
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        }
      },
      animation: {
        fadeInUp: "fadeInUp 0.6s ease-out both",
        fadeIn: "fadeIn 0.3s ease-out forwards",
      },
      colors: {
        emerald: {
          600: "#059669",
          500: "#047857",
        },
        red: {
          600: "#dc2626",
          500: "#b91c1c",
        },
        blue: {
          600: "#2563eb",
          500: "#1d4ed8",
        },
        gray: {
          700: "#374151",
          600: "#4b5563",
        }
        
      }
    }
  },
  safelist: [
    "btn-yellow",
    "btn", // también la base si querés evitar su purge
    "btn-interactivo",
    "animate-fadeInUp",
    "animate-fadeIn",
    "delay-0",
    "delay-100",
    "delay-200",
    "scale-95",
    "scale-100",
    "opacity-0",
    "opacity-100",
    "debug-box",
    "transition-all",
    "duration-200"
  ],
  plugins: []
};




