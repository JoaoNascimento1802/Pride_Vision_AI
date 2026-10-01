/**
 * TenantAdmin.tsx — Painel de administração de Workspaces/Tenants.
 *
 * Acesso restrito a usuários com role ADMIN. Exibe os tenants cadastrados,
 * usuários associados e configuração de SSO Corporativo.
 */
import { useState } from 'react'

import { listarTenants, listarUsuariosTenant } from '../api/client'
import type { TenantInfo, TenantUserInfo } from '../api/client'

import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'
import { useAuth } from '../auth/useAuth'

function BadgeRole({ role }: { role: string }) {
  const cls =
    role === 'admin'
      ? 'bg-violet-100 text-violet-800 ring-violet-300'
      : role === 'developer'
        ? 'bg-sky-100 text-sky-800 ring-sky-300'
        : 'bg-slate-100 text-slate-700 ring-slate-300'
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold uppercase ring-1 ring-inset ${cls}`}>
      {role}
    </span>
  )
}

function PainelUsuariosTenant({ tenant }: { tenant: TenantInfo }) {
  const { dados, carregando, erro } = useRequisicao(
    () => listarUsuariosTenant(tenant.id),
    [tenant.id],
  )

  return (
    <div className="mt-3">
      {carregando && <div className="text-xs text-slate-400">Carregando usuários...</div>}
      {erro && <div className="text-xs text-red-500">{erro}</div>}
      {!carregando && !erro && (
        dados && dados.length > 0 ? (
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="py-1.5 text-left text-xs font-semibold text-slate-500">Usuário</th>
                <th className="py-1.5 text-left text-xs font-semibold text-slate-500">E-mail</th>
                <th className="py-1.5 text-left text-xs font-semibold text-slate-500">Role</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {dados.map((u: TenantUserInfo) => (
                <tr key={u.user_id}>
                  <td className="py-1.5 font-medium text-slate-800">{u.nome}</td>
                  <td className="py-1.5 text-slate-500">{u.email}</td>
                  <td className="py-1.5"><BadgeRole role={u.role} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-xs text-slate-400 italic">Nenhum usuário associado a este workspace.</div>
        )
      )}
    </div>
  )
}

function CardTenant({ tenant }: { tenant: TenantInfo }) {
  const [expandido, setExpandido] = useState(false)

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base font-semibold text-slate-900">{tenant.name}</span>
            <span className="text-xs text-slate-400">#{tenant.id}</span>
          </div>
          {tenant.domain && (
            <div className="mt-0.5 text-xs text-slate-500">
              🌐 <span className="font-mono">{tenant.domain}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          {tenant.sso_config && (
            <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700 ring-1 ring-green-300">
              ✓ SSO Configurado
            </span>
          )}
          <button
            onClick={() => setExpandido((v) => !v)}
            className="rounded-md border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            {expandido ? 'Recolher' : 'Ver usuários'}
          </button>
        </div>
      </div>

      {tenant.sso_config && (
        <div className="mt-3 rounded-md bg-slate-50 p-3">
          <div className="mb-1 text-xs font-semibold text-slate-500 uppercase tracking-wide">Configuração SSO (OIDC)</div>
          <div className="space-y-1 text-xs font-mono text-slate-600">
            {Object.entries(tenant.sso_config).map(([k, v]) => (
              <div key={k}>
                <span className="text-slate-400">{k}:</span>{' '}
                <span>{k.toLowerCase().includes('secret') ? '••••••••' : String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {expandido && <PainelUsuariosTenant tenant={tenant} />}
    </div>
  )
}

export function TenantAdmin() {
  const { usuario } = useAuth()

  if (usuario?.role !== 'admin') {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center">
        <div className="text-3xl mb-2">🔒</div>
        <div className="font-semibold text-red-800">Acesso restrito a Administradores</div>
        <div className="mt-1 text-sm text-red-600">
          Você precisa da role <strong>admin</strong> para acessar o painel de Tenant Admin.
        </div>
      </div>
    )
  }

  const { dados, carregando, erro, recarregar } = useRequisicao(listarTenants, [])

  return (
    <>
      <TituloDaPagina
        titulo="Tenant Admin"
        descricao="Gerenciamento de Workspaces (Tenants), usuários associados e configuração de SSO Corporativo."
        acao={
          <button
            onClick={recarregar}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50"
          >
            ↺ Atualizar
          </button>
        }
      />

      {carregando && <Carregando />}
      {erro && <Erro mensagem={erro} />}

      {!carregando && !erro && (
        dados && (dados as TenantInfo[]).length > 0 ? (
          <div className="space-y-4">
            {(dados as TenantInfo[]).map((t: TenantInfo) => (
              <CardTenant key={t.id} tenant={t} />
            ))}
          </div>
        ) : (
          <Vazio titulo="Nenhum workspace encontrado" descricao="Nenhum tenant cadastrado no sistema." />
        )
      )}
    </>
  )
}

