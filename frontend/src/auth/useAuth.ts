import { useContext } from 'react'

import { AuthContext } from './AuthContext'

/** Acesso à sessão. Falha cedo se usado fora do provedor. */
export function useAuth() {
  const contexto = useContext(AuthContext)
  if (!contexto) {
    throw new Error('useAuth precisa estar dentro de <AuthProvider>.')
  }
  return contexto
}
