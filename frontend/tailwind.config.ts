import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#FAFAFA',
        surface: '#FFFFFF',
        sidebar: '#F5F5F5',
        ink: '#171717',
        muted: '#737373',
        line: '#E5E5E5',
        signal: '#2563EB',
        success: '#16A34A',
        amber: '#D97706',
        rose: '#DC2626',
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
