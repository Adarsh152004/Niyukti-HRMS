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
      'react-router-dom': path.resolve(__dirname, '../frontend/node_modules/react-router-dom'),
      'lucide-react': path.resolve(__dirname, '../frontend/node_modules/lucide-react'),
      'clsx': path.resolve(__dirname, '../frontend/node_modules/clsx'),
      'tailwind-merge': path.resolve(__dirname, '../frontend/node_modules/tailwind-merge'),
      'class-variance-authority': path.resolve(__dirname, '../frontend/node_modules/class-variance-authority'),
      'framer-motion': path.resolve(__dirname, '../frontend/node_modules/framer-motion'),
      'date-fns': path.resolve(__dirname, '../frontend/node_modules/date-fns'),
    },
  },
  server: {
    port: 5175,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
