/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.{html,js}',
    './static/js/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary': 'var(--primary)',
        'background': 'var(--background)',
        'accent': 'var(--accent)',
      },
    },
  },
  plugins: [],
}