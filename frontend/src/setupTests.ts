/**
 * setupTests.ts — Preparo comum de todo teste de tela.
 *
 * Carregado uma vez por arquivo de teste pelo Vitest (ver `vite.config.ts`).
 */
import '@testing-library/jest-dom/vitest'

import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  // Sem isto o DOM do teste anterior sobrevive e um `getByText` acha o elemento
  // errado — falha que aparece só quando os testes rodam juntos.
  cleanup()
  vi.clearAllMocks()
  localStorage.clear()
})

// O Recharts mede o contêiner para desenhar. No jsdom todo elemento tem tamanho
// zero, então o gráfico não renderiza e o aviso polui a saída. Fixar o tamanho
// resolve os dois de uma vez.
Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
  configurable: true,
  value: 800,
})
Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
  configurable: true,
  value: 600,
})

globalThis.ResizeObserver =
  globalThis.ResizeObserver ??
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
