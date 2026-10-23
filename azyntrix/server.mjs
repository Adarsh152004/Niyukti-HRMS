import { createServer } from '../frontend/node_modules/vite/dist/node/index.js';
import react from '../frontend/node_modules/@vitejs/plugin-react/dist/index.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  process.chdir(__dirname);

  const server = await createServer({
    root: __dirname,
    configFile: false,
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'react': path.resolve(__dirname, '../frontend/node_modules/react'),
        'react/jsx-runtime': path.resolve(__dirname, '../frontend/node_modules/react/jsx-runtime.js'),
        'react/jsx-dev-runtime': path.resolve(__dirname, '../frontend/node_modules/react/jsx-dev-runtime.js'),
        'react-dom/client': path.resolve(__dirname, '../frontend/node_modules/react-dom/client.js'),
        'react-dom': path.resolve(__dirname, '../frontend/node_modules/react-dom'),
        'react-refresh': path.resolve(__dirname, '../frontend/node_modules/react-refresh'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5180,
      proxy: {
        '/api': {
          target: 'http://localhost:5050',
          changeOrigin: true,
        },
      },
    },
  });

  await server.listen();
  server.printUrls();
}

startServer();
