/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FF9A00',
        'primary-dark': '#e6870a',
        success: '#059669',
        dark: '#181d24',
        'dark-light': '#1f252d',
        'dark-lighter': '#2a3038',
        orange: '#FF9A00'
      },
      fontFamily: {
        'lato': ['Lato', 'sans-serif'],
        'inter': ['Inter', 'sans-serif']
      },
      backdropBlur: {
        'xs': '2px',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'bounce-slow': 'bounce 2s infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(0)' },
        }
      },
      boxShadow: {
        'glow': '0 0 20px rgba(255, 154, 0, 0.3)',
        'glow-lg': '0 0 30px rgba(255, 154, 0, 0.4)',
        'modern': '0 4px 20px rgba(0, 0, 0, 0.08)',
        'modern-lg': '0 8px 30px rgba(0, 0, 0, 0.12)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}