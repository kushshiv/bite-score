/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        trust: {
          50: '#f0fdf4',
          100: '#dcfce7',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        surface: {
          DEFAULT: 'var(--surface)',
          raised: 'var(--surface-raised)',
          hover: 'var(--surface-hover)',
          border: 'var(--surface-border)',
        },
        discover: {
          fg: 'var(--discover-fg)',
          muted: 'var(--discover-fg-muted)',
          secondary: 'var(--discover-fg-secondary)',
          subtle: 'var(--discover-fg-subtle)',
        },
        slate: {
          850: '#1a2332',
        },
        caution: {
          500: '#f59e0b',
          100: '#fef3c7',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
