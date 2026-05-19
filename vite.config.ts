import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    headers: {
      'X-Frame-Options': 'ALLOWALL'
    },
    proxy: {
      // 后端路由本身带 /api 前缀的：直接转发
      '/api/v2': {
        target: 'http://localhost:9001',
        changeOrigin: true
      },
      '/api/issues': {
        target: 'http://localhost:9001',
        changeOrigin: true
      },
      '/api/checklists': {
        target: 'http://localhost:9001',
        changeOrigin: true
      },
      '/api/flowticket': {
        target: 'http://localhost:9001',
        changeOrigin: true
      },
      // 后端路由不带 /api 前缀的：去掉 /api 前缀
      '/api/profiles': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/plans': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/dict': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/tasks': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/api/health': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
