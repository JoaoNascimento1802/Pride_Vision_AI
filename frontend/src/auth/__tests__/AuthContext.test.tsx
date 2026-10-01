/**
 * Sessão do usuário. Cobre AC-UI-E2 de SDD/08-interface.md.
 *
 * Um token expirado precisa derrubar a sessão em qualquer tela, não só na que
 * fez a chamada — daí o evento no interceptor do axios em vez de tratamento
 * caso a caso.
 */
import { act, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { EVENTO_SESSAO_EXPIRADA, guardarToken, usuarioAtual } from '../../api/client'
import { USUARIO } from '../../testes/dados'
import { AuthProvider } from '../AuthContext'
import { useAuth } from '../useAuth'

vi.mock('../../api/client', async (importarOriginal) => ({
  ...(await importarOriginal<typeof import('../../api/client')>()),
  usuarioAtual: vi.fn(),
}))

const usuarioAtualMock = vi.mocked(usuarioAtual)

function Sonda() {
  const { usuario, carregando } = useAuth()
  if (carregando) return <p>carregando</p>
  return <p>{usuario ? `logado: ${usuario.nome}` : 'sem sessão'}</p>
}

function montar() {
  return render(
    <AuthProvider>
      <Sonda />
    </AuthProvider>,
  )
}

describe('Sessão', () => {
  beforeEach(() => {
    usuarioAtualMock.mockResolvedValue(USUARIO)
  })

  it('AC-UI-E2 — o evento de sessão expirada encerra a sessão em qualquer tela', async () => {
    guardarToken('token-guardado')
    montar()

    expect(await screen.findByText('logado: Ana Souza')).toBeInTheDocument()

    // É o que o interceptor do axios dispara ao receber 401
    act(() => {
      window.dispatchEvent(new Event(EVENTO_SESSAO_EXPIRADA))
    })

    expect(await screen.findByText('sem sessão')).toBeInTheDocument()
  })

  it('AC-UI-E2 — token guardado que a API recusa não vira sessão', async () => {
    guardarToken('token-vencido')
    usuarioAtualMock.mockRejectedValue(new Error('401'))
    montar()

    await waitFor(() => expect(screen.getByText('sem sessão')).toBeInTheDocument())
  })
})
