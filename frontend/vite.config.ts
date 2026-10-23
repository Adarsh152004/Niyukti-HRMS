import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
      'lucide-react': path.resolve(__dirname, './node_modules/lucide-react'),
      'framer-motion': path.resolve(__dirname, './node_modules/framer-motion'),
      'recharts': path.resolve(__dirname, './node_modules/recharts'),
      'clsx': path.resolve(__dirname, './node_modules/clsx'),
      'tailwind-merge': path.resolve(__dirname, './node_modules/tailwind-merge'),
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
    },
  },
  server: {
    port: 5185,
    host: true,
    fs: {
      strict: false,
      allow: ['..', 'E:/', 'F:/', 'C:/'],
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
