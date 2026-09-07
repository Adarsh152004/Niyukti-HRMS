import { build } from './node_modules/vite/dist/node/index.js';
import react from './node_modules/@vitejs/plugin-react/dist/index.js';
import tailwindcss from './node_modules/tailwindcss/lib/index.js';
import autoprefixer from './node_modules/autoprefixer/lib/autoprefixer.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const appDir = path.resolve(__dirname, '../ceo_mobile_chat_app');

async function runBuild() {
  await build({
    root: appDir,
    configFile: false,
    plugins: [react()],
    css: {
      postcss: {
        plugins: [
          tailwindcss({
            content: [
              path.resolve(appDir, './index.html'),
              path.resolve(appDir, './src/**/*.{js,ts,jsx,tsx}'),
            ],
          }),
          autoprefixer(),
        ],
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(appDir, './src'),
        'react': path.resolve(__dirname, './node_modules/react'),
        'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
        'lucide-react': path.resolve(__dirname, './node_modules/lucide-react'),
        'clsx': path.resolve(__dirname, './node_modules/clsx'),
        'tailwind-merge': path.resolve(__dirname, './node_modules/tailwind-merge'),
        'framer-motion': path.resolve(__dirname, './node_modules/framer-motion'),
        'recharts': path.resolve(__dirname, './node_modules/recharts'),
      },
    },
    build: {
      outDir: path.resolve(appDir, 'dist'),
      emptyOutDir: true,
    }
  });
  console.log('BUILD COMPLETE');
}

runBuild().catch(console.error);
