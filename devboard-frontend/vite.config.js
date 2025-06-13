import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  // Enable source maps for debugging (even in production builds)
  build: {
    sourcemap: true,  // This generates .map files for debugging
    minify: false,    // Disable minification for easier debugging (optional)
  },
  
  // Development server configuration
  server: {
    host: '0.0.0.0',  // Allow external connections (needed for Docker)
    port: 5173,
    hmr: {
      port: 5173      // Hot module replacement port
    }
  }
})
