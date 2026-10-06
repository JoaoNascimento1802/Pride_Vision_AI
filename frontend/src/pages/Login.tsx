// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Login.tsx — Entrada e primeiro cadastro.
 *
 * As duas ações ficam na mesma tela porque o sistema começa sem nenhum
 * usuário: obrigar a descobrir uma tela separada de cadastro travaria o
 * primeiro acesso.
 */
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Mail, User, Lock, ArrowRight, ShieldCheck,} from 'lucide-react'

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
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600 shadow-lg mb-6">
            <ShieldCheck className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            PRIDE <span className="text-indigo-600">Vision AI</span>
          </h1>
          <p className="mt-3 text-sm text-slate-500 max-w-sm mx-auto">
            Centraliza, correlaciona e prioriza as vulnerabilidades das suas aplicações.
          </p>
        </div>

        <div className="bg-white py-8 px-6 shadow-sm rounded-xl border border-slate-200 sm:px-10">
          <form onSubmit={aoEnviar} className="space-y-6">
            <Campo
              rotulo="E-mail"
              tipo="email"
              valor={email}
              aoMudar={setEmail}
              autoComplete="email"
              icone={<Mail className="h-5 w-5 text-slate-400" />}
            />

            {cadastrando && (
              <Campo 
                rotulo="Nome do Usuário" 
                tipo="text" 
                valor={nome} 
                aoMudar={setNome} 
                autoComplete="name"
                icone={<User className="h-5 w-5 text-slate-400" />}
              />
            )}

            <Campo
              rotulo="Senha"
              tipo="password"
              valor={senha}
              aoMudar={setSenha}
              autoComplete={cadastrando ? 'new-password' : 'current-password'}
              dica={cadastrando ? 'Mínimo de 8 caracteres.' : undefined}
              icone={<Lock className="h-5 w-5 text-slate-400" />}
            />

            {erro && (
              <div className="rounded-md bg-red-50 p-4 border border-red-200">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <ShieldCheck className="h-5 w-5 text-red-400" aria-hidden="true" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">{erro}</h3>
                  </div>
                </div>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={enviando}
                className="flex w-full justify-center items-center gap-2 rounded-md bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-60 transition-all duration-200"
              >
                {enviando ? 'Aguarde…' : cadastrando ? 'Criar conta e entrar' : 'Entrar'}
                {!enviando && <ArrowRight className="h-4 w-4" />}
              </button>
            </div>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-slate-600">
              {cadastrando ? 'Já possui conta?' : 'Primeiro acesso?'}{' '}
              <button
                type="button"
                onClick={() => {
                  setModo(cadastrando ? 'entrar' : 'cadastrar')
                  setErro(null)
                }}
                className="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors"
              >
                {cadastrando ? 'Entrar agora' : 'Criar uma conta'}
              </button>
            </p>
          </div>
        </div>
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
  icone,
}: {
  rotulo: string
  tipo: string
  valor: string
  aoMudar: (valor: string) => void
  autoComplete?: string
  dica?: string
  icone: React.ReactNode
}) {
  return (
    <div>
      <label className="block text-sm font-medium leading-6 text-slate-900">
        {rotulo}
      </label>
      <div className="relative mt-2 rounded-md shadow-sm">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          {icone}
        </div>
        <input
          type={tipo}
          value={valor}
          required
          autoComplete={autoComplete}
          onChange={(evento) => aoMudar(evento.target.value)}
          className="block w-full rounded-md border-0 py-2.5 pl-10 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 transition-all duration-200 outline-none"
        />
      </div>
      {dica && <p className="mt-2 text-xs text-slate-500">{dica}</p>}
    </div>
  )
}
