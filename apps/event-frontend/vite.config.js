import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const eventApiTarget = env.VITE_EVENT_API_TARGET || 'http://localhost:8081'

  return {
    plugins: [react()],
    base: command === 'build' ? env.VITE_BASE_PATH || '/events/' : '/',
    build: {
      outDir: 'dist',
      sourcemap: env.VITE_ENABLE_SOURCE_MAPS === 'true',
      chunkSizeWarningLimit: 1000
    },
    server: {
      host: env.VITE_DEV_SERVER_HOST || '0.0.0.0',
      port: Number.parseInt(env.VITE_DEV_SERVER_PORT || '5174', 10),
      proxy: {
        '/api/events': {
          target: eventApiTarget,
          changeOrigin: true
        }
      }
    },
    test: {
      environment: 'jsdom',
      setupFiles: './src/test/setup.js'
    },
    envPrefix: 'VITE_'
  }
})
