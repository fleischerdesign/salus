import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  test: {
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    globals: true,
    pool: 'forks',
  },
});
