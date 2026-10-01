/**
 * CloudCspm.tsx — Inventário de recursos cloud e misconfigurations.
 *
 * Exibe findings de postura (Prowler / Security Hub / CloudSploit) com destaque
 * para Toxic Combinations (recurso cloud exposto + container vulnerável).
 */
import { Link } from 'react-router-dom'

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
        ☠️ TOXIC COMBINATION
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
    <>
      <TituloDaPagina
        titulo="Cloud CSPM"
        descricao="Inventário de recursos e misconfigurations detectados por scanners de postura (Prowler, Security Hub, CloudSploit)."
        acao={
          <button
            onClick={recarregar}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50"
          >
            ↺ Atualizar
          </button>
        }
      />

      {carregando && <Carregando />}
      {erro && <Erro mensagem={erro} />}

      {!carregando && !erro && (
        <>
          {/* Cards de alerta: Toxic Combinations */}
          {criticos.length > 0 && (
            <div className="mb-6">
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-red-600">
                ⚠️ Combinações Tóxicas ({criticos.length})
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {criticos.map((v) => (
                  <div
                    key={v.id}
                    className="rounded-lg border-2 border-red-300 bg-red-50 p-4 shadow-sm"
                  >
                    <div className="mb-2 flex items-start justify-between gap-2">
                      <span className="text-xs font-semibold text-red-800">{providerIcon(v.endpoint)}</span>
                      {badgeToxic(v)}
                    </div>
                    <div className="mb-1 font-medium text-slate-900 text-sm">{v.tipo_vuln}</div>
                    <div className="mb-2 font-mono text-xs text-slate-500 truncate" title={v.endpoint}>{v.endpoint}</div>
                    <div className="mb-3 text-xs text-slate-600 line-clamp-2">{v.severidade_original}</div>
                    <div className="flex items-center justify-between">
                      <BadgeRisco risco={v.risco as Risco} label={v.risco} />
                      <Link
                        to={`/vulnerabilidades/${v.id}`}
                        className="text-xs text-violet-600 hover:underline"
                      >
                        Ver detalhes →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tabela de misconfigurations gerais */}
          {outros.length > 0 ? (
            <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
                <h2 className="text-sm font-semibold text-slate-700">
                  Misconfigurations ({outros.length})
                </h2>
              </div>
              <table className="min-w-full divide-y divide-slate-100 text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-slate-600">Provider / Recurso</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-600">Misconfiguration</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-600">Risco</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {outros.map((v) => (
                    <tr key={v.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3">
                        <div className="text-xs text-slate-500">{providerIcon(v.endpoint)}</div>
                        <div className="mt-0.5 font-mono text-xs text-slate-600 truncate max-w-xs" title={v.endpoint}>
                          {v.endpoint}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-900">{v.tipo_vuln}</div>
                        <div className="mt-0.5 text-xs text-slate-500 line-clamp-1">{v.severidade_original}</div>
                      </td>
                      <td className="px-4 py-3">
                        <BadgeRisco risco={v.risco as Risco} label={v.risco} />
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-slate-600">{v.status_label ?? v.status}</span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          to={`/vulnerabilidades/${v.id}`}
                          className="text-xs text-violet-600 hover:underline"
                        >
                          Detalhe →
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
              descricao="Configure o webhook apontando para /api/v1/ingestion/cspm."
            />
          ) : null}
        </>
      )}
    </>
  )
}

