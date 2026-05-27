module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        linen: "var(--linen)",
        "mandys-pink": "var(--mandys-pink)",
        "lesbian-green": "var(--lesbian-green)",
        golden: "var(--golden-orange)",
        tundora: "var(--tundora)",
        "old-rose": "var(--old-rose)",
        canvas: "var(--canvas)",
        surface: "var(--surface)",
        rose: "var(--rose)",
        "rose-soft": "var(--rose-soft)",
        "lavender-soft": "var(--lavender-soft)",
        "text-strong": "var(--text-strong)",
        "text-muted": "var(--text-muted)",
        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
        border: "var(--border-soft)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        serene: "0 18px 40px -28px rgba(76, 68, 68, 0.45)",
      },
      fontFamily: {
        sans: ["Montserrat", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["'Cormorant Garamond'", "Georgia", "serif"],
        serif: ["Cardo", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
