import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    coverage: {
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'dist/',
        '**/*.config.js',
        '**/mockServiceWorker.js'
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})