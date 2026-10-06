// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Tela de aplicações. Cobre SDD/08-interface.md.
 *
 * O inventário e o envio dos relatórios ficam na mesma tela porque são um fluxo
 * só: cadastrar sem enviar relatório não produz nada.
 */
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  criarAplicacao,
  enviarRelatorio,
  listarAplicacoes,
  listarUploads,
  obterOpcoes,
} from '../../api/client'
import { APLICACAO, OPCOES, UPLOADS } from '../../testes/dados'
import { renderizar } from '../../testes/utilitarios'
import { Aplicacoes } from '../Aplicacoes'

vi.mock('../../api/client', async (importarOriginal) => ({
  ...(await importarOriginal<typeof import('../../api/client')>()),
  listarAplicacoes: vi.fn(),
  listarUploads: vi.fn(),
  obterOpcoes: vi.fn(),
  criarAplicacao: vi.fn(),
  enviarRelatorio: vi.fn(),
}))

const listarAplicacoesMock = vi.mocked(listarAplicacoes)
const listarUploadsMock = vi.mocked(listarUploads)
const obterOpcoesMock = vi.mocked(obterOpcoes)
const criarAplicacaoMock = vi.mocked(criarAplicacao)
const enviarRelatorioMock = vi.mocked(enviarRelatorio)

describe('Tela de aplicações', () => {
  beforeEach(() => {
    listarAplicacoesMock.mockResolvedValue([APLICACAO])
    listarUploadsMock.mockResolvedValue(UPLOADS)
    obterOpcoesMock.mockResolvedValue(OPCOES)
  })

  it('AC-UI-07 — lista cada aplicação com nome, ambiente, exposição e importância', async () => {
    renderizar(<Aplicacoes />)

    expect(await screen.findByText('Portal do Cliente')).toBeInTheDocument()
    expect(screen.getByText('Produção')).toBeInTheDocument()
    expect(screen.getByText(/Internet/)).toBeInTheDocument()
    expect(screen.getByText(/importância alta/)).toBeInTheDocument()
  })

  it('AC-UI-08 — mostra a quantidade de vulnerabilidades de cada aplicação', async () => {
    renderizar(<Aplicacoes />)

    const total = await screen.findByText('Total')
    expect(total.parentElement).toHaveTextContent('12')

    const criticas = screen.getByText('Críticas')
    expect(criticas.parentElement).toHaveTextContent('4')
  })

  it('AC-UI-09 — o formulário oferece os seis campos do PDF §4.1', async () => {
    const usuario = userEvent.setup()
    renderizar(<Aplicacoes />)

    await usuario.click(await screen.findByRole('button', { name: 'Nova aplicação' }))

    const formulario = await screen.findByRole('heading', { name: 'Nova aplicação' })
    const cartao = formulario.closest('section')
    if (!cartao) throw new Error('formulário fora de um cartão')

    const dentro = within(cartao)
    expect(dentro.getByLabelText('Nome')).toBeInTheDocument()
    expect(dentro.getByLabelText('Responsável')).toBeInTheDocument()
    expect(dentro.getByLabelText('Ambiente')).toBeInTheDocument()
    expect(dentro.getByLabelText('Exposição')).toBeInTheDocument()
    expect(dentro.getByLabelText('Importância para o negócio')).toBeInTheDocument()
    expect(dentro.getByLabelText('URL (opcional)')).toBeInTheDocument()
  })

  it('AC-UI-10 — enviar o formulário cadastra a aplicação e recarrega a lista', async () => {
    const usuario = userEvent.setup()
    criarAplicacaoMock.mockResolvedValue(APLICACAO)
    renderizar(<Aplicacoes />)

    await usuario.click(await screen.findByRole('button', { name: 'Nova aplicação' }))
    await usuario.type(await screen.findByLabelText('Nome'), 'Sistema de Pedidos')
    await usuario.type(screen.getByLabelText('Responsável'), 'Time Backend')
    await usuario.selectOptions(screen.getByLabelText('Ambiente'), 'homologacao')
    await usuario.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(criarAplicacaoMock).toHaveBeenCalledWith(
      expect.objectContaining({
        nome: 'Sistema de Pedidos',
        responsavel: 'Time Backend',
        ambiente: 'homologacao',
      }),
    )
    // Duas chamadas: a carga inicial e a recarga após o cadastro
    expect(listarAplicacoesMock.mock.calls.length).toBeGreaterThan(1)
  })

  it('AC-UI-11 — permite enviar o relatório do Semgrep e o do Nuclei', async () => {
    const usuario = userEvent.setup()
    enviarRelatorioMock.mockResolvedValue({
      upload_id: 1,
      ferramenta: 'semgrep',
      ferramenta_label: 'Semgrep',
      achados_lidos: 2,
      achados_ignorados: 0,
      avisos: [],
      vulnerabilidades_totais: 2,
      vulnerabilidades_novas: 2,
      vulnerabilidades_atualizadas: 0,
    })
    renderizar(<Aplicacoes />)

    expect(
      await screen.findByText('Enviar relatório do Semgrep'),
    ).toBeInTheDocument()
    expect(screen.getByText('Enviar relatório do Nuclei')).toBeInTheDocument()

    const rotulo = screen.getByText('Enviar relatório do Semgrep')
    const campo = rotulo.querySelector('input[type="file"]')
    if (!campo) throw new Error('botão de upload sem campo de arquivo')

    await usuario.upload(
      campo as HTMLInputElement,
      new File(['{"results": []}'], 'semgrep.json', { type: 'application/json' }),
    )

    expect(enviarRelatorioMock).toHaveBeenCalledWith(
      APLICACAO.id,
      'semgrep',
      expect.any(File),
    )
    expect(await screen.findByText(/2 achado\(s\) lido\(s\)/)).toBeInTheDocument()
  })

  it('AC-UI-11 — mostra qual relatório está em vigor para cada ferramenta', async () => {
    renderizar(<Aplicacoes />)

    expect(await screen.findByText(/semgrep\.json · 2 achado\(s\)/)).toBeInTheDocument()
  })
})
