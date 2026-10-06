// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Vulnerabilidades.tsx — Lista central, ordenada da mais grave para a menos.
 *
 * Os filtros vão para a URL, então uma busca pode ser compartilhada por link e
 * sobrevive ao recarregar a página.
 */
import { Link, useSearchParams } from 'react-router-dom'
import { FilterX } from 'lucide-react'

import { listarAplicacoes, listarVulnerabilidades, obterOpcoes } from '../api/client'
import type { FiltrosVulnerabilidade, Risco, StatusVulnerabilidade } from '../api/types'
import {
  BadgeFerramenta,
  BadgeRisco,
  BadgeStatus,
  EtiquetaAmbiente,
  SeloCorrelacionada,
  TipoVulnerabilidade,
} from '../components/Badges'
import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'

export function Vulnerabilidades() {
  const [parametros, setParametros] = useSearchParams()

  const filtros: FiltrosVulnerabilidade = {}
  const aplicacaoId = parametros.get('aplicacao_id')
  const risco = parametros.get('risco')
  const status = parametros.get('status')
  const tipo_vuln = parametros.get('tipo_vuln')
  const correlacionadas = parametros.get('apenas_correlacionadas')

  if (aplicacaoId) filtros.aplicacao_id = Number(aplicacaoId)
  if (risco) filtros.risco = risco as Risco
  if (status) filtros.status = status as StatusVulnerabilidade
  if (tipo_vuln) filtros.tipo_vuln = tipo_vuln
  if (correlacionadas === 'true') filtros.apenas_correlacionadas = true

  const chave = parametros.toString()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const lista = useRequisicao(() => listarVulnerabilidades(filtros), [chave])
  const opcoes = useRequisicao(obterOpcoes, [])
  const aplicacoes = useRequisicao(listarAplicacoes, [])

  function definirFiltro(nome: string, valor: string) {
    const novos = new URLSearchParams(parametros)
    if (valor) {
      novos.set(nome, valor)
    } else {
      novos.delete(nome)
    }
    setParametros(novos)
  }

  if (opcoes.carregando) return <Carregando />

  return (
    <>
      <TituloDaPagina
        titulo="Vulnerabilidades"
        descricao="Ordenadas por risco. As confirmadas pelas duas ferramentas aparecem primeiro dentro de cada nível."
      />

      <div className="mb-4 flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <FiltroSelecao
          rotulo="Aplicação"
          valor={aplicacaoId ?? ''}
          aoMudar={(v) => definirFiltro('aplicacao_id', v)}
          opcoes={(aplicacoes.dados ?? []).map((app) => ({
            valor: String(app.id),
            label: app.nome,
          }))}
        />
        <FiltroSelecao
          rotulo="Risco"
          valor={risco ?? ''}
          aoMudar={(v) => definirFiltro('risco', v)}
          opcoes={opcoes.dados?.riscos ?? []}
        />
        <FiltroSelecao
          rotulo="Status"
          valor={status ?? ''}
          aoMudar={(v) => definirFiltro('status', v)}
          opcoes={opcoes.dados?.status ?? []}
        />
        <FiltroSelecao
          rotulo="Categoria"
          valor={tipo_vuln ?? ''}
          aoMudar={(v) => definirFiltro('tipo_vuln', v)}
          opcoes={[
            { valor: 'sca', label: 'Dependências (SCA)' },
            { valor: 'container_vulnerability', label: 'Container' },
            { valor: 'xss', label: 'XSS' },
            { valor: 'sqli', label: 'SQL Injection' },
            { valor: 'secrets', label: 'Credenciais Expostas' },
          ]}
        />

        <label className="flex items-center gap-2 pb-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={correlacionadas === 'true'}
            onChange={(evento) =>
              definirFiltro('apenas_correlacionadas', evento.target.checked ? 'true' : '')
            }
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          Somente correlacionadas
        </label>

        {chave && (
          <button
            type="button"
            onClick={() => setParametros(new URLSearchParams())}
            className="flex items-center gap-1 pb-2 text-sm text-slate-500 hover:text-indigo-600 hover:underline transition-all duration-200"
          >
            <FilterX className="h-4 w-4" />
            Limpar filtros
          </button>
        )}
      </div>

      {lista.carregando ? (
        <Carregando />
      ) : lista.erro ? (
        <Erro mensagem={lista.erro} aoTentar={lista.recarregar} />
      ) : !lista.dados?.length ? (
        <Vazio
          titulo="Nenhuma vulnerabilidade encontrada"
          descricao={
            chave
              ? 'Nenhum resultado para os filtros aplicados. Tente limpá-los.'
              : 'Envie os relatórios do Semgrep e do Nuclei de alguma aplicação para começar.'
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-medium">Risco</th>
                <th className="px-6 py-4 font-medium">Vulnerabilidade</th>
                <th className="px-6 py-4 font-medium">Aplicação</th>
                <th className="px-6 py-4 font-medium">Origem</th>
                <th className="px-6 py-4 font-medium">Severidade</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Identificada em</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {lista.dados.map((vuln) => (
                <tr key={vuln.id} className="transition hover:bg-slate-50">
                  <td className="px-6 py-4">
                    <BadgeRisco risco={vuln.risco} label={vuln.risco_label} />
                  </td>
                  <td className="px-6 py-4">
                    <Link
                      to={`/vulnerabilidades/${vuln.id}`}
                      className="block hover:text-indigo-600 transition-colors"
                    >
                      <span className="flex flex-wrap items-center gap-2">
                        <TipoVulnerabilidade tipo={vuln.tipo_vuln} />
                        {vuln.correlacionada && <SeloCorrelacionada />}
                      </span>
                      <span className="mt-0.5 block font-mono text-xs text-slate-500">
                        {vuln.endpoint}
                      </span>
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <span className="block text-slate-700">{vuln.aplicacao_nome}</span>
                    <EtiquetaAmbiente label={vuln.aplicacao_ambiente} />
                  </td>
                  <td className="px-6 py-4">
                    <span className="flex gap-1">
                      {vuln.origens.map((origem) => (
                        <BadgeFerramenta key={origem} nome={origem} />
                      ))}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {vuln.severidade_original ?? '—'}
                  </td>
                  <td className="px-6 py-4">
                    <BadgeStatus status={vuln.status} label={vuln.status_label} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-500">
                    {new Date(vuln.identificada_em).toLocaleDateString('pt-BR')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

function FiltroSelecao({
  rotulo,
  valor,
  opcoes,
  aoMudar,
}: {
  rotulo: string
  valor: string
  opcoes: { valor: string; label: string }[]
  aoMudar: (valor: string) => void
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500">
        {rotulo}
      </span>
      <select
        value={valor}
        onChange={(evento) => aoMudar(evento.target.value)}
        className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-shadow"
      >
        <option value="">Todas</option>
        {opcoes.map((opcao) => (
          <option key={opcao.valor} value={opcao.valor}>
            {opcao.label}
          </option>
        ))}
      </select>
    </label>
  )
}
