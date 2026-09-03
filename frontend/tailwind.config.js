/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        palette: {
          deep: '#064789',
          steel: '#427AA1',
          ice: '#EBF2FA',
          forest: '#679436',
          lime: '#A5BE00',
        },
        background: 'var(--bg)',
        accent: 'var(--accent)',
        'text-primary': 'var(--text-h)',
        'text-secondary': 'var(--text)',
      },
      fontFamily: {
        sans: ['Manrope', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
