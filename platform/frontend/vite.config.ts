import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        port: 3000,
        proxy: {
            // Proxy /api requests to backend in development
            // The /api prefix is forwarded as-is to the backend
            // Example: /api/recommend -> http://localhost:8000/api/recommend
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                // No rewrite - forward /api prefix to backend
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: true,
    },
})

