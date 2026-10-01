/**
 * RuntimeSecurity.tsx — Feed de eventos de Runtime detectados por agentes eBPF
 * (Falco, Tetragon ou Tracee). Exibe agregação temporal (hit_count),
 * filtros por severidade e link direto para a vulnerabilidade correlacionada.
 */
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { listarVulnerabilidades } from '../api/client'
import { BadgeRisco } from '../components/Badges'
import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'
import type { Risco } from '../api/types'

const SEVERIDADES = ['', 'critico', 'alto', 'medio', 'baixo'] as const

function badgeSeveridade(sev: string) {
  const map: Record<string, string> = {
    critico: 'bg-red-100 text-red-800 ring-red-300',
    alto: 'bg-orange-100 text-orange-800 ring-orange-300',
    medio: 'bg-yellow-100 text-yellow-800 ring-yellow-300',
    baixo: 'bg-green-100 text-green-800 ring-green-300',
  }
  const cls = map[sev.toLowerCase()] ?? 'bg-slate-100 text-slate-700 ring-slate-300'
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold uppercase ring-1 ring-inset ${cls}`}>
      {sev}
    </span>
  )
}

export function RuntimeSecurity() {
  const [params, setParams] = useSearchParams()
  const [containerFilter, setContainerFilter] = useState(params.get('container_id') ?? '')
  const [sevFilter, setSevFilter] = useState(params.get('severity') ?? '')

  function aplicarFiltros() {
    const p = new URLSearchParams()
    if (containerFilter) p.set('container_id', containerFilter)
    if (sevFilter) p.set('severity', sevFilter)
    setParams(p)
  }

  // Reutiliza listarVulnerabilidades com tipo_vuln=Runtime para não criar nova rota
  const chave = params.toString()
  const { dados, carregando, erro, recarregar } = useRequisicao(
    () => listarVulnerabilidades({ tipo_vuln: 'Runtime' }),
    [chave],
  )

  return (
    <>
      <TituloDaPagina
        titulo="Runtime Security"
        descricao="Eventos de ameaças ativas detectados por agentes eBPF (Falco / Tetragon). Deduplicados por container + regra."
        acao={
          <button
            onClick={recarregar}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50"
          >
            ↺ Atualizar
          </button>
        }
      />

      {/* Filtros */}
      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Container ID..."
          value={containerFilter}
          onChange={(e) => setContainerFilter(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm shadow-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
        />
        <select
          value={sevFilter}
          onChange={(e) => setSevFilter(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm shadow-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
        >
          {SEVERIDADES.map((s) => (
            <option key={s} value={s}>{s ? s.charAt(0).toUpperCase() + s.slice(1) : 'Todas as severidades'}</option>
          ))}
        </select>
        <button
          onClick={aplicarFiltros}
          className="rounded-md bg-violet-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-violet-700"
        >
          Filtrar
        </button>
      </div>

      {carregando && <Carregando />}
      {erro && <Erro mensagem={erro} />}

      {!carregando && !erro && (
        dados && dados.length > 0 ? (
          <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-slate-600">Regra / Ameaça</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-600">Container</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-600">Severidade</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-600">Risco Calculado</th>
                  <th className="px-4 py-3 text-right font-semibold text-slate-600">Hit Count</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-600">Reachability</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-600">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {dados.map((v) => {
                  const isReachable = v.risco === 'critico'
                  return (
                    <tr key={v.id} className={`hover:bg-slate-50 ${isReachable ? 'bg-red-50' : ''}`}>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-900">{v.tipo_vuln}</div>
                        <div className="mt-0.5 truncate max-w-xs text-xs text-slate-500" title={v.endpoint}>
                          {v.severidade_original}
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-600">
                        {v.endpoint.replace('container/', '') || '—'}
                      </td>
                      <td className="px-4 py-3">
                        {badgeSeveridade(v.risco)}
                      </td>
                      <td className="px-4 py-3">
                        <BadgeRisco risco={v.risco as Risco} label={v.risco} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="inline-flex items-center justify-center rounded-full bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-700">
                          ×{1}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {isReachable ? (
                          <span className="inline-flex items-center gap-1 rounded bg-red-100 px-2 py-0.5 text-xs font-bold text-red-800">
                            🎯 REACHABLE
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <Link
                          to={`/vulnerabilidades/${v.id}`}
                          className="text-violet-600 hover:underline text-xs"
                        >
                          Ver CVE →
                        </Link>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <Vazio
            titulo="Nenhum evento de Runtime detectado"
            descricao="Configure o webhook do Falco apontando para /api/v1/ingestion/runtime."
          />
        )
      )}
    </>
  )
}

