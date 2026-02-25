import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: process.env.HOST || 'localhost',
    port: process.env.PORT || 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://api.own-council.localhost:1355',
        changeOrigin: true,
      }
    }
  }
})
