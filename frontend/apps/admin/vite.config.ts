import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  optimizeDeps: {
    include: [
      '@hospitality-platform/design-system',
      '@hospitality-platform/types',
      '@hospitality-platform/api-client',
      '@hospitality-platform/utils',
    ],
  },
  server: {
    port: 3002,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});

