import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => ({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': process.env.VITE_API_URL || 'http://localhost:8000',
    },
  },
}))
