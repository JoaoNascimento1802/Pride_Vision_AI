// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * TenantAdmin.tsx — Painel de administração de Workspaces/Tenants.
 *
 * Acesso restrito a usuários com role ADMIN. Exibe os tenants cadastrados,
 * usuários associados e configuração de SSO Corporativo.
 */
import { useState } from 'react'
import { Users, Lock, Globe, Building2, ChevronDown, ChevronUp, RefreshCw, Mail, Shield } from 'lucide-react'

import { listarTenants, listarUsuariosTenant } from '../api/client'
import type { TenantInfo, TenantUserInfo } from '../api/client'

import { Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'
import { useAuth } from '../auth/useAuth'

function BadgeRole({ role }: { role: string }) {
  const cls =
    role === 'admin'
      ? 'bg-indigo-100 text-indigo-800 ring-indigo-300'
      : role === 'developer'
        ? 'bg-sky-100 text-sky-800 ring-sky-300'
        : 'bg-slate-100 text-slate-700 ring-slate-300'
  return (
    <span className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold uppercase ring-1 ring-inset ${cls}`}>
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
    <div className="mt-6 border-t border-slate-100 pt-4">
      <h4 className="mb-4 text-sm font-semibold text-slate-800 flex items-center gap-2">
        <Users className="h-4 w-4 text-slate-500" />
        Usuários Associados
      </h4>
      {carregando && <div className="text-sm text-slate-500 animate-pulse">Carregando usuários...</div>}
      {erro && <div className="text-sm text-red-500">{erro}</div>}
      {!carregando && !erro && (
        dados && dados.length > 0 ? (
          <div className="overflow-hidden rounded-lg border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold text-slate-800">Usuário</th>
                  <th className="px-6 py-3 text-left font-semibold text-slate-800">E-mail</th>
                  <th className="px-6 py-3 text-left font-semibold text-slate-800">Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {dados.map((u: TenantUserInfo) => (
                  <tr key={u.user_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3 font-medium text-slate-800">{u.nome}</td>
                    <td className="px-6 py-3 text-slate-500 flex items-center gap-2">
                      <Mail className="h-4 w-4 text-slate-400" />
                      {u.email}
                    </td>
                    <td className="px-6 py-3"><BadgeRole role={u.role} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-sm text-slate-500 italic bg-slate-50 p-4 rounded-lg border border-slate-100">Nenhum usuário associado a este workspace.</div>
        )
      )}
    </div>
  )
}

function CardTenant({ tenant }: { tenant: TenantInfo }) {
  const [expandido, setExpandido] = useState(false)

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <span className="text-lg font-bold text-slate-900">{tenant.name}</span>
              <span className="ml-2 text-xs font-mono text-slate-400">#{tenant.id}</span>
            </div>
          </div>
          {tenant.domain && (
            <div className="mt-2 flex items-center gap-1.5 text-sm text-slate-600 ml-11">
              <Globe className="h-4 w-4 text-slate-400" />
              <span className="font-medium">{tenant.domain}</span>
            </div>
          )}
        </div>
        <div className="flex flex-col items-end gap-3">
          {tenant.sso_config && (
            <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-2.5 py-1 text-xs font-bold text-green-700 ring-1 ring-green-200">
              <Shield className="h-3.5 w-3.5" /> SSO Configurado
            </span>
          )}
          <button
            onClick={() => setExpandido((v) => !v)}
            className="flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-indigo-600 transition-colors"
          >
            {expandido ? (
              <>Recolher <ChevronUp className="h-4 w-4" /></>
            ) : (
              <>Ver usuários <ChevronDown className="h-4 w-4" /></>
            )}
          </button>
        </div>
      </div>

      {tenant.sso_config && (
        <div className="mt-5 rounded-lg bg-slate-50 border border-slate-100 p-4">
          <div className="mb-3 text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
            <Lock className="h-4 w-4" />
            Configurações SSO (OIDC)
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm font-mono text-slate-600">
            {Object.entries(tenant.sso_config).map(([k, v]) => (
              <div key={k} className="flex flex-col bg-white p-2 rounded border border-slate-100">
                <span className="text-xs font-bold text-slate-400 mb-1">{k}</span>
                <span className="truncate" title={String(v)}>
                  {k.toLowerCase().includes('secret') ? '••••••••' : String(v)}
                </span>
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
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="rounded-xl border border-red-200 bg-red-50 p-10 text-center max-w-md shadow-sm">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100 mb-4">
            <Lock className="h-8 w-8 text-red-600" />
          </div>
          <div className="text-xl font-bold text-red-800 mb-2">Acesso restrito</div>
          <div className="text-sm text-red-600">
            Você precisa da função <strong>admin</strong> para acessar as configurações do Tenant.
          </div>
        </div>
      </div>
    )
  }

  const { dados, carregando, erro, recarregar } = useRequisicao(listarTenants, [])

  return (
    <div className="bg-slate-50 min-h-screen">
      <TituloDaPagina
        titulo={
          <span className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-indigo-600" />
            Tenant Admin
          </span>
        }
        descricao="Gerenciamento de Workspaces (Tenants), usuários associados e configurações de SSO Corporativo."
        acao={
          <button
            onClick={recarregar}
            className="flex items-center gap-2 transition-all duration-200 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 hover:shadow-md"
          >
            <RefreshCw className="h-4 w-4" /> Atualizar
          </button>
        }
      />

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {carregando && <Carregando />}
        {erro && <Erro mensagem={erro} />}

        {!carregando && !erro && (
          dados && (dados as TenantInfo[]).length > 0 ? (
            <div className="space-y-6">
              {(dados as TenantInfo[]).map((t: TenantInfo) => (
                <CardTenant key={t.id} tenant={t} />
              ))}
            </div>
          ) : (
            <Vazio titulo="Nenhum workspace encontrado" descricao="Nenhum tenant cadastrado no sistema." />
          )
        )}
      </div>
    </div>
  )
}
