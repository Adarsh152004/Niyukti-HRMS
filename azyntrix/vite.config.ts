// Native esbuild JSX transform (zero Babel dependencies, ultra-fast and resilient)
export default {
  esbuild: {
    jsx: 'automatic',
  },
  server: {
    port: 5180,
    host: true,
  },
};
