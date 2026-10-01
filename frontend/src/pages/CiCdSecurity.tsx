/**
 * CiCdSecurity.tsx — Painel de CI/CD Security Gates.
 *
 * Exibe pipelines avaliados, histórico de decisões (PASS/WARN/BLOCK),
 * políticas ativas e permite executar um check manual.
 */
import { useEffect, useState } from 'react'

import {
  desativarPolicy,
  executarCheck,
  listarGateResults,
  listarPipelines,
  listarPolicies,
  mensagemDeErro,
} from '../api/client'
import type { GateDecision, GateResult, PipelineRun, Policy } from '../api/types'
import { TituloDaPagina } from '../components/Layout'

// ─── helpers visuais ──────────────────────────────────────────────────────────

const BADGE: Record<GateDecision, string> = {
  pass: 'bg-emerald-100 text-emerald-800',
  warn: 'bg-amber-100 text-amber-800',
  block: 'bg-red-100 text-red-800',
}

const ICONE: Record<GateDecision, string> = {
  pass: '✅',
  warn: '⚠️',
  block: '🚫',
}

const LABEL: Record<GateDecision, string> = {
  pass: 'Aprovado',
  warn: 'Com aviso',
  block: 'Bloqueado',
}

function BadgeDecision({ decision }: { decision: GateDecision }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${BADGE[decision]}`}
    >
      {ICONE[decision]} {LABEL[decision]}
    </span>
  )
}

function formatar(iso: string) {
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// ─── componente principal ─────────────────────────────────────────────────────

export function CiCdSecurity() {
  const [pipelines, setPipelines] = useState<PipelineRun[]>([])
  const [gateResults, setGateResults] = useState<GateResult[]>([])
  const [policies, setPolicies] = useState<Policy[]>([])
  const [erro, setErro] = useState<string | null>(null)
  const [checkando, setCheckando] = useState(false)
  const [checkErro, setCheckErro] = useState<string | null>(null)
  const [appId, setAppId] = useState('')

  const carregar = () => {
    Promise.all([listarPipelines(), listarGateResults(), listarPolicies()])
      .then(([p, g, pol]) => {
        setPipelines(p)
        setGateResults(g)
        setPolicies(pol)
      })
      .catch((e) => setErro(mensagemDeErro(e)))
  }

  useEffect(() => {
    carregar()
  }, [])

  // Contadores de resumo
  const totalPass = gateResults.filter((g) => g.decision === 'pass').length
  const totalWarn = gateResults.filter((g) => g.decision === 'warn').length
  const totalBlock = gateResults.filter((g) => g.decision === 'block').length

  const handleCheck = async () => {
    const id = parseInt(appId, 10)
    if (isNaN(id) || id <= 0) {
      setCheckErro('Informe um ID de aplicação válido.')
      return
    }
    setCheckErro(null)
    setCheckando(true)
    try {
      await executarCheck({ application_id: id })
      carregar()
    } catch (e) {
      setCheckErro(mensagemDeErro(e))
    } finally {
      setCheckando(false)
    }
  }

  const handleDesativarPolicy = async (id: number) => {
    try {
      await desativarPolicy(id)
      carregar()
    } catch (e) {
      setErro(mensagemDeErro(e))
    }
  }

  if (erro) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
        Erro ao carregar dados: {erro}
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <TituloDaPagina
        titulo="CI/CD Security Gates"
        descricao="Pipelines avaliados, decisões PASS / WARN / BLOCK e políticas de segurança."
      />

      {/* ── Resumo ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { rotulo: 'Pipelines', valor: pipelines.length, cor: 'text-slate-700' },
          { rotulo: 'Aprovados', valor: totalPass, cor: 'text-emerald-700' },
          { rotulo: 'Com aviso', valor: totalWarn, cor: 'text-amber-700' },
          { rotulo: 'Bloqueados', valor: totalBlock, cor: 'text-red-700' },
        ].map(({ rotulo, valor, cor }) => (
          <div
            key={rotulo}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <p className="text-xs font-medium text-slate-500">{rotulo}</p>
            <p className={`mt-1 text-2xl font-bold ${cor}`}>{valor}</p>
          </div>
        ))}
      </div>

      {/* ── Check manual ───────────────────────────────────────────── */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-sm font-semibold text-slate-800">Executar check manual</h2>
        <div className="flex items-center gap-3">
          <input
            type="number"
            min={1}
            placeholder="ID da aplicação"
            value={appId}
            onChange={(e) => setAppId(e.target.value)}
            className="w-44 rounded-lg border border-slate-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
          />
          <button
            onClick={handleCheck}
            disabled={checkando}
            className="rounded-lg bg-violet-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
          >
            {checkando ? 'Avaliando…' : 'Executar gate'}
          </button>
        </div>
        {checkErro && <p className="mt-2 text-xs text-red-600">{checkErro}</p>}
      </div>

      {/* ── Histórico de pipelines ─────────────────────────────────── */}
      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Pipelines recentes</h2>
        {pipelines.length === 0 ? (
          <p className="text-sm text-slate-400">Nenhum pipeline avaliado ainda.</p>
        ) : (
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-100 bg-slate-50 text-xs font-medium text-slate-500">
                <tr>
                  <th className="px-4 py-2 text-left">App</th>
                  <th className="px-4 py-2 text-left">Branch</th>
                  <th className="px-4 py-2 text-left">Commit</th>
                  <th className="px-4 py-2 text-left">Provider</th>
                  <th className="px-4 py-2 text-left">Última decisão</th>
                  <th className="px-4 py-2 text-left">Em</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {pipelines.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50">
                    <td className="px-4 py-2 font-mono text-xs">{run.aplicacao_id}</td>
                    <td className="px-4 py-2 text-slate-600">{run.branch ?? '—'}</td>
                    <td className="px-4 py-2 font-mono text-xs text-slate-500">
                      {run.commit_sha ? run.commit_sha.slice(0, 8) : '—'}
                    </td>
                    <td className="px-4 py-2 text-slate-500 capitalize">
                      {run.provider ?? '—'}
                    </td>
                    <td className="px-4 py-2">
                      {run.ultimo_resultado ? (
                        <BadgeDecision decision={run.ultimo_resultado.decision} />
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-slate-400">
                      {run.ultimo_resultado
                        ? formatar(run.ultimo_resultado.avaliado_em)
                        : formatar(run.criado_em)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* ── Políticas ativas ───────────────────────────────────────── */}
      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Políticas ativas</h2>
        {policies.length === 0 ? (
          <p className="text-sm text-slate-400">Nenhuma política configurada.</p>
        ) : (
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-100 bg-slate-50 text-xs font-medium text-slate-500">
                <tr>
                  <th className="px-4 py-2 text-left">Nome</th>
                  <th className="px-4 py-2 text-left">Risco mín.</th>
                  <th className="px-4 py-2 text-left">Ação</th>
                  <th className="px-4 py-2 text-left">Escopo</th>
                  <th className="px-4 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {policies.map((pol) => (
                  <tr key={pol.id} className="hover:bg-slate-50">
                    <td className="px-4 py-2 font-medium text-slate-800">{pol.nome}</td>
                    <td className="px-4 py-2 capitalize text-slate-600">{pol.risco_minimo}</td>
                    <td className="px-4 py-2">
                      <BadgeDecision decision={pol.acao} />
                    </td>
                    <td className="px-4 py-2 text-slate-500">
                      {pol.aplicacao_id ? `App #${pol.aplicacao_id}` : 'Global'}
                    </td>
                    <td className="px-4 py-2 text-right">
                      <button
                        onClick={() => handleDesativarPolicy(pol.id)}
                        className="rounded px-2 py-0.5 text-xs text-red-500 hover:bg-red-50"
                      >
                        Desativar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

