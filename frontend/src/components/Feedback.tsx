// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Feedback.tsx — Estados de carregamento, erro e lista vazia.
 *
 * Padronizados aqui para que toda tela trate os três casos do mesmo jeito. Uma
 * tela que só desenha o caminho feliz deixa o usuário sem saber se está
 * carregando, se deu erro, ou se realmente não há nada.
 */
import type { ReactNode } from 'react'
import { Loader2, AlertCircle, FileSearch, Info } from 'lucide-react'

export function Carregando({ texto = 'Carregando…' }: { texto?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-slate-500">
      <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      <span className="text-sm font-medium">{texto}</span>
    </div>
  )
}

export function Erro({ mensagem, aoTentar }: { mensagem: string; aoTentar?: () => void }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 shadow-sm">
      <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-rose-600" />
      <div>
        <p className="font-semibold text-rose-900">Não foi possível carregar</p>
        <p className="mt-1">{mensagem}</p>
        {aoTentar && (
          <button
            type="button"
            onClick={aoTentar}
            className="mt-3 rounded-md bg-rose-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition-all duration-200 hover:bg-rose-700 hover:shadow-md"
          >
            Tentar de novo
          </button>
        )}
      </div>
    </div>
  )
}

export function Vazio({
  titulo,
  descricao,
  acao,
}: {
  titulo: string
  descricao: string
  acao?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 p-12 text-center">
      <FileSearch className="mb-4 h-12 w-12 text-slate-400" />
      <p className="font-semibold text-slate-800">{titulo}</p>
      <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">{descricao}</p>
      {acao && <div className="mt-6">{acao}</div>}
    </div>
  )
}

export function Aviso({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-indigo-200 bg-indigo-50 p-4 text-sm text-indigo-900 shadow-sm">
      <Info className="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" />
      <div>{children}</div>
    </div>
  )
}

export function Cartao({
  titulo,
  children,
  acao,
}: {
  titulo?: string
  children: ReactNode
  acao?: ReactNode
}) {
  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      {(titulo || acao) && (
        <header className="flex items-center justify-between border-b border-slate-200 bg-slate-50/50 px-6 py-4">
          {titulo && <h2 className="text-base font-semibold text-slate-800">{titulo}</h2>}
          {acao && <div>{acao}</div>}
        </header>
      )}
      <div className="p-6">{children}</div>
    </section>
  )
}
