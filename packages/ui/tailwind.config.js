/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // These would be imported from tokens/index.ts in a real build process
        // For artifact simplicity, defined here
        confidence: {
          low: '#6b7280',    // Gray-500
          medium: '#f97316', // Orange-500
          high: '#3b82f6',   // Blue-500
        }
      }
    },
  },
  plugins: [],
}
