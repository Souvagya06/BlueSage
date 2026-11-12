/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        water: {
          50:  '#eff8ff',
          100: '#dbeffe',
          200: '#bfe3fe',
          300: '#93d1fd',
          400: '#60b6fa',
          500: '#3b97f6',
          600: '#2578eb',
          700: '#1d62d8',
          800: '#1e50af',
          900: '#1e448a',
          950: '#172b55',
        }
      }
    }
  },
  plugins: [],
}

