import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: __dirname,
  plugins: [react()],
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
      'react': path.resolve(__dirname, '../frontend/node_modules/react'),
      'react-dom': path.resolve(__dirname, '../frontend/node_modules/react-dom'),
      'lucide-react': path.resolve(__dirname, '../frontend/node_modules/lucide-react'),
      'clsx': path.resolve(__dirname, '../frontend/node_modules/clsx'),
      'tailwind-merge': path.resolve(__dirname, '../frontend/node_modules/tailwind-merge'),
    },
  },
  server: {
    port: 5174,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
