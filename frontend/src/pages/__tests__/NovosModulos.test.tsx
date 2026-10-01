import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { RuntimeSecurity } from '../RuntimeSecurity'
import { CloudCspm } from '../CloudCspm'
import { TenantAdmin } from '../TenantAdmin'
import { AuthContext } from '../../auth/AuthContext'

// Mock todas as funções de API
vi.mock('../../api/client', () => ({
  listarVulnerabilidades: vi.fn(),
  listarTenants: vi.fn(),
  listarUsuariosTenant: vi.fn(),
  mensagemDeErro: (e: unknown) => String(e),
}))

import { listarVulnerabilidades, listarTenants } from '../../api/client'

const ADMIN_AUTH = {
  usuario: {
    id: 1,
    nome: 'Admin',
    role: 'admin',
    email: 'admin@t.com',
    criado_em: '2023-01-01',
    permissions: ['audit:read', 'user:manage'],
    tenants: [{ id: 1, name: 'Default' }],
  },
  carregando: false,
  entrar: vi.fn(),
  sair: vi.fn(),
  tenantId: '1',
  setTenantId: vi.fn(),
}

function renderComAuth(elemento: React.ReactElement, auth = ADMIN_AUTH) {
  return render(
    <MemoryRouter>
      <AuthContext.Provider value={auth as any}>
        {elemento}
      </AuthContext.Provider>
    </MemoryRouter>
  )
}

// ---------------------------------------------------------------------------
// Runtime Security
// ---------------------------------------------------------------------------
describe('RuntimeSecurity', () => {
  it('AC-UI-RT-01 — exibe mensagem vazia quando não há eventos de runtime', async () => {
    vi.mocked(listarVulnerabilidades).mockResolvedValue([])

    renderComAuth(<RuntimeSecurity />)

    await waitFor(() => {
      expect(screen.getByText(/Runtime Security/i)).toBeInTheDocument()
      expect(screen.getByText(/Nenhum evento de Runtime detectado/i)).toBeInTheDocument()
    })
  })

  it('AC-UI-RT-02 — renderiza linha da tabela para evento crítico com badge REACHABLE', async () => {
    vi.mocked(listarVulnerabilidades).mockResolvedValue([
      {
        id: 10,
        tipo_vuln: 'Runtime: Terminal shell in container',
        severidade_original: 'bash -i executado como root',
        endpoint: 'container/8a9b2c3d4e5f',
        risco: 'critico' as any,
        status: 'nova' as any,
        status_label: 'Nova',
        aplicacao_id: 1,
      } as any,
    ])

    renderComAuth(<RuntimeSecurity />)

    await waitFor(() => {
      expect(screen.getByText('Runtime: Terminal shell in container')).toBeInTheDocument()
      expect(screen.getByText('🎯 REACHABLE')).toBeInTheDocument()
    })
  })
})

// ---------------------------------------------------------------------------
// Cloud CSPM
// ---------------------------------------------------------------------------
describe('CloudCspm', () => {
  it('AC-UI-CSPM-01 — exibe mensagem vazia quando não há findings cloud', async () => {
    vi.mocked(listarVulnerabilidades).mockResolvedValue([])

    renderComAuth(<CloudCspm />)

    await waitFor(() => {
      expect(screen.getAllByText(/Cloud CSPM/i).length).toBeGreaterThan(0)
      expect(screen.getByText('Nenhum finding de Cloud CSPM encontrado')).toBeInTheDocument()
    })
  })

  it('AC-UI-CSPM-02 — exibe card TOXIC COMBINATION para finding crítico', async () => {
    vi.mocked(listarVulnerabilidades).mockResolvedValue([
      {
        id: 20,
        tipo_vuln: 'Security Group allows unrestricted access',
        severidade_original: 'SG aberto para 0.0.0.0/0:443',
        endpoint: 'arn:aws:ec2:us-east-1::security-group/sg-0a1b2c3d',
        risco: 'critico' as any,
        status: 'nova' as any,
        status_label: 'Nova',
        aplicacao_id: 1,
      } as any,
    ])

    renderComAuth(<CloudCspm />)

    await waitFor(() => {
      expect(screen.getByText(/TOXIC COMBINATION/i)).toBeInTheDocument()
      expect(screen.getByText('Security Group allows unrestricted access')).toBeInTheDocument()
    })
  })
})

// ---------------------------------------------------------------------------
// Tenant Admin
// ---------------------------------------------------------------------------
describe('TenantAdmin', () => {
  it('AC-UI-MT-ADMIN-01 — bloqueia acesso para usuário não-admin', async () => {
    const devAuth = {
      ...ADMIN_AUTH,
      usuario: { ...ADMIN_AUTH.usuario, role: 'developer', permissions: ['finding:read'] },
    }

    renderComAuth(<TenantAdmin />, devAuth as any)

    expect(screen.getByText(/Acesso restrito a Administradores/i)).toBeInTheDocument()
  })

  it('AC-UI-MT-ADMIN-02 — exibe lista de tenants para admin', async () => {
    vi.mocked(listarTenants).mockResolvedValue([
      { id: 1, name: 'Default Organization', domain: null, sso_config: null },
      { id: 3, name: 'FinTech Corp', domain: 'fintechcorp.com.br', sso_config: { issuer: 'https://login.microsoftonline.com/abc' } },
    ])

    renderComAuth(<TenantAdmin />)

    await waitFor(() => {
      expect(screen.getByText('Default Organization')).toBeInTheDocument()
      expect(screen.getByText('FinTech Corp')).toBeInTheDocument()
      expect(screen.getByText('✓ SSO Configurado')).toBeInTheDocument()
    })
  })
})

