// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import { useParams, Link } from 'react-router-dom'
import { Package, ShieldCheck, FileJson, ArrowLeft, ExternalLink, ShieldAlert } from 'lucide-react'

import { http } from '../api/client'
import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'

interface SbomResumo {
  id: number
  aplicacao_id: number
  versao_app: string
  spec_version: string
  serial_number: string
  criado_em: string
}

interface SbomComponentDetalhe {
  id: number
  nome: string
  versao: string
  ecossistema: string
  tipo_componente: string
  purl: string
  licenca: string | null
}

export function SbomVisualizer() {
  const { id } = useParams() // aplicacao_id

  const { dados: sboms, carregando: c1, erro: e1 } = useRequisicao(
    () => http.get<SbomResumo[]>(\/api/aplicacoes/\/sboms\).then(res => res.data),
    [id]
  )

  const latestSbom = sboms?.[0]

  const { dados: componentes, carregando: c2, erro: e2 } = useRequisicao(
    () => latestSbom ? http.get<SbomComponentDetalhe[]>(\/api/sboms/\/componentes\).then(res => res.data) : Promise.resolve([]),
    [latestSbom?.id]
  )

  const carregando = c1 || (latestSbom && c2)
  const erro = e1 || e2

  return (
    <div className="bg-slate-50 min-h-screen">
      <TituloDaPagina
        titulo={
          <span className="flex items-center gap-2">
            <Package className="h-6 w-6 text-indigo-600" />
            Software Bill of Materials (SBOM)
          </span>
        }
        descricao="Visualizao da rvore de dependncias e supply chain em conformidade com CycloneDX."
        acao={
          <Link
            to="/aplicacoes"
            className="flex items-center gap-2 transition-all duration-200 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 hover:shadow-md"
          >
            <ArrowLeft className="h-4 w-4" /> Voltar
          </Link>
        }
      />

      {carregando && !componentes ? (
        <Carregando />
      ) : erro ? (
        <Erro mensagem={erro} />
      ) : !latestSbom ? (
        <Vazio
          titulo="Nenhum SBOM encontrado"
          descricao="No h arquivos CycloneDX processados para esta aplicao."
        />
      ) : (
        <div className="space-y-6">
          <div className="grid gap-6 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-indigo-50 p-2"><FileJson className="h-5 w-5 text-indigo-600"/></div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Spec / Formato</p>
                  <p className="text-lg font-bold text-slate-900">CycloneDX {latestSbom.spec_version}</p>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-emerald-50 p-2"><ShieldCheck className="h-5 w-5 text-emerald-600"/></div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Total de Componentes</p>
                  <p className="text-lg font-bold text-slate-900">{componentes?.length || 0}</p>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-amber-50 p-2"><ShieldAlert className="h-5 w-5 text-amber-600"/></div>
                <div>
                  <p className="text-sm font-medium text-slate-500">ltima Atualizao</p>
                  <p className="text-sm font-bold text-slate-900 mt-1">{new Date(latestSbom.criado_em).toLocaleString('pt-BR')}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
             <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
                <h3 className="font-semibold text-slate-800">Inventrio de Dependncias (Supply Chain)</h3>
             </div>
             <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Nome do Pacote</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Verso</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Ecossistema</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">Licena</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-800">PURL</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {(componentes || []).map((c) => (
                    <tr key={c.id} className="hover:bg-slate-50 transition-colors duration-150">
                      <td className="px-6 py-4 font-medium text-slate-900">{c.nome}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">{c.versao}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                          {c.ecossistema || 'library'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-600">{c.licenca || 'No declarada'}</td>
                      <td className="px-6 py-4 font-mono text-[10px] text-slate-400 truncate max-w-xs" title={c.purl}>
                        {c.purl}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
