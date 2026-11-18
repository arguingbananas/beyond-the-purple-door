import js from '@eslint/js';
import globals from 'globals';

export default [
  { ignores: ['node_modules/', 'a2ts-web/', 'apps/'] },
  js.configs.recommended,
  { languageOptions: { ecmaVersion: 2024, sourceType: 'module', globals: { ...globals.node } } },
];
