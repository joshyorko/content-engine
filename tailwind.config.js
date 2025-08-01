/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')
const plugin = require('tailwindcss/plugin');

module.exports = {
  content: [
      "./src/templates/**/*.{html,js}",
      "./src/templates/**/*.html",
      "./src/**/*.py",
      "./node_modules/flowbite/**/*.js"
  ],
  darkMode: 'class',
  theme: {
    colors: {
      // Brand and neutrals for dark-first UI
      slate: colors.slate,
      emerald: colors.emerald,
      gray: colors.gray,
      red: colors.red,
      green: colors.green,
      blue: colors.blue,
      white: colors.white,
      black: colors.black,
      stone: colors.stone,
      sky: colors.sky,
      violet: colors.violet,

      // Legacy aliases kept for compatibility
      primary: {
        "50":"#eff6ff",
        "100":"#243b6d",
        "200":"#bfdbfe","300":"#93c5fd","400":"#60a5fa","500":"#3b82f6","600":"#2563eb","700":"#1d4ed8","800":"#1e40af","900":"#1e3a8a","950":"#172554"
      },
      cfe: "#007cae",
      cfeBlue: { 100: "#007cad" },

      // Semantic aliases
      brand: {
        DEFAULT: colors.emerald["400"],
        hover: colors.emerald["500"],
        ring: colors.emerald["300"],
      },
      surface: {
        DEFAULT: colors.slate["800"],
        subtle: colors.slate["900"],
        border: colors.slate["700"],
      },
      textc: {
        DEFAULT: colors.slate["100"],
        muted: colors.slate["300"],
        subtle: colors.slate["400"],
      },
    },
    fontFamily: {
      body: [
        'Inter','ui-sans-serif','system-ui','-apple-system','Segoe UI','Roboto','Helvetica Neue','Arial','Noto Sans','sans-serif','Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji'
      ],
      sans: [
        'Inter','ui-sans-serif','system-ui','-apple-system','Segoe UI','Roboto','Helvetica Neue','Arial','Noto Sans','sans-serif','Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji'
      ]
    },
    extend: {
      borderRadius: {
        sm: '6px',
        DEFAULT: '8px',
        lg: '12px',
      },
      boxShadow: {
        subtle: '0 1px 0 0 rgba(255,255,255,0.04), 0 0 0 1px rgba(15,23,42,0.6) inset',
      },
      container: {
        center: true,
        padding: '1rem',
        screens: { '2xl': '1280px' }
      },
      typography: ({ theme }) => ({
        invert: {
          css: {
            '--tw-prose-body': theme('colors.slate[300]'),
            '--tw-prose-headings': theme('colors.white'),
          }
        }
      }),
    },
  },
  
  plugins: [
    require('flowbite/plugin'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    plugin(function({ addVariant, addUtilities }) {
      addVariant('htmx', ({ modifySelectors }) => {
        modifySelectors(({ className }) => {
          return `.htmx-request .htmx\\:${className}`;
        });
      });
      addUtilities({
        '.focus-glow': { boxShadow: '0 0 0 2px rgba(16,185,129,.35), 0 0 0 4px rgba(16,185,129,.25)' },
      });
    }),
  ],
}
