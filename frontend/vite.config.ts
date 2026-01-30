import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        // Proxy /api requests to backend in development
        // In production, VITE_API_URL is used instead (set in .env.production)
        '/api': {
          target: env.VITE_DEV_BACKEND_URL || 'http://127.0.0.1:8001',
          changeOrigin: true,
        },
      },
    },
    // Ensure environment variables are available
    define: {
      // Expose build time for debugging
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
  }
})
