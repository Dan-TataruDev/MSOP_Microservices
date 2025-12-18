import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'Hospitality Platform',
        short_name: 'Hospitality',
        description: 'Smart Hospitality & Retail Platform',
        theme_color: '#2563eb',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      // Resolve workspace packages to their source files
      '@hospitality-platform/types': path.resolve(__dirname, '../../packages/types/src/index.ts'),
      '@hospitality-platform/utils': path.resolve(__dirname, '../../packages/utils/src/index.ts'),
      '@hospitality-platform/api-client': path.resolve(__dirname, '../../packages/api-client/src/index.ts'),
      '@hospitality-platform/design-system': path.resolve(__dirname, '../../packages/design-system/src/index.ts'),
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
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});

