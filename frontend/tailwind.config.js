/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'leaf-green': {
          400: '#9bd66a',
          500: '#7fbf45',
          600: '#659d34',
        },
        primary: {
          50: '#f1f9eb',
          100: '#dcefcf',
          400: '#9bd66a',
          500: '#7fbf45',
          600: '#659d34',
          700: '#4d7d27',
        },
        dark: {
          50: '#f9fafb',
          900: '#111827',
          950: '#030712',
        },
      },
      animation: {
        'pulse-soft': 'pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      fontSize: {
        'base': ['16px', '24px'],
        'lg': ['18px', '28px'],
        'xl': ['20px', '28px'],
      },
    },
  },
  plugins: [],
}

