/**
 * Tela de vulnerabilidades. Cobre SDD/08-interface.md.
 *
 * O PDF §7 lista sete colunas obrigatórias. Cada uma tem um AC próprio: é a
 * tela central do produto, e "mostra o suficiente" não é critério verificável.
 */
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { listarAplicacoes, listarVulnerabilidades, obterOpcoes } from '../../api/client'
import {
  APLICACAO,
  OPCOES,
  VULNERABILIDADE_CRITICA,
  VULNERABILIDADE_SEM_SEVERIDADE,
} from '../../testes/dados'
import { renderizar } from '../../testes/utilitarios'
import { Vulnerabilidades } from '../Vulnerabilidades'

vi.mock('../../api/client', async (importarOriginal) => ({
  ...(await importarOriginal<typeof import('../../api/client')>()),
  listarVulnerabilidades: vi.fn(),
  listarAplicacoes: vi.fn(),
  obterOpcoes: vi.fn(),
}))

const listarVulnerabilidadesMock = vi.mocked(listarVulnerabilidades)
const listarAplicacoesMock = vi.mocked(listarAplicacoes)
const obterOpcoesMock = vi.mocked(obterOpcoes)

/** Linha da tabela correspondente a uma vulnerabilidade, achada pelo endpoint. */
async function linhaDe(endpoint: string) {
  const celula = await screen.findByText(endpoint)
  const linha = celula.closest('tr')
  if (!linha) throw new Error(`Sem linha para ${endpoint}`)
  return linha
}

describe('Lista de vulnerabilidades', () => {
  beforeEach(() => {
    listarVulnerabilidadesMock.mockResolvedValue([
      VULNERABILIDADE_CRITICA,
      VULNERABILIDADE_SEM_SEVERIDADE,
    ])
    listarAplicacoesMock.mockResolvedValue([APLICACAO])
    obterOpcoesMock.mockResolvedValue(OPCOES)
  })

  it('AC-UI-12 — cada linha mostra o tipo da vulnerabilidade', async () => {
    renderizar(<Vulnerabilidades />)
    expect(await linhaDe('/busca')).toHaveTextContent(/xss/i)
  })

  it('AC-UI-13 — cada linha mostra a aplicação afetada', async () => {
    renderizar(<Vulnerabilidades />)
    expect(await linhaDe('/busca')).toHaveTextContent('Portal do Cliente')
  })

  it('AC-UI-14 — cada linha mostra a origem: Semgrep, Nuclei ou ambas', async () => {
    renderizar(<Vulnerabilidades />)

    const correlacionada = await linhaDe('/busca')
    expect(within(correlacionada).getByText('Semgrep')).toBeInTheDocument()
    expect(within(correlacionada).getByText('Nuclei')).toBeInTheDocument()

    const soSemgrep = await linhaDe('/api/usuarios')
    expect(within(soSemgrep).getByText('Semgrep')).toBeInTheDocument()
    expect(within(soSemgrep).queryByText('Nuclei')).not.toBeInTheDocument()
  })

  it('AC-UI-15 — cada linha mostra a severidade original da ferramenta', async () => {
    renderizar(<Vulnerabilidades />)
    expect(await linhaDe('/busca')).toHaveTextContent('ERROR')
  })

  it('AC-UI-16 — cada linha mostra o risco calculado pelo PRIDE', async () => {
    renderizar(<Vulnerabilidades />)
    expect(await linhaDe('/busca')).toHaveTextContent('Crítico')
    expect(await linhaDe('/api/usuarios')).toHaveTextContent('Alto')
  })

  it('AC-UI-17 — cada linha mostra o status da correção', async () => {
    renderizar(<Vulnerabilidades />)
    expect(await linhaDe('/busca')).toHaveTextContent('Nova')
    expect(await linhaDe('/api/usuarios')).toHaveTextContent('Em correção')
  })

  it('AC-UI-18 — cada linha mostra a data da identificação', async () => {
    renderizar(<Vulnerabilidades />)
    expect(await linhaDe('/busca')).toHaveTextContent(
      new Date(VULNERABILIDADE_CRITICA.identificada_em).toLocaleDateString('pt-BR'),
    )
  })

  it('AC-UI-19 — os filtros de aplicação, risco, status e correlacionadas existem', async () => {
    renderizar(<Vulnerabilidades />)

    expect(await screen.findByLabelText('Aplicação')).toBeInTheDocument()
    expect(screen.getByLabelText('Risco')).toBeInTheDocument()
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    expect(screen.getByLabelText('Somente correlacionadas')).toBeInTheDocument()
  })

  it('AC-UI-19 — escolher um risco refaz a busca com o filtro aplicado', async () => {
    const usuario = userEvent.setup()
    renderizar(<Vulnerabilidades />)

    await usuario.selectOptions(await screen.findByLabelText('Risco'), 'critico')

    expect(listarVulnerabilidadesMock).toHaveBeenLastCalledWith(
      expect.objectContaining({ risco: 'critico' }),
    )
  })

  it('AC-UI-19 — o filtro recebido pela URL já vem aplicado', async () => {
    renderizar(<Vulnerabilidades />, '/vulnerabilidades?status=em_correcao')

    await screen.findByText('/busca')
    expect(listarVulnerabilidadesMock).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'em_correcao' }),
    )
  })

  it('AC-UI-20 — sem resultado, explica o que fazer em vez de mostrar tabela vazia', async () => {
    listarVulnerabilidadesMock.mockResolvedValue([])
    renderizar(<Vulnerabilidades />)

    expect(await screen.findByText('Nenhuma vulnerabilidade encontrada')).toBeInTheDocument()
    expect(screen.getByText(/Envie os relatórios do Semgrep e do Nuclei/)).toBeInTheDocument()
  })

  it('AC-UI-E4 — sem severidade original, a célula mostra um traço', async () => {
    renderizar(<Vulnerabilidades />)

    const linha = await linhaDe('/api/usuarios')
    expect(linha).toHaveTextContent('—')
    expect(linha).not.toHaveTextContent('null')
  })
})
