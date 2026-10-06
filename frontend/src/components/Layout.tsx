// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import { NavLink, Outlet } from 'react-router-dom'
import { LayoutDashboard, Shield, Activity, Layers, Lock, Settings, LogOut } from 'lucide-react'

import { useAuth } from '../auth/useAuth'

const ABAS = [
  { para: '/auditoria', rotulo: 'Auditoria', exato: false, permissao: 'audit:read', icon: Activity },
  { para: '/observabilidade', rotulo: 'System Health', exato: false, permissao: 'audit:read', icon: Settings },
  { para: '/', rotulo: 'Visão Geral', exato: true, icon: LayoutDashboard },
  { para: '/aplicacoes', rotulo: 'Aplicações', exato: false, icon: Layers },
  { para: '/vulnerabilidades', rotulo: 'Vulnerabilidades', exato: false, icon: Shield },
  { para: '/ci-seguranca', rotulo: 'CI/CD Security', exato: false, icon: Lock },
  { para: '/integracoes', rotulo: 'Integrações', exato: false, icon: Settings },
]

export function Layout() {
  const { usuario, sair, tenantId, setTenantId } = useAuth()

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-50">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col bg-slate-900 text-slate-300">
        <div className="flex h-16 items-center px-6 border-b border-slate-800">
          <span className="text-lg font-bold tracking-tight text-white">
            PRIDE <span className="text-indigo-500">Vision AI</span>
          </span>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
          {ABAS.filter(aba => !aba.permissao || usuario?.permissions.includes(aba.permissao)).map((aba) => {
            const Icon = aba.icon
            return (
              <NavLink
                key={aba.para}
                to={aba.para}
                end={aba.exato}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-indigo-600 text-white rounded-lg shadow-sm'
                      : 'hover:bg-slate-800 hover:text-white rounded-lg'
                  }`
                }
              >
                <Icon className="h-5 w-5" />
                {aba.rotulo}
              </NavLink>
            )
          })}
        </nav>
      </aside>

      {/* Main Column */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header */}
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-8 shadow-sm">
          <div className="flex items-center text-lg font-semibold text-slate-800">
             Painel de Controle
          </div>

          <div className="flex items-center gap-6">
            {usuario?.tenants && usuario.tenants.length > 1 && (
              <select
                value={tenantId || ''}
                onChange={(e) => setTenantId(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white py-1.5 pl-3 pr-8 text-sm text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                {usuario.tenants.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}
            
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-slate-700">{usuario?.nome}</span>
              <button
                type="button"
                onClick={sair}
                className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 transition-all duration-200 hover:bg-slate-100 hover:text-slate-900"
              >
                <LogOut className="h-4 w-4" />
                Sair
              </button>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 bg-slate-50 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export function TituloDaPagina({
  titulo,
  descricao,
  acao,
}: {
  titulo: React.ReactNode
  descricao?: string
  acao?: React.ReactNode
}) {
  return (
    <div className="mb-8 flex items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{titulo}</h1>
        {descricao && <p className="mt-2 text-sm text-slate-500">{descricao}</p>}
      </div>
      {acao && <div>{acao}</div>}
    </div>
  )
}
