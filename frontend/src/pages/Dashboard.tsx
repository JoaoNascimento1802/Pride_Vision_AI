/**
 * Dashboard.tsx — Tela inicial.
 *
 * Responde de relance à pergunta que a plataforma existe para resolver: quanto
 * risco há, e onde ele está concentrado.
 */
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link } from 'react-router-dom'

import { obterDashboard } from '../api/client'
import type { Risco } from '../api/types'
import { Cartao, Carregando, Erro, Vazio } from '../components/Feedback'
import { EtiquetaAmbiente } from '../components/Badges'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'

// Mesmas cores dos badges, para o gráfico e a tabela contarem a mesma história
const COR_RISCO: Record<string, string> = {
  critico: '#b42318',
  alto: '#d97706',
  medio: '#ca8a04',
  baixo: '#0e7490',
}

const COR_STATUS: Record<string, string> = {
  nova: '#64748b',
  em_analise: '#0284c7',
  em_correcao: '#4f46e5',
  corrigida: '#059669',
  falso_positivo: '#94a3b8',
}

export function Dashboard() {
  const { dados, carregando, erro, recarregar } = useRequisicao(obterDashboard, [])

  if (carregando) return <Carregando />
  if (erro) return <Erro mensagem={erro} aoTentar={recarregar} />
  if (!dados) return null

  const semDados = dados.total_aplicacoes === 0

  return (
    <>
      <TituloDaPagina
        titulo="Visão geral"
        descricao="Situação de segurança das aplicações cadastradas."
      />

      {semDados ? (
        <Vazio
          titulo="Nenhuma aplicação cadastrada"
          descricao="Cadastre uma aplicação e envie os relatórios do Semgrep e do Nuclei para ver a análise aqui."
          acao={
            <Link
              to="/aplicacoes"
              className="inline-block rounded-md bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
            >
              Cadastrar aplicação
            </Link>
          }
        />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
            <Indicador rotulo="Aplicações" valor={dados.total_aplicacoes} />
            <Indicador rotulo="Vulnerabilidades" valor={dados.total_vulnerabilidades} />
            <Indicador rotulo="Críticas" valor={dados.total_criticas} destaque="critico" />
            <Indicador rotulo="Em correção" valor={dados.total_em_correcao} />
            <Indicador rotulo="Corrigidas" valor={dados.total_corrigidas} destaque="ok" />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Cartao titulo="Vulnerabilidades por risco">
              {dados.total_vulnerabilidades === 0 ? (
                <p className="py-8 text-center text-sm text-slate-500">
                  Nenhum relatório processado ainda.
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={dados.por_risco} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                    <Tooltip
                      cursor={{ fill: '#f1f5f9' }}
                      formatter={(valor) => [`${valor}`, 'Vulnerabilidades']}
                    />
                    <Bar dataKey="total" radius={[4, 4, 0, 0]}>
                      {dados.por_risco.map((item) => (
                        <Cell key={item.valor} fill={COR_RISCO[item.valor] ?? '#94a3b8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Cartao>

            <Cartao titulo="Situação do tratamento">
              {dados.total_vulnerabilidades === 0 ? (
                <p className="py-8 text-center text-sm text-slate-500">
                  Nenhum relatório processado ainda.
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie
                      data={dados.por_status.filter((item) => item.total > 0)}
                      dataKey="total"
                      nameKey="label"
                      innerRadius={50}
                      outerRadius={85}
                      paddingAngle={2}
                    >
                      {dados.por_status
                        .filter((item) => item.total > 0)
                        .map((item) => (
                          <Cell key={item.valor} fill={COR_STATUS[item.valor] ?? '#94a3b8'} />
                        ))}
                    </Pie>
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <Tooltip formatter={(valor) => [`${valor}`, 'Vulnerabilidades']} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </Cartao>
          </div>

          <Cartao titulo="Aplicações com maior risco">
            {dados.aplicacoes_em_risco.length === 0 ? (
              <p className="py-6 text-center text-sm text-slate-500">
                Nenhuma vulnerabilidade registrada.
              </p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-500">
                    <th className="pb-2 font-medium">Aplicação</th>
                    <th className="pb-2 font-medium">Ambiente</th>
                    <th className="pb-2 font-medium">Exposição</th>
                    <th className="pb-2 text-right font-medium">Críticas</th>
                    <th className="pb-2 text-right font-medium">Altas</th>
                    <th className="pb-2 text-right font-medium">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {dados.aplicacoes_em_risco.map((app) => (
                    <tr key={app.id} className="hover:bg-slate-50">
                      <td className="py-2.5">
                        <Link
                          to={`/vulnerabilidades?aplicacao_id=${app.id}`}
                          className="font-medium text-slate-800 hover:text-violet-700 hover:underline"
                        >
                          {app.nome}
                        </Link>
                      </td>
                      <td className="py-2.5">
                        <EtiquetaAmbiente label={app.ambiente} />
                      </td>
                      <td className="py-2.5 text-slate-600">{app.exposicao}</td>
                      <td className="py-2.5 text-right font-semibold text-critico">
                        {app.criticas || '—'}
                      </td>
                      <td className="py-2.5 text-right font-medium text-alto">
                        {app.altas || '—'}
                      </td>
                      <td className="py-2.5 text-right text-slate-600">{app.total}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Cartao>
        </div>
      )}
    </>
  )
}

function Indicador({
  rotulo,
  valor,
  destaque,
}: {
  rotulo: string
  valor: number
  destaque?: Risco | 'ok'
}) {
  const cor =
    destaque === 'critico' && valor > 0
      ? 'text-critico'
      : destaque === 'ok' && valor > 0
        ? 'text-emerald-600'
        : 'text-slate-900'

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{rotulo}</p>
      <p className={`mt-1 text-2xl font-semibold ${cor}`}>{valor}</p>
    </div>
  )
}
