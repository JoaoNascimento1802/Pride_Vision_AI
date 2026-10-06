// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * App.tsx — Rotas da aplicação.
 *
 * Tudo fica atrás do login: a plataforma trata dados de segurança, e não há
 * tela que faça sentido expor sem autenticação.
 */
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { Carregando } from './components/Feedback'
import { Layout } from './components/Layout'
import { Aplicacoes } from './pages/Aplicacoes'
import { CiCdSecurity } from './pages/CiCdSecurity'
import { Dashboard } from './pages/Dashboard'
import { DetalheVulnerabilidade } from './pages/DetalheVulnerabilidade'
import { Login } from './pages/Login'
import { Vulnerabilidades } from './pages/Vulnerabilidades'
import Integracoes from './pages/Integracoes'
import { Auditoria } from './pages/Auditoria'
import { Observability } from './pages/Observability'
import { CloudCspm } from './pages/CloudCspm'
import { RuntimeSecurity } from './pages/RuntimeSecurity'
import { TenantAdmin } from './pages/TenantAdmin'
import { SbomVisualizer } from './pages/SbomVisualizer'

function Rotas() {
  const { usuario, carregando } = useAuth()

  // Enquanto o token guardado é revalidado, mostrar o login faria a tela piscar
  // para quem já estava autenticado.
  if (carregando) {
    return <Carregando texto="Verificando sessão…" />
  }

  if (!usuario) {
    return (
      <Routes>
        <Route path="/entrar" element={<Login />} />
        <Route path="*" element={<Navigate to="/entrar" replace />} />
      </Routes>
    )
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/aplicacoes" element={<Aplicacoes />} />
        <Route path="/aplicacoes/:id/sboms" element={<SbomVisualizer />} />
        <Route path="/vulnerabilidades" element={<Vulnerabilidades />} />
        <Route path="/vulnerabilidades/:id" element={<DetalheVulnerabilidade />} />
        <Route path="/ci-seguranca" element={<CiCdSecurity />} />
        <Route path="/integracoes" element={<Integracoes />} />
        <Route path="/auditoria" element={<Auditoria />} />
        <Route path="/observabilidade" element={<Observability />} />
        <Route path="/cloud-cspm" element={<CloudCspm />} />
        <Route path="/runtime-security" element={<RuntimeSecurity />} />
        <Route path="/admin/tenants" element={<TenantAdmin />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Rotas />
      </AuthProvider>
    </BrowserRouter>
  )
}

