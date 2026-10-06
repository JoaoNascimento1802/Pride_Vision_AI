// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import { useEffect, useState } from 'react'
import { http } from '../api/client'
import { Activity, Database, Server, Brain, RefreshCw, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'

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
        http.get<string>('/api/metrics', { headers: { Accept: 'text/plain' } })
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
    return (
      <div className="flex items-center justify-center h-full p-6 text-slate-500">
        <RefreshCw className="w-6 h-6 mr-2 animate-spin text-indigo-600" />
        Carregando métricas...
      </div>
    )
  }

  const getStatusIcon = (status?: string) => {
    return status === 'ok' || status === 'up' ? (
      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
    ) : (
      <XCircle className="w-5 h-5 text-red-500" />
    )
  }

  const getStatusBadge = (status?: string) => {
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ">
        {getStatusIcon(status)}
        {status?.toUpperCase() || 'UNKNOWN'}
      </span>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 bg-slate-50 min-h-screen">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-7 h-7 text-indigo-600" />
            Visão Geral do Sistema (Observability)
          </h1>
          <p className="text-slate-500 mt-1">Métricas e saúde dos serviços em tempo real</p>
        </div>
        <button 
          onClick={carregar} 
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg transition-all duration-200 hover:bg-indigo-700 hover:shadow-md font-medium text-sm"
        >
          <RefreshCw className="w-4 h-4" />
          Atualizar
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50">
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Server className="w-5 h-5 text-indigo-600" />
              Deep Health Check
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3.5 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-slate-400" />
                  <span className="font-medium text-slate-700">Status Geral</span>
                </div>
                {getStatusBadge(health?.status)}
              </div>
              
              <div className="flex justify-between items-center p-3.5 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-slate-400" />
                  <span className="font-medium text-slate-700">Banco de Dados</span>
                </div>
                {getStatusBadge(health?.database)}
              </div>
              
              <div className="flex justify-between items-center p-3.5 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <Server className="w-5 h-5 text-slate-400" />
                  <span className="font-medium text-slate-700">Integração Jira</span>
                </div>
                {getStatusBadge(health?.services?.jira)}
              </div>
              
              <div className="flex justify-between items-center p-3.5 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <Brain className="w-5 h-5 text-slate-400" />
                  <span className="font-medium text-slate-700">Motor GenAI</span>
                </div>
                {getStatusBadge(health?.services?.genai)}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50">
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              Métricas Principais (Prometheus)
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-2 mb-2 text-indigo-600">
                  <Activity className="w-4 h-4" />
                  <span className="text-sm font-semibold">Requisições Totais</span>
                </div>
                <div className="text-3xl font-bold text-slate-800">{metrics?.totalRequests || 0}</div>
              </div>
              
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-2 mb-2 text-red-600">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm font-semibold">Taxa de Erro (4xx/5xx)</span>
                </div>
                <div className="text-3xl font-bold text-slate-800">{metrics?.errorRate.toFixed(2)}%</div>
              </div>
              
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-2 mb-2 text-amber-600">
                  <Activity className="w-4 h-4" />
                  <span className="text-sm font-semibold">Filas de Background</span>
                </div>
                <div className="text-3xl font-bold text-slate-800">{metrics?.activeTasks || 0}</div>
              </div>
              
              <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-2 mb-2 text-purple-600">
                  <Database className="w-4 h-4" />
                  <span className="text-sm font-semibold">Conexões DB (Est.)</span>
                </div>
                <div className="text-3xl font-bold text-slate-800">{metrics?.dbConnections || 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

