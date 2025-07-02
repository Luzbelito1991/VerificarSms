/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./static/**/*.html",
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      keyframes: {
        'fade-in-up': {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.6s ease-out both',
        'fade-in': 'fade-in 0.3s ease-out forwards'
      }
    }
  },
  safelist: [
    'animate-fade-in-up',
    'animate-fade-in',
    'delay-0',
    'delay-100',
    'delay-200'
  ],
  plugins: []
};
// This configuration file sets up Tailwind CSS with custom animations and safelists for specific classes.
// It includes content paths for HTML and JavaScript files, extends the theme with fade-in animations