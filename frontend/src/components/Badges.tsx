/**
 * Badges.tsx — Etiquetas de risco, status e origem.
 *
 * O nível de risco é a informação mais consultada da interface, então ganha
 * cor própria e peso visual. Status e origem são secundários e ficam neutros,
 * para não competirem pela atenção.
 */
import type { Risco, StatusVulnerabilidade } from '../api/types'

const ESTILO_RISCO: Record<Risco, string> = {
  critico: 'bg-critico-fundo text-critico ring-critico/30',
  alto: 'bg-alto-fundo text-alto ring-alto/30',
  medio: 'bg-medio-fundo text-medio ring-medio/30',
  baixo: 'bg-baixo-fundo text-baixo ring-baixo/30',
}

export function BadgeRisco({ risco, label }: { risco: Risco; label: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ring-1 ring-inset ${ESTILO_RISCO[risco]}`}
    >
      {label}
    </span>
  )
}

const ESTILO_STATUS: Record<StatusVulnerabilidade, string> = {
  nova: 'bg-slate-100 text-slate-700 ring-slate-300',
  em_analise: 'bg-sky-50 text-sky-700 ring-sky-300',
  em_correcao: 'bg-indigo-50 text-indigo-700 ring-indigo-300',
  aguardando_validacao: 'bg-amber-50 text-amber-700 ring-amber-300',
  corrigida: 'bg-emerald-50 text-emerald-700 ring-emerald-300',
  falso_positivo: 'bg-slate-100 text-slate-500 ring-slate-300',
  aceito_como_risco: 'bg-orange-50 text-orange-700 ring-orange-300',
  excecao_temporaria: 'bg-fuchsia-50 text-fuchsia-700 ring-fuchsia-300',
  duplicado: 'bg-slate-100 text-slate-500 ring-slate-300',
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
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${ESTILO_STATUS[status]}`}
    >
      {label}
    </span>
  )
}

export function BadgeFerramenta({ nome }: { nome: string }) {
  const ehSemgrep = nome.toLowerCase() === 'semgrep'
  return (
    <span
      className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
        ehSemgrep
          ? 'bg-violet-50 text-violet-700 ring-violet-200'
          : 'bg-amber-50 text-amber-700 ring-amber-200'
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
      className="inline-flex items-center gap-1 rounded bg-critico-fundo px-1.5 py-0.5 text-xs font-medium text-critico ring-1 ring-inset ring-critico/20"
      title="Encontrada pelo Semgrep e confirmada pelo Nuclei"
    >
      ✓✓ correlacionada
    </span>
  )
}

export function EtiquetaAmbiente({ label }: { label: string }) {
  const producao = label.toLowerCase().startsWith('produ')
  return (
    <span
      className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
        producao
          ? 'bg-rose-50 text-rose-700 ring-rose-200'
          : 'bg-slate-100 text-slate-600 ring-slate-200'
      }`}
    >
      {label}
    </span>
  )
}

export function TipoVulnerabilidade({ tipo }: { tipo: string }) {
  return <span className="font-medium uppercase">{tipo.replace(/_/g, ' ')}</span>
}
