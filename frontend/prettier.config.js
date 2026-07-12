export default {
  tailwindStylesheet: './src/app.css',
  tabWidth: 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "none",
  "printWidth": 100,
  "plugins": ["prettier-plugin-svelte", "prettier-plugin-tailwindcss"],
  "overrides": [
    { "files": "*.svelte", "options": { "parser": "svelte" } }
  ]
}
