// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Activity, RefreshCw, Filter, Target, Terminal } from 'lucide-react'

import { listarFindingsRuntime } from '../api/client'
import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'

function badgeSeveridade(sev: string) {
  const map: Record<string, string> = {
    critical: 'bg-red-100 text-red-800 ring-red-300',
    emergency: 'bg-red-100 text-red-800 ring-red-300',
    alert: 'bg-orange-100 text-orange-800 ring-orange-300',
    error: 'bg-orange-100 text-orange-800 ring-orange-300',
    warning: 'bg-yellow-100 text-yellow-800 ring-yellow-300',
    notice: 'bg-blue-100 text-blue-800 ring-blue-300',
    info: 'bg-green-100 text-green-800 ring-green-300',
    debug: 'bg-slate-100 text-slate-800 ring-slate-300',
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
  const [autoRefresh, setAutoRefresh] = useState(true)

  function aplicarFiltros() {
    const p = new URLSearchParams()
    if (containerFilter) p.set('container_id', containerFilter)
    if (sevFilter) p.set('severity', sevFilter)
    setParams(p)
  }

  const p_container_id = params.get('container_id') || undefined
  const p_severity = params.get('severity') || undefined

  const { dados, carregando, erro, recarregar } = useRequisicao(
    () => listarFindingsRuntime({ container_id: p_container_id, severity: p_severity }),
    [params.toString()],
  )

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>
    if (autoRefresh) {
      interval = setInterval(() => {
        recarregar()
      }, 5000) // Poll every 5 seconds
    }
    return () => clearInterval(interval)
  }, [autoRefresh, recarregar])

  return (
    <div className="bg-slate-50 min-h-screen">
      <TituloDaPagina
        titulo={
          <span className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-indigo-600" />
            Runtime Security (Live Feed)
          </span>
        }
        descricao="Eventos de ameaas ativas detectados por agentes eBPF (Falco / Tetragon). Feed em tempo real via polling."
        acao={
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 cursor-pointer">
              <input 
                type="checkbox" 
                checked={autoRefresh} 
                onChange={(e) => setAutoRefresh(e.target.checked)} 
                className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-600"
              />
              Live Auto-Refresh
            </label>
            <button
              onClick={recarregar}
              className="flex items-center gap-2 transition-all duration-200 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 hover:shadow-md"
            >
              <RefreshCw className="h-4 w-4" /> Atualizar
            </button>
          </div>
        }
      />

      <div className="mb-6 rounded-xl bg-white p-4 shadow-sm border border-slate-200">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="mb-1.5 block text-sm font-semibold text-slate-700">ID do Container</label>
            <input
              type="text"
              placeholder="Ex: a1b2c3d4..."
              className="block w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={containerFilter}
              onChange={(e) => setContainerFilter(e.target.value)}
            />
          </div>

          <div className="sm:w-64">
            <label className="mb-1.5 block text-sm font-semibold text-slate-700">Severidade (Falco)</label>
            <select
              className="block w-full rounded-md border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={sevFilter}
              onChange={(e) => setSevFilter(e.target.value)}
            >
              <option value="">Todas</option>
              <option value="critical">Critical</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="notice">Notice</option>
              <option value="info">Info</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={aplicarFiltros}
              className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all duration-200"
            >
              <Filter className="h-4 w-4" />
              Filtrar
            </button>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        {carregando && !dados ? (
          <Carregando />
        ) : erro ? (
          <Erro mensagem={erro} aoTentar={recarregar} />
        ) : (
          dados && dados.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">ltimo Evento</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Regra / Processo</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Container / Syscall</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Severidade</th>
                    <th className="px-6 py-4 text-right font-semibold text-slate-800">Hit Count</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Ao</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {dados.map((f) => {
                    return (
                      <tr key={f.id} className="hover:bg-slate-50 transition-colors duration-150">
                        <td className="px-6 py-4 font-mono text-xs text-slate-600 whitespace-nowrap">
                          {new Date(f.last_seen_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-slate-900">{f.rule_name || 'Desconhecida'}</div>
                          <div className="mt-1 flex items-center gap-1 font-mono text-xs font-medium text-slate-500">
                            <Terminal className="h-3 w-3" /> {f.process_name || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-mono text-xs font-medium text-indigo-600 truncate max-w-[150px]" title={f.container_id || ''}>
                            {f.container_id ? f.container_id.substring(0,12) : 'N/A'}
                          </div>
                          <div className="mt-1 text-xs text-slate-500">
                            Syscall: {f.syscall || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {badgeSeveridade(f.severidade)}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="inline-flex items-center justify-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-700 ring-1 ring-slate-300">
                            x{f.hit_count}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {f.vulnerabilidade_id ? (
                            <Link
                              to={`/vulnerabilidades/${f.vulnerabilidade_id}`}
                              className="inline-flex items-center gap-1.5 rounded-md bg-red-100 px-2.5 py-1 text-xs font-bold text-red-800 hover:bg-red-200 transition-colors"
                            >
                              <Target className="h-3.5 w-3.5" /> Ver Vuln Elevada
                            </Link>
                          ) : (
                            <span className="text-xs text-slate-400 font-medium">Apenas Log</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <Vazio
              titulo="Nenhum evento de Runtime ativo"
              descricao="Sistemas eBPF operando normalmente. Nenhum evento malicioso detectado."
            />
          )
        )}
      </div>
    </div>
  )
}
