// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { AuthContext } from '../auth/AuthContext'

describe('Multi-Tenancy e SSO', () => {
  it('AC-MT-03 — Dado um usuário com múltiplas associações na tabela TenantUser, exibe seletor', async () => {
    const mockUsuario = {
      id: 1,
      email: 'joao@corporate.com',
      nome: 'João',
      role: 'DEVELOPER',
      criado_em: '2023-01-01T00:00:00Z',
      permissions: ['audit:read'],
      tenants: [
        { id: 1, name: 'Default Organization' },
        { id: 2, name: 'Corporate Org' }
      ]
    }
    
    render(
      <MemoryRouter>
        <AuthContext.Provider value={{
          usuario: mockUsuario as any,
          carregando: false,
          entrar: vi.fn(),
          sair: vi.fn(),
          tenantId: '1',
          setTenantId: vi.fn()
        }}>
          <Layout />
        </AuthContext.Provider>
      </MemoryRouter>
    )
    
    // Verifica se o select renderizou
    const select = await screen.findByRole('combobox')
    expect(select).toBeInTheDocument()
    
    // Verifica se as opções estão lá
    expect(screen.getByText('Default Organization')).toBeInTheDocument()
    expect(screen.getByText('Corporate Org')).toBeInTheDocument()
  })
})
