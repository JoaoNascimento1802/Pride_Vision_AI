// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Cloud, ShieldAlert, AlertTriangle, ExternalLink, RefreshCw, CheckCircle, Server } from 'lucide-react'

import { listarVulnerabilidades } from '../api/client'
import { BadgeRisco } from '../components/Badges'
import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'

function providerIcon(endpoint: string) {
  if (endpoint.includes('arn:aws')) return '?? AWS'
  if (endpoint.includes('projects/')) return '?? GCP'
  if (endpoint.includes('azure')) return '?? Azure'
  return '?? Cloud'
}

export function CloudCspm() {
  const { dados, carregando, erro, recarregar } = useRequisicao(
    () => listarVulnerabilidades({ tipo_vuln: 'Misconfiguration' }),
    [],
  )

  const vulnsCloud = useMemo(() => {
    // If backend doesn't filter perfectly, fallback to filtering by name/endpoint indicating cloud
    if (!dados) return []
    return dados.filter(v => v.tipo_vuln.toLowerCase().includes('misconfig') || v.tipo_vuln.toLowerCase().includes('cloud') || v.endpoint.includes('arn:'))
  }, [dados])

  const stats = useMemo(() => {
    if (!vulnsCloud) return { total: 0, critical: 0, high: 0, complianceScore: 100 }
    const critical = vulnsCloud.filter(v => v.risco === 'critico').length
    const high = vulnsCloud.filter(v => v.risco === 'alto').length
    const score = Math.max(0, 100 - (critical * 10) - (high * 5) - (vulnsCloud.length))
    return { total: vulnsCloud.length, critical, high, complianceScore: score }
  }, [vulnsCloud])

  return (
    <div className="bg-slate-50 min-h-screen">
      <TituloDaPagina
        titulo={
          <span className="flex items-center gap-2">
            <Cloud className="h-6 w-6 text-indigo-600" />
            Cloud Security Posture (CSPM)
          </span>
        }
        descricao="Monitoramento de conformidade e deteco de configuraes inseguras em nuvens pblicas (AWS, GCP, Azure)."
        acao={
          <button
            onClick={recarregar}
            className="flex items-center gap-2 transition-all duration-200 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 hover:shadow-md"
          >
            <RefreshCw className="h-4 w-4" /> Atualizar
          </button>
        }
      />

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-500">Compliance Score</h3>
            <CheckCircle className="h-5 w-5 text-emerald-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-slate-900">{stats.complianceScore}%</p>
          <div className="mt-2 h-2 w-full rounded-full bg-slate-100 overflow-hidden">
             <div className="h-full bg-indigo-500" style={{ width: `${stats.complianceScore}%` }}></div>
          </div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-500">Recursos Inseguros</h3>
            <Server className="h-5 w-5 text-indigo-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-slate-900">{stats.total}</p>
        </div>
        <div className="rounded-xl border border-red-200 bg-red-50/30 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-red-600">Risco Crtico</h3>
            <ShieldAlert className="h-5 w-5 text-red-600" />
          </div>
          <p className="mt-2 text-3xl font-bold text-red-700">{stats.critical}</p>
        </div>
        <div className="rounded-xl border border-orange-200 bg-orange-50/30 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-orange-600">Risco Alto</h3>
            <AlertTriangle className="h-5 w-5 text-orange-600" />
          </div>
          <p className="mt-2 text-3xl font-bold text-orange-700">{stats.high}</p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        {carregando && !dados ? (
          <Carregando />
        ) : erro ? (
          <Erro mensagem={erro} aoTentar={recarregar} />
        ) : vulnsCloud.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 text-left font-semibold text-slate-800">Regra Violada</th>
                  <th className="px-6 py-4 text-left font-semibold text-slate-800">Provedor / Recurso</th>
                  <th className="px-6 py-4 text-left font-semibold text-slate-800">Risco Calculado</th>
                  <th className="px-6 py-4 text-left font-semibold text-slate-800">Identificada Em</th>
                  <th className="px-6 py-4 text-left font-semibold text-slate-800">Ao</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {vulnsCloud.map((v) => {
                  const isToxic = v.risco === 'critico' && v.tipo_vuln.toLowerCase().includes('public')
                  return (
                    <tr key={v.id} className="hover:bg-slate-50 transition-colors duration-150">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-900">{v.tipo_vuln}</div>
                        {isToxic && (
                          <span className="mt-1 inline-flex items-center gap-1 rounded-md bg-red-100 px-2 py-0.5 text-xs font-bold text-red-800 ring-1 ring-red-300">
                            <AlertTriangle className="h-3 w-3" /> TOXIC COMBINATION
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-700 mb-1">{providerIcon(v.endpoint)}</div>
                        <div className="font-mono text-xs text-slate-500 truncate max-w-xs" title={v.endpoint}>{v.endpoint}</div>
                      </td>
                      <td className="px-6 py-4">
                        <BadgeRisco risco={v.risco as any} label={v.risco} />
                      </td>
                      <td className="px-6 py-4 text-slate-500 text-xs">
                        {new Date(v.identificada_em).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4">
                        <Link
                          to={`/vulnerabilidades/${v.id}`}
                          className="inline-flex items-center gap-1 font-medium text-indigo-600 hover:text-indigo-700 transition-colors text-xs"
                        >
                          Detalhes <ExternalLink className="h-3 w-3" />
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
            titulo="Ambiente Cloud Seguro"
            descricao="Nenhuma misconfiguration detectada nos conectores AWS, Azure ou GCP."
          />
        )}
      </div>
    </div>
  )
}
