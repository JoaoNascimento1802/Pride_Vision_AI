/**
 * CloudCspm.tsx — Inventário de recursos cloud e misconfigurations.
 *
 * Exibe findings de postura (Prowler / Security Hub / CloudSploit) com destaque
 * para Toxic Combinations (recurso cloud exposto + container vulnerável).
 */
import { Link } from 'react-router-dom'
import { Cloud, ShieldAlert, ExternalLink, RefreshCw, AlertTriangle } from 'lucide-react'

import { listarVulnerabilidades } from '../api/client'
import { BadgeRisco } from '../components/Badges'
import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'
import type { Risco, Vulnerabilidade } from '../api/types'

function providerIcon(endpoint: string) {
  if (endpoint.includes('arn:aws')) return '🟠 AWS'
  if (endpoint.includes('projects/')) return '🔵 GCP'
  if (endpoint.includes('azure')) return '🔷 Azure'
  return '☁️ Cloud'
}

function badgeToxic(v: Vulnerabilidade) {
  if (v.risco === 'critico') {
    return (
      <span className="inline-flex items-center gap-1 rounded-md bg-red-100 px-2 py-0.5 text-xs font-bold text-red-800 ring-1 ring-red-300">
        <AlertTriangle className="h-3 w-3" /> TOXIC COMBINATION
      </span>
    )
  }
  return null
}

export function CloudCspm() {
  // Usa listarVulnerabilidades — o Risk Engine já elevou CSPM + container para CRITICO
  const { dados, carregando, erro, recarregar } = useRequisicao(
    () => listarVulnerabilidades({ tipo_vuln: 'cloud' }),
    [],
  )

  const criticos = dados?.filter((v) => v.risco === 'critico') ?? []
  const outros = dados?.filter((v) => v.risco !== 'critico') ?? []

  return (
    <div className="bg-slate-50 min-h-screen">
      <TituloDaPagina
        titulo={
          <span className="flex items-center gap-2">
            <Cloud className="h-6 w-6 text-indigo-600" />
            Cloud CSPM
          </span>
        }
        descricao="Inventário de recursos e configurações incorretas detectadas por scanners de postura (Prowler, Security Hub, CloudSploit)."
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
        {carregando && <Carregando />}
        {erro && <Erro mensagem={erro} />}

        {!carregando && !erro && (
          <>
            {/* Cards de alerta: Toxic Combinations */}
            {criticos.length > 0 && (
              <div className="mb-6">
                <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-red-600 flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5" /> Combinações Tóxicas ({criticos.length})
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {criticos.map((v) => (
                    <div
                      key={v.id}
                      className="bg-white rounded-xl border-2 border-red-300 shadow-sm p-5 hover:shadow-md transition-shadow duration-200"
                    >
                      <div className="mb-3 flex items-start justify-between gap-2">
                        <span className="text-xs font-semibold text-slate-800">{providerIcon(v.endpoint)}</span>
                        {badgeToxic(v)}
                      </div>
                      <div className="mb-1 font-semibold text-slate-900 text-sm">{v.tipo_vuln}</div>
                      <div className="mb-3 font-mono text-xs text-slate-500 truncate" title={v.endpoint}>{v.endpoint}</div>
                      <div className="mb-4 text-xs text-slate-600 line-clamp-2">{v.severidade_original}</div>
                      <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                        <BadgeRisco risco={v.risco as Risco} label={v.risco} />
                        <Link
                          to={`/vulnerabilidades/${v.id}`}
                          className="flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                        >
                          Ver detalhes <ExternalLink className="h-3 w-3" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tabela de misconfigurations gerais */}
            {outros.length > 0 ? (
              <div className="overflow-hidden bg-white rounded-xl border border-slate-200 shadow-sm">
                <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
                  <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                    <Cloud className="h-4 w-4 text-slate-500" />
                    Configurações Incorretas ({outros.length})
                  </h2>
                </div>
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-4 text-left font-semibold text-slate-800">Provedor / Recurso</th>
                      <th className="px-6 py-4 text-left font-semibold text-slate-800">Configuração Incorreta</th>
                      <th className="px-6 py-4 text-left font-semibold text-slate-800">Risco</th>
                      <th className="px-6 py-4 text-left font-semibold text-slate-800">Status</th>
                      <th className="px-6 py-4"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {outros.map((v) => (
                      <tr key={v.id} className="hover:bg-slate-50 transition-colors duration-150">
                        <td className="px-6 py-4">
                          <div className="text-xs font-medium text-slate-500 mb-1">{providerIcon(v.endpoint)}</div>
                          <div className="font-mono text-xs text-slate-600 truncate max-w-xs" title={v.endpoint}>
                            {v.endpoint}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-medium text-slate-900">{v.tipo_vuln}</div>
                          <div className="mt-1 text-xs text-slate-500 line-clamp-1">{v.severidade_original}</div>
                        </td>
                        <td className="px-6 py-4">
                          <BadgeRisco risco={v.risco as Risco} label={v.risco} />
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
                            {v.status_label ?? v.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <Link
                            to={`/vulnerabilidades/${v.id}`}
                            className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                          >
                            Detalhe <ExternalLink className="h-3 w-3" />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : criticos.length === 0 ? (
              <Vazio
                titulo="Nenhum finding de Cloud CSPM encontrado"
                descricao="Configure a integração para a detecção de vulnerabilidades."
              />
            ) : null}
          </>
        )}
      </div>
    </div>
  )
}
