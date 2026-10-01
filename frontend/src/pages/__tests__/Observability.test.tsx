import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Observability } from '../Observability'
import { http } from '../../api/client'
import { AuthContext } from '../../auth/AuthContext'

vi.mock('../../api/client', () => ({
  http: {
    get: vi.fn()
  }
}))

describe('Observability', () => {
  it('AC-OBS-05 — mostra as métricas e o health', async () => {
    vi.mocked(http.get).mockImplementation(async (url) => {
      if (url === '/api/health') {
        return { data: { status: 'ok', database: 'up', services: { jira: 'up', genai: 'up' } } }
      }
      if (url === '/metrics') {
        return { data: `http_requests_total{method="GET",route="/api/saude",status_code="200"} 42\ndb_active_connections 5` }
      }
      return { data: {} }
    })

    const mockAuth = {
      usuario: { id: 1, nome: 'Admin', role: 'admin', email: 'admin@t.com', criado_em: '2023-01-01', permissions: ['audit:read'] },
      carregando: false,
      entrar: vi.fn(),
      sair: vi.fn(),
    }

    render(
      <MemoryRouter>
        <AuthContext.Provider value={mockAuth as any}>
          <Observability />
        </AuthContext.Provider>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('System Health (Observability)')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument() // 42 reqs
      expect(screen.getByText('5')).toBeInTheDocument()  // 5 db connections
    })
  })
})
