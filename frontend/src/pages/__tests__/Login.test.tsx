/**
 * Tela de login. Cobre SDD/08-interface.md.
 *
 * "Login simples" do PDF §10. Simples não quer dizer sem tratamento de erro: a
 * mensagem que a API devolve precisa chegar ao usuário.
 */
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { entrar, lerToken, usuarioAtual } from '../../api/client'
import { AuthProvider } from '../../auth/AuthContext'
import { USUARIO } from '../../testes/dados'
import { renderizar } from '../../testes/utilitarios'
import { Login } from '../Login'

vi.mock('../../api/client', async (importarOriginal) => ({
  ...(await importarOriginal<typeof import('../../api/client')>()),
  entrar: vi.fn(),
  registrar: vi.fn(),
  usuarioAtual: vi.fn(),
}))

const entrarMock = vi.mocked(entrar)

function abrirLogin() {
  return renderizar(
    <AuthProvider>
      <Login />
    </AuthProvider>,
  )
}

describe('Login', () => {
  beforeEach(() => {
    vi.mocked(usuarioAtual).mockResolvedValue(USUARIO)
  })

  it('AC-UI-30 — oferece e-mail, senha e o botão de entrar', () => {
    abrirLogin()

    expect(screen.getByLabelText('E-mail')).toBeInTheDocument()
    expect(screen.getByLabelText('Senha')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('AC-UI-31 — credenciais válidas guardam o token e abrem a sessão', async () => {
    const usuario = userEvent.setup()
    entrarMock.mockResolvedValue({
      access_token: 'token-de-teste',
      token_type: 'bearer',
      usuario: USUARIO,
    })
    abrirLogin()

    await usuario.type(screen.getByLabelText('E-mail'), 'ana@exemplo.com')
    await usuario.type(screen.getByLabelText('Senha'), 'senha-de-teste-123')
    await usuario.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(entrarMock).toHaveBeenCalledWith('ana@exemplo.com', 'senha-de-teste-123')
    expect(lerToken()).toBe('token-de-teste')
  })

  it('AC-UI-32 — credenciais inválidas exibem a mensagem da API e mantêm a tela', async () => {
    const usuario = userEvent.setup()
    entrarMock.mockRejectedValue(new Error('E-mail ou senha incorretos.'))
    abrirLogin()

    await usuario.type(screen.getByLabelText('E-mail'), 'ana@exemplo.com')
    await usuario.type(screen.getByLabelText('Senha'), 'errada')
    await usuario.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('E-mail ou senha incorretos.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument()
    expect(lerToken()).toBeNull()
  })
})
