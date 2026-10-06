// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * utilitarios.tsx — Renderização das telas nos testes.
 *
 * Toda tela deste projeto depende do React Router (usa `Link`, `useParams` ou
 * `useSearchParams`). Renderizá-las sem roteador quebra por um motivo que não
 * tem nada a ver com o AC sendo verificado.
 */
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AuthContext } from '../auth/AuthContext'
import { USUARIO } from './dados'

/** Renderiza a tela dentro de um roteador em memória. */
export function renderizar(elemento: ReactElement, rotaInicial = '/') {
  const authValue = { usuario: USUARIO, carregando: false, entrar: async () => {}, sair: () => {}, tenantId: "1", setTenantId: () => {} }
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={[rotaInicial]}>{elemento}</MemoryRouter>
    </AuthContext.Provider>
  )
}

/**
 * Renderiza uma tela que lê parâmetros da rota.
 *
 * Usada pelo detalhe da vulnerabilidade, que descobre qual carregar pelo `:id`.
 */
export function renderizarEmRota(
  elemento: ReactElement,
  padrao: string,
  rotaInicial: string,
) {
  const authValue = { usuario: USUARIO, carregando: false, entrar: async () => {}, sair: () => {}, tenantId: "1", setTenantId: () => {} }
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={[rotaInicial]}>
        <Routes>
          <Route path={padrao} element={elemento} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}
