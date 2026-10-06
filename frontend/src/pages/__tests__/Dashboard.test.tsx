// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Tela inicial — Visão geral. Cobre SDD/08-interface.md.
 *
 * O PDF §7 lista cinco coisas que esta tela precisa mostrar. Cada uma virou um
 * AC, e cada AC virou um teste.
 */
import { screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { obterDashboard } from '../../api/client'
import { DASHBOARD, DASHBOARD_VAZIO } from '../../testes/dados'
import { renderizar } from '../../testes/utilitarios'
import { Dashboard } from '../Dashboard'

vi.mock('../../api/client', async (importarOriginal) => ({
  ...(await importarOriginal<typeof import('../../api/client')>()),
  obterDashboard: vi.fn(),
}))

const obterDashboardMock = vi.mocked(obterDashboard)

describe('Visão geral', () => {
  beforeEach(() => {
    obterDashboardMock.mockResolvedValue(DASHBOARD)
  })

  it('AC-UI-01 — mostra o total de aplicações', async () => {
    renderizar(<Dashboard />)
    const indicador = await screen.findByText('Aplicações')
    expect(indicador.parentElement).toHaveTextContent('3')
  })

  it('AC-UI-02 — mostra o total de vulnerabilidades', async () => {
    renderizar(<Dashboard />)
    const indicador = await screen.findByText('Vulnerabilidades', { selector: 'p' })
    expect(indicador.parentElement).toHaveTextContent('17')
  })

  it('AC-UI-03 — mostra a quantidade de vulnerabilidades críticas', async () => {
    renderizar(<Dashboard />)
    // `selector` desempata com a coluna "Críticas" da tabela de aplicações
    const indicador = await screen.findByText('Críticas', { selector: 'p' })
    expect(indicador.parentElement).toHaveTextContent('4')
  })

  it('AC-UI-04 — mostra a quantidade de vulnerabilidades em correção', async () => {
    renderizar(<Dashboard />)
    const indicador = await screen.findByText('Em correção')
    expect(indicador.parentElement).toHaveTextContent('2')
  })

  it('AC-UI-05 — lista as aplicações com maior risco, com ambiente e exposição', async () => {
    renderizar(<Dashboard />)

    expect(await screen.findByText('Aplicações com maior risco')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Portal do Cliente' })).toBeInTheDocument()

    const linha = screen.getByRole('link', { name: 'Portal do Cliente' }).closest('tr')
    expect(linha).toHaveTextContent('Produção')
    expect(linha).toHaveTextContent('Internet')
  })

  it('AC-UI-06 — sem aplicação cadastrada, orienta a cadastrar em vez de mostrar zeros', async () => {
    obterDashboardMock.mockResolvedValue(DASHBOARD_VAZIO)
    renderizar(<Dashboard />)

    expect(await screen.findByText('Nenhuma aplicação cadastrada')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Cadastrar aplicação' })).toBeInTheDocument()
  })

  it('AC-UI-E1 — API fora do ar mostra o erro e oferece tentar de novo', async () => {
    obterDashboardMock.mockRejectedValue(new Error('Network Error'))
    renderizar(<Dashboard />)

    expect(await screen.findByText('Não foi possível carregar')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Tentar de novo' })).toBeInTheDocument()
  })

  it('AC-UI-E3 — enquanto carrega mostra o indicador, não uma tela em branco', () => {
    obterDashboardMock.mockReturnValue(new Promise(() => {}))
    renderizar(<Dashboard />)

    expect(screen.getByText('Carregando…')).toBeInTheDocument()
  })
})
