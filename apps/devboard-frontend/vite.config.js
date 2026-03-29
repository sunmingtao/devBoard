import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load environment variables based on mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd(), '')
  
  // Determine if we're in production mode
  const isProduction = mode === 'production'
  
  return {
    plugins: [vue()],
    
    // Environment-specific build configuration
    build: {
      // Enable source maps conditionally
      sourcemap: env.VITE_ENABLE_SOURCE_MAPS === 'true' || !isProduction,
      // Enable minification for production
      minify: isProduction ? 'esbuild' : false,
      // Output directory
      outDir: 'dist',
      // Asset size warning limit
      chunkSizeWarningLimit: 1000,
      // Rollup options for optimization
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router'],
            utils: ['axios']
          }
        }
      }
    },
    
    // Development server configuration
    server: {
      host: env.VITE_DEV_SERVER_HOST || '0.0.0.0',
      port: parseInt(env.VITE_DEV_SERVER_PORT) || 5173,
      hmr: {
        port: parseInt(env.VITE_DEV_SERVER_PORT) || 5173
      }
    },
    
    // Define global constants
    define: {
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION),
      __APP_ENVIRONMENT__: JSON.stringify(env.VITE_APP_ENVIRONMENT)
    },
    
    // Environment variables prefix
    envPrefix: 'VITE_'
  }
})
