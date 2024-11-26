// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/events': {
        target: 'http://webhook:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
