import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  resolve: {
    conditions: ['module', 'browser', 'development|production', 'svelte'],
  },
  test: {
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    globals: true,
    pool: 'forks',
    environmentMatchGlobs: [['tests/component/**', 'jsdom']],
  },
});
