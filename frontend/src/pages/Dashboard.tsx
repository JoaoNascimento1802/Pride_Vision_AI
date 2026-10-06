// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

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
import { Server, ShieldAlert, Shield, ShieldCheck, Activity } from 'lucide-react'

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
              className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-all duration-200 hover:bg-indigo-700 hover:shadow-md"
            >
              <Server className="h-4 w-4" />
              Cadastrar aplicação
            </Link>
          }
        />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
            <Indicador rotulo="Aplicações" valor={dados.total_aplicacoes} icone={Server} />
            <Indicador rotulo="Vulnerabilidades" valor={dados.total_vulnerabilidades} icone={ShieldAlert} />
            <Indicador rotulo="Críticas" valor={dados.total_criticas} destaque="critico" icone={Activity} />
            <Indicador rotulo="Em correção" valor={dados.total_em_correcao} icone={Shield} />
            <Indicador rotulo="Corrigidas" valor={dados.total_corrigidas} destaque="ok" icone={ShieldCheck} />
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

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h3 className="text-sm font-semibold text-slate-800">Aplicações com maior risco</h3>
            </div>
            {dados.aplicacoes_em_risco.length === 0 ? (
              <p className="py-6 text-center text-sm text-slate-500">
                Nenhuma vulnerabilidade registrada.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm divide-y divide-slate-200">
                  <thead className="bg-slate-50">
                    <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
                      <th className="px-6 py-4 font-medium">Aplicação</th>
                      <th className="px-6 py-4 font-medium">Ambiente</th>
                      <th className="px-6 py-4 font-medium">Exposição</th>
                      <th className="px-6 py-4 text-right font-medium">Críticas</th>
                      <th className="px-6 py-4 text-right font-medium">Altas</th>
                      <th className="px-6 py-4 text-right font-medium">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {dados.aplicacoes_em_risco.map((app) => (
                      <tr key={app.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <Link
                            to={`/vulnerabilidades?aplicacao_id=${app.id}`}
                            className="font-medium text-slate-800 hover:text-indigo-600 hover:underline"
                          >
                            {app.nome}
                          </Link>
                        </td>
                        <td className="px-6 py-4">
                          <EtiquetaAmbiente label={app.ambiente} />
                        </td>
                        <td className="px-6 py-4 text-slate-600">{app.exposicao}</td>
                        <td className="px-6 py-4 text-right font-semibold text-red-700">
                          {app.criticas || '—'}
                        </td>
                        <td className="px-6 py-4 text-right font-medium text-amber-600">
                          {app.altas || '—'}
                        </td>
                        <td className="px-6 py-4 text-right text-slate-600">{app.total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

function Indicador({
  rotulo,
  valor,
  destaque,
  icone: Icon,
}: {
  rotulo: string
  valor: number
  destaque?: Risco | 'ok'
  icone?: React.ElementType
}) {
  const cor =
    destaque === 'critico' && valor > 0
      ? 'text-red-700'
      : destaque === 'ok' && valor > 0
        ? 'text-emerald-600'
        : 'text-slate-800'

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex items-center justify-between">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{rotulo}</p>
        <p className={`mt-2 text-3xl font-semibold ${cor}`}>{valor}</p>
      </div>
      {Icon && (
        <div className={`p-3 rounded-full ${destaque === 'critico' ? 'bg-red-50 text-red-600' : destaque === 'ok' ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-50 text-slate-400'}`}>
          <Icon className="h-6 w-6" />
        </div>
      )}
    </div>
  )
}
