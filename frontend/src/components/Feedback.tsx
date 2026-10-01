/**
 * Feedback.tsx — Estados de carregamento, erro e lista vazia.
 *
 * Padronizados aqui para que toda tela trate os três casos do mesmo jeito. Uma
 * tela que só desenha o caminho feliz deixa o usuário sem saber se está
 * carregando, se deu erro, ou se realmente não há nada.
 */
import type { ReactNode } from 'react'

export function Carregando({ texto = 'Carregando…' }: { texto?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-slate-500">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-600" />
      {texto}
    </div>
  )
}

export function Erro({ mensagem, aoTentar }: { mensagem: string; aoTentar?: () => void }) {
  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
      <p className="font-medium">Não foi possível carregar</p>
      <p className="mt-1">{mensagem}</p>
      {aoTentar && (
        <button
          type="button"
          onClick={aoTentar}
          className="mt-3 rounded-md bg-rose-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-rose-700"
        >
          Tentar de novo
        </button>
      )}
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
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
      <p className="font-medium text-slate-700">{titulo}</p>
      <p className="mx-auto mt-1 max-w-md text-sm text-slate-500">{descricao}</p>
      {acao && <div className="mt-4">{acao}</div>}
    </div>
  )
}

export function Aviso({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
      {children}
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
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      {(titulo || acao) && (
        <header className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          {titulo && <h2 className="text-sm font-semibold text-slate-700">{titulo}</h2>}
          {acao}
        </header>
      )}
      <div className="p-5">{children}</div>
    </section>
  )
}
