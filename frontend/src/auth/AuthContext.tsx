// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * AuthContext.tsx — Sessão do usuário.
 *
 * Guarda o token no localStorage para a sessão sobreviver a um recarregamento,
 * e revalida contra a API na inicialização: um token guardado pode ter expirado
 * enquanto a aba estava fechada.
 */
import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import {
  EVENTO_SESSAO_EXPIRADA,
  entrar as apiEntrar,
  guardarToken,
  lerToken,
  usuarioAtual,
} from '../api/client'
import type { Usuario } from '../api/types'

interface EstadoAutenticacao {
  usuario: Usuario | null
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<void>
  sair: () => void
  tenantId: string | null
  setTenantId: (id: string) => void
}

export const AuthContext = createContext<EstadoAutenticacao | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  // Começa carregando quando há token guardado: enquanto a validação não
  // termina, mostrar o login faria a tela piscar para quem já estava logado.
  const [carregando, setCarregando] = useState(() => Boolean(lerToken()))
  const [tenantId, setTenantIdState] = useState(() => localStorage.getItem('@pride:tenant_id'))

  const setTenantId = useCallback((id: string) => {
    localStorage.setItem('@pride:tenant_id', id)
    setTenantIdState(id)
    window.location.reload() // Reload to fetch fresh data for the new tenant
  }, [])

  useEffect(() => {
    if (!lerToken()) {
      setCarregando(false)
      return
    }

    let cancelado = false
    usuarioAtual()
      .then((dados) => {
        if (!cancelado) {
          setUsuario(dados)
          if (dados.tenants?.length && !localStorage.getItem('@pride:tenant_id')) {
            localStorage.setItem('@pride:tenant_id', dados.tenants[0].id.toString())
            setTenantIdState(dados.tenants[0].id.toString())
          }
        }
      })
      .catch(() => {
        guardarToken(null)
        if (!cancelado) setUsuario(null)
      })
      .finally(() => {
        if (!cancelado) setCarregando(false)
      })

    return () => {
      cancelado = true
    }
  }, [])

  useEffect(() => {
    // O interceptor do axios avisa quando a API recusa o token em qualquer tela
    const aoExpirar = () => setUsuario(null)
    window.addEventListener(EVENTO_SESSAO_EXPIRADA, aoExpirar)
    return () => window.removeEventListener(EVENTO_SESSAO_EXPIRADA, aoExpirar)
  }, [])

  const entrar = useCallback(async (email: string, senha: string) => {
    const resposta = await apiEntrar(email, senha)
    guardarToken(resposta.access_token)
    if (resposta.usuario.tenants?.length) {
      localStorage.setItem('@pride:tenant_id', resposta.usuario.tenants[0].id.toString())
      setTenantIdState(resposta.usuario.tenants[0].id.toString())
    }
    setUsuario(resposta.usuario)
  }, [])

  const sair = useCallback(() => {
    guardarToken(null)
    setUsuario(null)
    localStorage.removeItem('@pride:tenant_id')
    setTenantIdState(null)
  }, [])

  const valor = useMemo(
    () => ({ usuario, carregando, entrar, sair, tenantId, setTenantId }),
    [usuario, carregando, entrar, sair, tenantId, setTenantId],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
