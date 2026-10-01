/**
 * Layout.tsx — Moldura das telas autenticadas: navegação e cabeçalho.
 */
import { NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'

const ABAS = [
  { para: '/auditoria', rotulo: 'Auditoria', exato: false, permissao: 'audit:read' },
  { para: '/observabilidade', rotulo: 'System Health', exato: false, permissao: 'audit:read' },
  { para: '/', rotulo: 'Visão geral', exato: true },
  { para: '/aplicacoes', rotulo: 'Aplicações', exato: false },
  { para: '/vulnerabilidades', rotulo: 'Vulnerabilidades', exato: false },
  { para: '/ci-seguranca', rotulo: 'CI/CD Security', exato: false },
  { para: '/integracoes', rotulo: 'Integrações', exato: false },
]

export function Layout() {
  const { usuario, sair, tenantId, setTenantId } = useAuth()

  return (
    <div className="min-h-full">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-8">
            <span className="text-sm font-bold tracking-tight text-slate-900">
              PRIDE <span className="text-violet-600">Vision AI</span>
            </span>

            <nav className="flex gap-1">
              {ABAS.filter(aba => !aba.permissao || usuario?.permissions.includes(aba.permissao)).map((aba) => (
                <NavLink
                  key={aba.para}
                  to={aba.para}
                  end={aba.exato}
                  className={({ isActive }) =>
                    `rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      isActive
                        ? 'bg-violet-50 text-violet-700'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`
                  }
                >
                  {aba.rotulo}
                </NavLink>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-3 text-sm">
            {usuario?.tenants && usuario.tenants.length > 1 && (
              <select
                value={tenantId || ''}
                onChange={(e) => setTenantId(e.target.value)}
                className="rounded-md border-slate-300 py-1 pl-3 pr-8 text-sm focus:border-violet-500 focus:outline-none focus:ring-violet-500"
              >
                {usuario.tenants.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}
            <span className="text-slate-600">{usuario?.nome}</span>
            <button
              type="button"
              onClick={sair}
              className="rounded-md px-2 py-1 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}

export function TituloDaPagina({
  titulo,
  descricao,
  acao,
}: {
  titulo: string
  descricao?: string
  acao?: React.ReactNode
}) {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">{titulo}</h1>
        {descricao && <p className="mt-1 text-sm text-slate-500">{descricao}</p>}
      </div>
      {acao}
    </div>
  )
}


