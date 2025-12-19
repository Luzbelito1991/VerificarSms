/** @type {import('tailwindcss').Config} */
// Declara el tipo para que los editores con TypeScript entiendan que esto es una config de Tailwind

module.exports = {
  // 🧭 Archivos donde Tailwind escanea clases usadas
  content: [
    "./templates/**/*.html",      // Archivos Jinja (plantillas HTML de FastAPI)
    "./static/**/*.html",         // HTML estático adicional
    "./static/js/**/*.js",        // JS con clases dinámicas (ej: .classList.add(...))
    "./static/css/**/*.css"       // Estilos personalizados para que no se purguen
  ],

  theme: {
    // 🎨 Extendemos el sistema visual con nuevos estilos
    extend: {
      // 🎬 Animaciones personalizadas
      keyframes: {
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(20px)" },  // Inicio invisible desde abajo
          to: { opacity: "1", transform: "translateY(0)" }        // Final visible en posición
        },
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },   // Entrada rápida
          "100%": { opacity: "1", transform: "translateY(0)" }
        }
      },

      // 🔁 Atajos para usar las animaciones arriba como clases utilitarias
      animation: {
        fadeInUp: "fadeInUp 0.6s ease-out both",   // Entrada más lenta y suave
        fadeIn: "fadeIn 0.3s ease-out forwards"    // Más rápida, útil para elementos UI secundarios
      },

      // 🧱 Paleta de colores personalizada usada en tus layouts, paneles y botones
      colors: {
        emerald: {
          600: "#059669",   // Verde principal (botones, foco, llamadas a la acción)
          500: "#047857"    // Verde medio, complementario
        },
        red: {
          600: "#dc2626",   // Rojo intenso (cancelar, errores)
          500: "#b91c1c"
        },
        blue: {
          600: "#2563eb",   // Azul sistema (accesos administrativos, links)
          500: "#1d4ed8"
        },
        gray: {
          700: "#374151",   // Gris oscuro (fondos, contenedores, bordes)
          600: "#4b5563"
        }
      }
    }
  },

  // 🚫 Clases protegidas: no deben eliminarse en el purge (aunque no estén explícitas en HTML)
  safelist: [
    // 🎯 Clases personalizadas que usás en botones o acciones del sistema
    "btn-yellow",         // Botón alternativo (amarillo)
    "btn",                // Botón base
    "btn-interactivo",    // Hover y foco animado

    // 🎬 Animaciones
    "animate-fadeInUp",
    "animate-fadeIn",

    // 🕒 Delays opcionales
    "delay-0",
    "delay-100",
    "delay-200",

    // 📐 Transformaciones visuales
    "scale-95",
    "scale-100",
    "opacity-0",
    "opacity-100",

    // 🧪 Clases de debug visual
    "debug-box",

    // ⚙️ Transiciones globales para hover, focus, etc.
    "transition-all",
    "duration-200"
  ],

  plugins: [] // Si querés agregar plugins de Tailwind como forms, typography, line-clamp, etc.
}
