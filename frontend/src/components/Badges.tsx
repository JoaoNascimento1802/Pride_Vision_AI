// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Badges.tsx — Etiquetas de risco, status e origem.
 *
 * O nível de risco é a informação mais consultada da interface, então ganha
 * cor própria e peso visual. Status e origem são secundários e ficam neutros,
 * para não competirem pela atenção.
 */
import type { Risco, StatusVulnerabilidade } from '../api/types'
import { CheckCheck } from 'lucide-react'

const ESTILO_RISCO: Record<Risco, string> = {
  critico: 'bg-rose-100 text-rose-800 ring-rose-200',
  alto: 'bg-orange-100 text-orange-800 ring-orange-200',
  medio: 'bg-amber-100 text-amber-800 ring-amber-200',
  baixo: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
}

export function BadgeRisco({ risco, label }: { risco: Risco; label: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ring-1 ring-inset ${ESTILO_RISCO[risco]}`}
    >
      {label}
    </span>
  )
}

const ESTILO_STATUS: Record<StatusVulnerabilidade, string> = {
  nova: 'bg-slate-100 text-slate-700 ring-slate-200',
  em_analise: 'bg-sky-100 text-sky-800 ring-sky-200',
  em_correcao: 'bg-indigo-100 text-indigo-800 ring-indigo-200',
  aguardando_validacao: 'bg-amber-100 text-amber-800 ring-amber-200',
  corrigida: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  falso_positivo: 'bg-slate-100 text-slate-600 ring-slate-200',
  aceito_como_risco: 'bg-orange-100 text-orange-800 ring-orange-200',
  excecao_temporaria: 'bg-fuchsia-100 text-fuchsia-800 ring-fuchsia-200',
  duplicado: 'bg-slate-100 text-slate-600 ring-slate-200',
}

export function BadgeStatus({
  status,
  label,
}: {
  status: StatusVulnerabilidade
  label: string
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${ESTILO_STATUS[status]}`}
    >
      {label}
    </span>
  )
}

export function BadgeFerramenta({ nome }: { nome: string }) {
  const ehSemgrep = nome.toLowerCase() === 'semgrep'
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
        ehSemgrep
          ? 'bg-violet-100 text-violet-800 ring-violet-200'
          : 'bg-indigo-100 text-indigo-800 ring-indigo-200'
      }`}
    >
      {nome}
    </span>
  )
}

/**
 * Marca visual de confirmação cruzada.
 *
 * Quando as duas ferramentas apontam o mesmo problema, a certeza é muito maior
 * — merece destaque próprio na listagem.
 */
export function SeloCorrelacionada() {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-semibold text-rose-800 ring-1 ring-inset ring-rose-200"
      title="Encontrada pelo Semgrep e confirmada pelo Nuclei"
    >
      <CheckCheck className="h-3.5 w-3.5" />
      correlacionada
    </span>
  )
}

export function EtiquetaAmbiente({ label }: { label: string }) {
  const producao = label.toLowerCase().startsWith('produ')
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
        producao
          ? 'bg-rose-100 text-rose-800 ring-rose-200'
          : 'bg-slate-100 text-slate-700 ring-slate-200'
      }`}
    >
      {label}
    </span>
  )
}

export function TipoVulnerabilidade({ tipo }: { tipo: string }) {
  return <span className="text-xs font-semibold uppercase tracking-wide text-slate-700">{tipo.replace(/_/g, ' ')}</span>
}
