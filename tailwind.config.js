/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",      // Archivos Jinja (FastAPI)
    "./static/**/*.html",         // Archivos estáticos (si los usás)
    "./static/js/**/*.js"         // JS donde usás clases dinámicas
  ],
  theme: {
    extend: {
      keyframes: {
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      },
      animation: {
        fadeInUp: 'fadeInUp 0.6s ease-out both',
        fadeIn: 'fadeIn 0.3s ease-out forwards'
      }
    }
  },
  safelist: [
    'animate-fadeInUp',
    'animate-fadeIn',
    'delay-0',
    'delay-100',
    'delay-200',
    'scale-95',
    'scale-100',
    'opacity-0',
    'opacity-100',
    'transition-all',
    'duration-200'
  ],
  plugins: []
};
