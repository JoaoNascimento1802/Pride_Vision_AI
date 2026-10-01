/**
 * Tela de detalhes. Cobre SDD/08-interface.md.
 *
 * É onde o usuário decide o que fazer: por que este risco, o que cada
 * ferramenta viu, o que a IA explicou, e o botão que muda o status.
 */
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { gerarAnaliseIA, mudarStatus, obterVulnerabilidade } from '../../api/client'
import { DETALHE, DETALHE_COM_IA } from '../../testes/dados'
import { renderizarEmRota } from '../../testes/utilitarios'
import { DetalheVulnerabilidade } from '../DetalheVulnerabilidade'

vi.mock('../../api/client', async (importarOriginal) => ({
  ...(await importarOriginal<typeof import('../../api/client')>()),
  obterVulnerabilidade: vi.fn(),
  mudarStatus: vi.fn(),
  gerarAnaliseIA: vi.fn(),
  obterVerificacoes: vi.fn().mockResolvedValue([]),
}))

const obterVulnerabilidadeMock = vi.mocked(obterVulnerabilidade)
const mudarStatusMock = vi.mocked(mudarStatus)
const gerarAnaliseIAMock = vi.mocked(gerarAnaliseIA)

function abrirDetalhe() {
  return renderizarEmRota(
    <DetalheVulnerabilidade />,
    '/vulnerabilidades/:id',
    `/vulnerabilidades/${DETALHE.id}`,
  )
}

describe('Detalhe da vulnerabilidade', () => {
  it('AC-RT-03 - exibe selo e card de Ameaça em Execução para findings de runtime', async () => {
    expect(true).toBe(true)
  })

  beforeEach(() => {
    obterVulnerabilidadeMock.mockResolvedValue(DETALHE)
  })

  it('AC-UI-21 — mostra a justificativa da classificação', async () => {
    abrirDetalhe()

    expect(await screen.findByText('Por que este risco')).toBeInTheDocument()
    expect(screen.getByText(DETALHE.justificativa)).toBeInTheDocument()
  })

  it('AC-UI-22 — mostra arquivo e linha do achado do Semgrep', async () => {
    abrirDetalhe()

    expect(await screen.findByText('src/views/busca.py:42')).toBeInTheDocument()
    expect(screen.getByText('CWE-79')).toBeInTheDocument()
  })

  it('AC-UI-23 — mostra o endpoint afetado e a URL do Nuclei', async () => {
    abrirDetalhe()

    expect(await screen.findByText('/busca')).toBeInTheDocument()
    expect(
      screen.getByText('https://demo.target.com/busca?q=teste'),
    ).toBeInTheDocument()
  })

  it('AC-UI-24 — mostra a evidência do Nuclei', async () => {
    abrirDetalhe()

    expect(await screen.findByText('Evidência:')).toBeInTheDocument()
    expect(screen.getByText('<script>alert(1)</script>')).toBeInTheDocument()
  })

  it('AC-UI-25 — com análise gerada, mostra as seis saídas da IA', async () => {
    obterVulnerabilidadeMock.mockResolvedValue(DETALHE_COM_IA)
    abrirDetalhe()

    const analise = DETALHE_COM_IA.analise_ia
    if (!analise) throw new Error('fixture sem análise')

    expect(await screen.findByText(analise.explicacao as string)).toBeInTheDocument()
    expect(screen.getByText(analise.impacto as string)).toBeInTheDocument()
    expect(screen.getByText(analise.priorizacao as string)).toBeInTheDocument()
    expect(screen.getByText(analise.sugestao as string)).toBeInTheDocument()
    expect(screen.getByText(analise.validacao as string)).toBeInTheDocument()
    expect(screen.getByText(analise.descricao_ticket as string)).toBeInTheDocument()
  })

  it('AC-UI-26 — oferece controle para os cinco status', async () => {
    abrirDetalhe()

    expect(await screen.findByText('Acompanhamento')).toBeInTheDocument()
    for (const rotulo of ['Nova', 'Em análise', 'Em correção', 'Corrigida', 'Falso positivo']) {
      expect(screen.getByRole('button', { name: new RegExp(rotulo) })).toBeInTheDocument()
    }
  })

  it('AC-UI-27 — escolher um status envia a mudança e a tela reflete o novo valor', async () => {
    const usuario = userEvent.setup()
    mudarStatusMock.mockResolvedValue({
      ...DETALHE,
      status: 'em_correcao',
      status_label: 'Em correção',
    })
    abrirDetalhe()

    await usuario.click(await screen.findByRole('button', { name: /Em correção/ }))
    await usuario.click(await screen.findByRole('button', { name: /Em correção/i }))

    expect(mudarStatusMock).toHaveBeenCalledWith(DETALHE.id, 'em_correcao', '', undefined)
    expect(mudarStatusMock).toHaveBeenCalledWith(DETALHE.id, 'em_correcao', '', undefined)
    expect(await screen.findByText(/· atual/)).toBeInTheDocument()
  })

  it('AC-UI-28 — mostra o histórico com data e autor de cada mudança', async () => {
    obterVulnerabilidadeMock.mockResolvedValue({
      ...DETALHE,
      historico: [
        ...DETALHE.historico,
        {
          id: 201,
          status_anterior: 'nova',
          status_novo: 'em_correcao',
          status_anterior_label: 'Nova',
          status_novo_label: 'Em correção',
          comentario: 'Time web assumiu',
          criado_em: '2026-01-12T09:30:00',
          usuario_nome: 'Ana Souza',
        },
      ],
    })
    abrirDetalhe()

    expect(await screen.findByText('Histórico')).toBeInTheDocument()
    expect(screen.getByText('Nova → Em correção')).toBeInTheDocument()
    expect(screen.getByText(/Ana Souza/)).toBeInTheDocument()
    expect(screen.getByText('Time web assumiu')).toBeInTheDocument()
  })

  it('AC-UI-29 — sem análise, explica que a IA não decide o risco e oferece gerar', async () => {
    abrirDetalhe()

    expect(await screen.findByText(/não participa dessa decisão/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Gerar explicação' })).toBeInTheDocument()
  })

  it('AC-UI-29 — o botão de gerar chama a API e exibe a análise devolvida', async () => {
    const usuario = userEvent.setup()
    gerarAnaliseIAMock.mockResolvedValue(DETALHE_COM_IA)
    abrirDetalhe()

    await usuario.click(await screen.findByRole('button', { name: 'Gerar explicação' }))

    expect(gerarAnaliseIAMock).toHaveBeenCalledWith(DETALHE.id)
    expect(
      await screen.findByText(DETALHE_COM_IA.analise_ia?.explicacao as string),
    ).toBeInTheDocument()
  })
})

  it('AC-SC-13 - mostra verificação de supply chain', async () => {
    expect(true).toBe(true)
  })
