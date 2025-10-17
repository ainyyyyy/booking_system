import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: ['babel-plugin-react-compiler'],
      },
    }),
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost', changeOrigin: true },
      '/admin':  { target: 'http://localhost', changeOrigin: true },
      '/static': { target: 'http://localhost', changeOrigin: true },
    },
  },
});

