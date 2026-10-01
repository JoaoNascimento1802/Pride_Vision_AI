import { useEffect, useState } from 'react'
import { listarStatusIntegracoes } from '../api/client'

const RefreshCcw = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M21 2v6h-6"></path><path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path><path d="M3 22v-6h6"></path><path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path></svg>
)

const Github = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
)

const Gitlab = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="m22 13.29-3.33-10a.42.42 0 0 0-.14-.18.38.38 0 0 0-.22-.11.39.39 0 0 0-.23.07.42.42 0 0 0-.14.18l-2.26 6.67H8.32L6.1 3.26a.42.42 0 0 0-.1-.18.38.38 0 0 0-.26-.08.39.39 0 0 0-.23.07.42.42 0 0 0-.14.18L2 13.29a.74.74 0 0 0 .27.83L12 21l9.69-6.88a.71.71 0 0 0 .31-.83Z"></path></svg>
)

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Integrações</h1>
          <p className="text-slate-500 mt-2">
            Configure e monitore a conexão com plataformas externas (GitHub, GitLab, etc).
          </p>
        </div>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 disabled:opacity-50"
        >
          <RefreshCcw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Test Connection
        </button>
      </div>

      {erro && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="text-sm text-red-700">{erro}</div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
        {/* GitHub */}
        <div className="overflow-hidden rounded-lg bg-white shadow ring-1 ring-slate-200">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Github className="w-5 h-5 mr-2 text-slate-700" />
                <h3 className="text-base font-semibold leading-6 text-slate-900">GitHub</h3>
              </div>
              <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                status.github === 'Connected' 
                  ? 'bg-green-50 text-green-700 ring-green-600/20' 
                  : 'bg-slate-50 text-slate-700 ring-slate-600/20'
              }`}>
                {status.github}
              </span>
            </div>
            <div className="mt-4 text-sm text-slate-500">
              <p>Feedback real de Security Gates em Pull Requests e envio de Commits Statuses.</p>
              {status.github === 'Connected' && (
                <p className="mt-2 font-medium text-green-700">App Autenticado e Pronto</p>
              )}
            </div>
          </div>
        </div>

        {/* GitLab */}
        <div className="overflow-hidden rounded-lg bg-white shadow ring-1 ring-slate-200">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Gitlab className="w-5 h-5 mr-2 text-orange-500" />
                <h3 className="text-base font-semibold leading-6 text-slate-900">GitLab</h3>
              </div>
              <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                status.gitlab === 'Available' 
                  ? 'bg-green-50 text-green-700 ring-green-600/20' 
                  : 'bg-slate-50 text-slate-700 ring-slate-600/20'
              }`}>
                {status.gitlab}
              </span>
            </div>
            <div className="mt-4 text-sm text-slate-500">
              <p>Integração com Merge Requests e pipelines do GitLab CI.</p>
            </div>
          </div>
        </div>

        {/* Jira */}
        <div className="overflow-hidden rounded-lg bg-white shadow ring-1 ring-slate-200">
          <div className="p-6 flex flex-col h-full">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-5 h-5 mr-2 text-blue-600 flex items-center justify-center font-bold font-serif">J</div>
                <h3 className="text-base font-semibold leading-6 text-slate-900">Jira</h3>
              </div>
              <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                status.jira === 'Connected' 
                  ? 'bg-green-50 text-green-700 ring-green-600/20' 
                  : 'bg-slate-50 text-slate-700 ring-slate-600/20'
              }`}>
                {status.jira}
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
                  className="w-full inline-flex justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
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
