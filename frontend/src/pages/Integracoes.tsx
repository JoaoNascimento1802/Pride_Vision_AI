// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import { useEffect, useState } from 'react'
import { RefreshCcw, Code, Kanban } from 'lucide-react'
import { listarStatusIntegracoes } from '../api/client'

export default function Integracoes() {
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [status, setStatus] = useState<{ github: string; gitlab: string; jira?: string; jira_site?: string }>({
    github: 'Not configured',
    gitlab: 'Not configured'
  })

  const fetchStatus = async () => {
    try {
      setLoading(true)
      setErro(null)
      const data = await listarStatusIntegracoes()
      setStatus(data)
    } catch (err: any) {
      setErro(err.message || 'Erro ao carregar status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  return (
    <div className="space-y-6 animate-in fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Integrações</h1>
          <p className="text-slate-500 mt-2">
            Configure e monitore a conexão com plataformas externas (GitHub, GitLab, etc).
          </p>
        </div>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:bg-indigo-700 hover:shadow-md disabled:opacity-50"
        >
          <RefreshCcw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Testar Conexão
        </button>
      </div>

      {erro && (
        <div className="rounded-xl bg-red-50 p-4 border border-red-200">
          <div className="text-sm text-red-700">{erro}</div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
        {/* GitHub */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Code className="w-5 h-5 mr-2 text-slate-700" />
                <h3 className="text-base font-semibold leading-6 text-slate-900">GitHub</h3>
              </div>
              <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                status.github === 'Connected' 
                  ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' 
                  : 'bg-slate-50 text-slate-700 ring-slate-600/20'
              }`}>
                {status.github === 'Connected' ? 'Conectado' : 'Não configurado'}
              </span>
            </div>
            <div className="mt-4 text-sm text-slate-500">
              <p>Feedback real de Security Gates em Pull Requests e envio de Commits Statuses.</p>
              {status.github === 'Connected' && (
                <p className="mt-2 font-medium text-emerald-700">App Autenticado e Pronto</p>
              )}
            </div>
          </div>
        </div>

        {/* GitLab */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Code className="w-5 h-5 mr-2 text-orange-500" />
                <h3 className="text-base font-semibold leading-6 text-slate-900">GitLab</h3>
              </div>
              <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                status.gitlab === 'Available' 
                  ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' 
                  : 'bg-slate-50 text-slate-700 ring-slate-600/20'
              }`}>
                {status.gitlab === 'Available' ? 'Disponível' : 'Não configurado'}
              </span>
            </div>
            <div className="mt-4 text-sm text-slate-500">
              <p>Integração com Merge Requests e pipelines do GitLab CI.</p>
            </div>
          </div>
        </div>

        {/* Jira */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col transition-all duration-200 hover:shadow-md">
          <div className="p-6 flex flex-col h-full">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Kanban className="w-5 h-5 mr-2 text-indigo-600" />
                <h3 className="text-base font-semibold leading-6 text-slate-900">Jira</h3>
              </div>
              <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                status.jira === 'Connected' 
                  ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' 
                  : 'bg-slate-50 text-slate-700 ring-slate-600/20'
              }`}>
                {status.jira === 'Connected' ? 'Conectado' : 'Não configurado'}
              </span>
            </div>
            <div className="mt-4 text-sm text-slate-500 flex-grow">
              <p>Ticketing bi-direcional seguro (OAuth 3LO) com Atlassian Jira Cloud.</p>
              {status.jira === 'Connected' && (
                <p className="mt-2 text-xs truncate" title={status.jira_site}>
                  Conectado a: {status.jira_site}
                </p>
              )}
            </div>
            <div className="mt-6">
              {status.jira === 'Connected' ? (
                <button
                  disabled
                  className="w-full inline-flex justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 opacity-50 cursor-not-allowed"
                >
                  Conectado
                </button>
              ) : (
                <a
                  href="/api/integrations/jira/authorize"
                  className="w-full inline-flex justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:bg-indigo-500 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Conectar ao Jira
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
