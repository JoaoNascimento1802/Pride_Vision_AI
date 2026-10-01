import { useEffect, useState } from 'react'
import { Cartao } from '../components/Feedback'
import { http } from '../api/client'

interface HealthStatus {
  status: string
  database: string
  services: {
    jira: string
    genai: string
  }
}

interface MetricsData {
  totalRequests: number
  errorRate: number
  totalErrors: number
  activeTasks: number
  dbConnections: number
}

export function Observability() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    carregar()
  }, [])

  async function carregar() {
    setLoading(true)
    try {
      const [resHealth, resMetrics] = await Promise.all([
        http.get<HealthStatus>('/api/health'),
        http.get<string>('/metrics', { headers: { Accept: 'text/plain' } })
      ])
      
      setHealth(resHealth.data)
      setMetrics(parseMetrics(resMetrics.data))
    } catch (error) {
      console.error('Erro ao carregar telemetria:', error)
    } finally {
      setLoading(false)
    }
  }

  function parseMetrics(text: string): MetricsData {
    let totalRequests = 0
    let totalErrors = 0
    let activeTasks = 0
    let dbConnections = 0

    const lines = text.split('\n')
    for (const line of lines) {
      if (line.startsWith('#')) continue

      if (line.startsWith('http_requests_total')) {
        const value = parseFloat(line.split(' ').pop() || '0')
        totalRequests += value
        if (line.includes('status_code="500"') || line.includes('status_code="4') || line.includes('status_code="5')) {
          totalErrors += value
        }
      } else if (line.startsWith('background_tasks_queue_size')) {
        activeTasks = parseFloat(line.split(' ').pop() || '0')
      } else if (line.startsWith('db_active_connections')) {
        dbConnections = parseFloat(line.split(' ').pop() || '0')
      }
    }

    return {
      totalRequests,
      totalErrors,
      errorRate: totalRequests > 0 ? (totalErrors / totalRequests) * 100 : 0,
      activeTasks,
      dbConnections
    }
  }

  if (loading) {
    return <div className="p-6 text-gray-500">Carregando métricas...</div>
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">System Health (Observability)</h1>
        <button onClick={carregar} className="bg-slate-200 px-3 py-1 rounded">Atualizar</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Cartao titulo="Deep Health Check">
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="font-medium">Status Geral</span>
              <span className={`px-2 py-1 rounded text-sm ${health?.status === 'ok' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {health?.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="font-medium">Banco de Dados</span>
              <span className={`px-2 py-1 rounded text-sm ${health?.database === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {health?.database?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="font-medium">Integração Jira</span>
              <span className={`px-2 py-1 rounded text-sm ${health?.services?.jira === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {health?.services?.jira?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="font-medium">Motor GenAI</span>
              <span className={`px-2 py-1 rounded text-sm ${health?.services?.genai === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {health?.services?.genai?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
          </div>
        </Cartao>

        <Cartao titulo="Métricas Principais (Prometheus)">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded border border-blue-100">
                <div className="text-sm text-blue-600 font-medium">Requisições Totais</div>
                <div className="text-2xl font-bold text-blue-900">{metrics?.totalRequests || 0}</div>
              </div>
              <div className="p-4 bg-red-50 rounded border border-red-100">
                <div className="text-sm text-red-600 font-medium">Taxa de Erro (4xx/5xx)</div>
                <div className="text-2xl font-bold text-red-900">{metrics?.errorRate.toFixed(2)}%</div>
              </div>
              <div className="p-4 bg-yellow-50 rounded border border-yellow-100">
                <div className="text-sm text-yellow-600 font-medium">Filas de Background</div>
                <div className="text-2xl font-bold text-yellow-900">{metrics?.activeTasks || 0}</div>
              </div>
              <div className="p-4 bg-purple-50 rounded border border-purple-100">
                <div className="text-sm text-purple-600 font-medium">Conexões DB (Est.)</div>
                <div className="text-2xl font-bold text-purple-900">{metrics?.dbConnections || 0}</div>
              </div>
            </div>
          </div>
        </Cartao>
      </div>
    </div>
  )
}
