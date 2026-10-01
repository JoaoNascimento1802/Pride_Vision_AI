/**
 * Login.tsx — Entrada e primeiro cadastro.
 *
 * As duas ações ficam na mesma tela porque o sistema começa sem nenhum
 * usuário: obrigar a descobrir uma tela separada de cadastro travaria o
 * primeiro acesso.
 */
import { useState } from 'react'
import type { FormEvent } from 'react'

import { mensagemDeErro, registrar } from '../api/client'
import { useAuth } from '../auth/useAuth'

export function Login() {
  const { entrar } = useAuth()
  const [modo, setModo] = useState<'entrar' | 'cadastrar'>('entrar')
  const [email, setEmail] = useState('')
  const [nome, setNome] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  const cadastrando = modo === 'cadastrar'

  async function aoEnviar(evento: FormEvent) {
    evento.preventDefault()
    setErro(null)
    setEnviando(true)

    try {
      if (cadastrando) {
        await registrar(email, nome, senha)
      }
      await entrar(email, senha)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível entrar.'))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            PRIDE <span className="text-violet-600">Vision AI</span>
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Centraliza, correlaciona e prioriza as vulnerabilidades das suas aplicações.
          </p>
        </div>

        <form
          onSubmit={aoEnviar}
          className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
        >
          <Campo
            rotulo="E-mail"
            tipo="email"
            valor={email}
            aoMudar={setEmail}
            autoComplete="email"
          />

          {cadastrando && (
            <Campo rotulo="Nome" tipo="text" valor={nome} aoMudar={setNome} autoComplete="name" />
          )}

          <Campo
            rotulo="Senha"
            tipo="password"
            valor={senha}
            aoMudar={setSenha}
            autoComplete={cadastrando ? 'new-password' : 'current-password'}
            dica={cadastrando ? 'Mínimo de 8 caracteres.' : undefined}
          />

          {erro && (
            <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{erro}</p>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="w-full rounded-md bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700 disabled:opacity-60"
          >
            {enviando ? 'Aguarde…' : cadastrando ? 'Criar conta e entrar' : 'Entrar'}
          </button>

          <p className="text-center text-sm text-slate-500">
            {cadastrando ? 'Já tem conta?' : 'Primeiro acesso?'}{' '}
            <button
              type="button"
              onClick={() => {
                setModo(cadastrando ? 'entrar' : 'cadastrar')
                setErro(null)
              }}
              className="font-medium text-violet-600 hover:underline"
            >
              {cadastrando ? 'Entrar' : 'Criar uma conta'}
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}

function Campo({
  rotulo,
  tipo,
  valor,
  aoMudar,
  autoComplete,
  dica,
}: {
  rotulo: string
  tipo: string
  valor: string
  aoMudar: (valor: string) => void
  autoComplete?: string
  dica?: string
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{rotulo}</span>
      <input
        type={tipo}
        value={valor}
        required
        autoComplete={autoComplete}
        onChange={(evento) => aoMudar(evento.target.value)}
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
      />
      {dica && <span className="mt-1 block text-xs text-slate-400">{dica}</span>}
    </label>
  )
}
