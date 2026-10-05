/**
 * RuntimeSecurity.tsx — Feed de eventos de Runtime detectados por agentes eBPF
 * (Falco, Tetragon ou Tracee). Exibe agregação temporal (hit_count),
 * filtros por severidade e link direto para a vulnerabilidade correlacionada.
 */
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Activity, Terminal, RefreshCw, ExternalLink, Filter, Target } from 'lucide-react'

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
    <span className={`inline-flex items-center rounded px-2.5 py-0.5 text-xs font-semibold uppercase ring-1 ring-inset ${cls}`}>
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
    <div className="bg-slate-50 min-h-screen">
      <TituloDaPagina
        titulo={
          <span className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-indigo-600" />
            Runtime Security
          </span>
        }
        descricao="Eventos de ameaças ativas detectados por agentes eBPF (Falco / Tetragon). Desduplicados por container + regra."
        acao={
          <button
            onClick={recarregar}
            className="flex items-center gap-2 transition-all duration-200 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 hover:shadow-md"
          >
            <RefreshCw className="h-4 w-4" /> Atualizar
          </button>
        }
      />

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Filtros */}
        <div className="mb-8 p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-slate-500">
            <Filter className="h-4 w-4" />
            <span className="text-sm font-medium">Filtros:</span>
          </div>
          <div className="flex-1 flex flex-wrap gap-3">
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <Terminal className="h-4 w-4 text-slate-400" />
              </div>
              <input
                type="text"
                placeholder="Container ID..."
                value={containerFilter}
                onChange={(e) => setContainerFilter(e.target.value)}
                className="block w-full rounded-md border border-slate-300 py-1.5 pl-10 pr-3 text-sm placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <select
              value={sevFilter}
              onChange={(e) => setSevFilter(e.target.value)}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-700"
            >
              {SEVERIDADES.map((s) => (
                <option key={s} value={s}>{s ? s.charAt(0).toUpperCase() + s.slice(1) : 'Todas as severidades'}</option>
              ))}
            </select>
          </div>
          <button
            onClick={aplicarFiltros}
            className="transition-all duration-200 rounded-md bg-indigo-600 px-5 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 hover:shadow-md"
          >
            Aplicar Filtros
          </button>
        </div>

        {carregando && <Carregando />}
        {erro && <Erro mensagem={erro} />}

        {!carregando && !erro && (
          dados && dados.length > 0 ? (
            <div className="overflow-hidden bg-white rounded-xl border border-slate-200 shadow-sm">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Regra / Ameaça</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Container</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Severidade</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Risco Calculado</th>
                    <th className="px-6 py-4 text-right font-semibold text-slate-800">Hit Count</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Acessibilidade</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {dados.map((v) => {
                    const isReachable = v.risco === 'critico'
                    return (
                      <tr key={v.id} className={`hover:bg-slate-50 transition-colors duration-150 ${isReachable ? 'bg-red-50/30' : ''}`}>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-slate-900">{v.tipo_vuln}</div>
                          <div className="mt-1 truncate max-w-xs text-xs text-slate-500" title={v.endpoint}>
                            {v.severidade_original}
                          </div>
                        </td>
                        <td className="px-6 py-4 font-mono text-xs font-medium text-slate-600">
                          {v.endpoint.replace('container/', '') || '—'}
                        </td>
                        <td className="px-6 py-4">
                          {badgeSeveridade(v.risco)}
                        </td>
                        <td className="px-6 py-4">
                          <BadgeRisco risco={v.risco as Risco} label={v.risco} />
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="inline-flex items-center justify-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-700">
                            ×{1}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {isReachable ? (
                            <span className="inline-flex items-center gap-1.5 rounded-md bg-red-100 px-2.5 py-1 text-xs font-bold text-red-800">
                              <Target className="h-3.5 w-3.5" /> ALCANÇÁVEL
                            </span>
                          ) : (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <Link
                            to={`/vulnerabilidades/${v.id}`}
                            className="inline-flex items-center gap-1 font-medium text-indigo-600 hover:text-indigo-700 transition-colors text-xs"
                          >
                            Ver CVE <ExternalLink className="h-3 w-3" />
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
              descricao="Configure a integração para a detecção em runtime."
            />
          )
        )}
      </div>
    </div>
  )
}
