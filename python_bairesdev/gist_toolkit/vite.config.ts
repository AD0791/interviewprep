import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true, // Listens on all IP interfaces (crucial for Docker port mapping)
    strictPort: true,
    proxy: {
      // Proxies all '/api/v1' HTTP calls to backend server
      // Why: Bypasses browser CORS options/preflight checks during dev cycles
      '/api/v1': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxies WebSocket connections
      '/ws': {
        target: 'ws://backend:8000',
        ws: true,
      },
    },
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        // Code Splitting: Splits node_modules into distinct cache chunks
        // Why: Boosts page speed index since browser cache retains static vendors across updates
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'vendor-core-react';
            if (id.includes('redux') || id.includes('@reduxjs')) return 'vendor-state-redux';
            if (id.includes('chakra-ui') || id.includes('@emotion')) return 'vendor-ui-chakra';
            return 'vendor-helpers';
          }
        },
      },
    },
  },
});
