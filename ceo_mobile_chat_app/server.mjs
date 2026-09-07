import { createServer } from '../frontend/node_modules/vite/dist/node/index.js';
import react from '../frontend/node_modules/@vitejs/plugin-react/dist/index.js';
import tailwindcss from '../frontend/node_modules/tailwindcss/lib/index.js';
import autoprefixer from '../frontend/node_modules/autoprefixer/lib/autoprefixer.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const server = await createServer({
    root: __dirname,
    configFile: false,
    plugins: [react()],
    css: {
      postcss: {
        plugins: [
          tailwindcss({
            content: [
              './index.html',
              './src/**/*.{js,ts,jsx,tsx}',
            ],
          }),
          autoprefixer(),
        ],
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'react': path.resolve(__dirname, '../frontend/node_modules/react'),
        'react-dom': path.resolve(__dirname, '../frontend/node_modules/react-dom'),
        'react-refresh': path.resolve(__dirname, '../frontend/node_modules/react-refresh'),
        'lucide-react': path.resolve(__dirname, '../frontend/node_modules/lucide-react'),
        'clsx': path.resolve(__dirname, '../frontend/node_modules/clsx'),
        'tailwind-merge': path.resolve(__dirname, '../frontend/node_modules/tailwind-merge'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5174,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  });

  await server.listen();
  server.printUrls();
}

startServer();
