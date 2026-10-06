// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
// `defineConfig` vem de `vitest/config`, não de `vite`: é a versão que conhece o
// bloco `test`. Com a de `vite`, o `tsc -b` do build reprova a configuração.
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      // Durante o desenvolvimento o navegador chama /api no próprio Vite, que
      // repassa ao backend. Assim o frontend usa caminhos relativos e o mesmo
      // código serve em produção, onde a URL da API vem de VITE_API_URL.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/metrics': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    // jsdom porque os ACs de tela falam do que o usuário vê; sem DOM não há o
    // que asserir. Ver frontend/CLAUDE.md.
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.ts',
    include: ['src/**/*.test.{ts,tsx}'],
    css: false,
  },
})

