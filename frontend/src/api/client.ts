/**
 * client.ts — Cliente HTTP e funções de acesso à API.
 *
 * Centraliza a base da URL, o envio do token e a tradução de erro em mensagem
 * legível. As telas chamam estas funções e nunca o axios diretamente.
 */
import axios, { AxiosError } from 'axios'

import type {
  Aplicacao,
  AplicacaoNaLista,
  CiCheckResponse,
  Dashboard,
  FiltrosVulnerabilidade,
  GateResult,
  NovaAplicacao,
  Opcoes,
  PipelineRun,
  Policy,
  PolicyException,
  RespostaLogin,
  ResultadoUpload,
  StatusVulnerabilidade,
  TicketProvider,
  TicketResumo,
  UploadResumo,
  Usuario,
  Vulnerabilidade,
  VulnerabilidadeDetalhe,
} from './types'

const CHAVE_TOKEN = 'pride.token'

export const http = axios.create({
  // Em desenvolvimento fica vazio e o proxy do Vite resolve; em produção
  // VITE_API_URL aponta para o backend publicado.
  baseURL: import.meta.env.VITE_API_URL ?? '',
})

http.interceptors.request.use((config) => {
  const token = lerToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const tenantId = localStorage.getItem('@pride:tenant_id')
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId
  }
  return config
})

/** Disparado quando a API recusa o token, para a aplicação voltar ao login. */
export const EVENTO_SESSAO_EXPIRADA = 'pride:sessao-expirada'

http.interceptors.response.use(
  (resposta) => resposta,
  (erro: AxiosError) => {
    if (erro.response?.status === 401) {
      // Um token expirado precisa derrubar a sessão em qualquer tela, não só na
      // que fez a chamada — daí o evento em vez de tratar caso a caso.
      guardarToken(null)
      window.dispatchEvent(new Event(EVENTO_SESSAO_EXPIRADA))
    }
    return Promise.reject(erro)
  },
)

export function lerToken(): string | null {
  return localStorage.getItem(CHAVE_TOKEN)
}

export function guardarToken(token: string | null): void {
  if (token) {
    localStorage.setItem(CHAVE_TOKEN, token)
  } else {
    localStorage.removeItem(CHAVE_TOKEN)
  }
}

/**
 * Extrai a mensagem que a API enviou.
 *
 * O FastAPI devolve `detail` como texto nos erros de negócio e como lista de
 * objetos nos erros de validação; os dois casos precisam virar frase.
 */
export function mensagemDeErro(erro: unknown, padrao = 'Algo deu errado.'): string {
  if (!axios.isAxiosError(erro)) {
    return erro instanceof Error ? erro.message : padrao
  }

  if (!erro.response) {
    return 'Não foi possível falar com o servidor. Ele está rodando?'
  }

  const detalhe = (erro.response.data as { detail?: unknown } | undefined)?.detail

  if (typeof detalhe === 'string') return detalhe

  if (Array.isArray(detalhe)) {
    const partes = detalhe
      .map((item) => {
        const erroValidacao = item as { loc?: unknown[]; msg?: string }
        const campo = erroValidacao.loc?.slice(1).join('.') ?? ''
        return campo ? `${campo}: ${erroValidacao.msg}` : erroValidacao.msg
      })
      .filter(Boolean)
    if (partes.length) return partes.join('; ')
  }

  return padrao
}

// ---------------------------------------------------------------------------
// Autenticação
// ---------------------------------------------------------------------------

export async function entrar(email: string, senha: string): Promise<RespostaLogin> {
  // A rota de login segue o padrão OAuth2 e espera formulário, não JSON
  const corpo = new URLSearchParams({ username: email, password: senha })
  const { data } = await http.post<RespostaLogin>('/api/auth/login', corpo)
  return data
}

export async function registrar(
  email: string,
  nome: string,
  senha: string,
): Promise<Usuario> {
  const { data } = await http.post<Usuario>('/api/auth/registrar', { email, nome, senha })
  return data
}

export async function usuarioAtual(): Promise<Usuario> {
  const { data } = await http.get<Usuario>('/api/auth/eu')
  return data
}

// ---------------------------------------------------------------------------
// Aplicações
// ---------------------------------------------------------------------------

export async function listarAplicacoes(): Promise<AplicacaoNaLista[]> {
  const { data } = await http.get<AplicacaoNaLista[]>('/api/aplicacoes')
  return data
}

export async function obterAplicacao(id: number): Promise<Aplicacao> {
  const { data } = await http.get<Aplicacao>(`/api/aplicacoes/${id}`)
  return data
}

export async function criarAplicacao(dados: NovaAplicacao): Promise<Aplicacao> {
  const { data } = await http.post<Aplicacao>('/api/aplicacoes', dados)
  return data
}

export async function atualizarAplicacao(
  id: number,
  dados: Partial<NovaAplicacao>,
): Promise<Aplicacao> {
  const { data } = await http.patch<Aplicacao>(`/api/aplicacoes/${id}`, dados)
  return data
}

export async function removerAplicacao(id: number): Promise<void> {
  await http.delete(`/api/aplicacoes/${id}`)
}

// ---------------------------------------------------------------------------
// Uploads
// ---------------------------------------------------------------------------

export async function enviarRelatorio(
  aplicacaoId: number,
  ferramenta: 'semgrep' | 'nuclei' | 'trivy' | 'gitleaks' | 'checkov',
  arquivo: File,
): Promise<ResultadoUpload> {
  const formulario = new FormData()
  formulario.append('arquivo', arquivo)
  const { data } = await http.post<ResultadoUpload>(
    `/api/aplicacoes/${aplicacaoId}/uploads/${ferramenta}`,
    formulario,
  )
  return data
}

export async function listarUploads(aplicacaoId: number): Promise<UploadResumo[]> {
  const { data } = await http.get<UploadResumo[]>(`/api/aplicacoes/${aplicacaoId}/uploads`)
  return data
}

export async function enviarSbom(aplicacaoId: number, arquivo: File): Promise<any> {
  const formulario = new FormData()
  formulario.append('arquivo', arquivo)
  const { data } = await http.post(`/api/aplicacoes/${aplicacaoId}/sboms/import`, formulario)
  return data
}

// ---------------------------------------------------------------------------
// Vulnerabilidades
// ---------------------------------------------------------------------------

export async function listarVulnerabilidades(
  filtros: FiltrosVulnerabilidade = {},
): Promise<Vulnerabilidade[]> {
  const { data } = await http.get<Vulnerabilidade[]>('/api/vulnerabilidades', {
    params: filtros,
  })
  return data
}

export async function obterVulnerabilidade(id: number): Promise<VulnerabilidadeDetalhe> {
  const { data } = await http.get<VulnerabilidadeDetalhe>(`/api/vulnerabilidades/${id}`)
  return data
}

export async function mudarStatus(
  id: number,
  status: StatusVulnerabilidade,
  comentario?: string,
  reason?: string,
): Promise<VulnerabilidadeDetalhe> {
  const { data } = await http.patch<VulnerabilidadeDetalhe>(
    `/api/vulnerabilidades/${id}/status`,
    { status, comentario: comentario || null, reason: reason || null },
  )
  return data
}

export async function gerarAnaliseIA(id: number): Promise<VulnerabilidadeDetalhe> {
  const { data } = await http.post<VulnerabilidadeDetalhe>(
    `/api/vulnerabilidades/${id}/analise`,
  )
  return data
}

// ---------------------------------------------------------------------------
// Dashboard e opções
// ---------------------------------------------------------------------------

export async function obterDashboard(): Promise<Dashboard> {
  const { data } = await http.get<Dashboard>('/api/dashboard')
  return data
}

export async function criarTicket(vulnerabilidadeId: number, provider: TicketProvider): Promise<TicketResumo> {
  const { data } = await http.post<TicketResumo>(`/api/vulnerabilidades/${vulnerabilidadeId}/tickets`, {
    provider
  })
  return data
}

export async function sincronizarTicket(vulnerabilidadeId: number, ticketId: number): Promise<TicketResumo> {
  const { data } = await http.post<TicketResumo>(`/api/vulnerabilidades/${vulnerabilidadeId}/tickets/${ticketId}/sync`)
  return data
}

export async function obterOpcoes(): Promise<Opcoes> {
  const { data } = await http.get<Opcoes>('/api/opcoes')
  return data
}

// ---------------------------------------------------------------------------
// CI/CD Security Gates
// ---------------------------------------------------------------------------

export async function listarPipelines(aplicacaoId?: number): Promise<PipelineRun[]> {
  const { data } = await http.get<PipelineRun[]>('/api/ci/pipelines', {
    params: aplicacaoId ? { aplicacao_id: aplicacaoId } : {},
  })
  return data
}

export async function listarGateResults(aplicacaoId?: number): Promise<GateResult[]> {
  const { data } = await http.get<GateResult[]>('/api/ci/gate-results', {
    params: aplicacaoId ? { aplicacao_id: aplicacaoId } : {},
  })
  return data
}

export async function listarPolicies(aplicacaoId?: number): Promise<Policy[]> {
  const { data } = await http.get<Policy[]>('/api/ci/policies', {
    params: aplicacaoId ? { aplicacao_id: aplicacaoId } : {},
  })
  return data
}

export async function criarPolicy(dados: {
  nome: string
  risco_minimo: string
  acao: string
  aplicacao_id?: number
  descricao?: string
}): Promise<Policy> {
  const { data } = await http.post<Policy>('/api/ci/policies', dados)
  return data
}

export async function desativarPolicy(id: number): Promise<void> {
  await http.delete(`/api/ci/policies/${id}`)
}

export async function listarExcecoes(vulnerabilidadeId?: number): Promise<PolicyException[]> {
  const { data } = await http.get<PolicyException[]>('/api/ci/exceptions', {
    params: vulnerabilidadeId ? { vulnerability_id: vulnerabilidadeId } : {},
  })
  return data
}

export async function executarCheck(dados: {
  application_id: number
  commit_sha?: string
  branch?: string
  environment?: string
  pipeline_id?: string
  provider?: string
  repository?: string
  pull_request_number?: number
}): Promise<CiCheckResponse> {
  const { data } = await http.post<CiCheckResponse>('/api/ci/check', dados)
  return data
}

export async function listarStatusIntegracoes(): Promise<{ github: string; gitlab: string }> {
  const { data } = await http.get<{ github: string; gitlab: string }>('/api/integrations/status')
  return data
}

export async function apiGetAuditLogs(skip = 0, limit = 20): Promise<{ items: any[], total: number }> {
  const resposta = await http.get(`/api/audit?skip=${skip}&limit=${limit}`)
  return resposta.data
}

// ---------------------------------------------------------------------------
// Remediation
// ---------------------------------------------------------------------------

export async function atribuirOwner(
  id: number,
  owner_id: number | null,
  owner_team: string | null = null,
): Promise<VulnerabilidadeDetalhe> {
  const { data } = await http.patch<VulnerabilidadeDetalhe>(`/api/vulnerabilidades/${id}/owner`, {
    owner_id,
    owner_team,
  })
  return data
}

export async function adicionarComentario(id: number, content: string): Promise<any> {
  const { data } = await http.post(`/api/vulnerabilidades/${id}/comments`, { content })
  return data
}

export async function listarComentarios(id: number): Promise<any[]> {
  const { data } = await http.get(`/api/vulnerabilidades/${id}/comments`)
  return data
}

export async function adicionarEvidencia(
  id: number,
  description: string,
  reference: string | null = null,
  evidence_type: string = 'other'
): Promise<any> {
  const { data } = await http.post(`/api/vulnerabilidades/${id}/evidences`, {
    description,
    reference,
    evidence_type
  })
  return data
}

export async function listarEvidencias(id: number): Promise<any[]> {
  const { data } = await http.get(`/api/vulnerabilidades/${id}/evidences`)
  return data
}

export async function obterVerificacoes(imageName: string): Promise<any[]> {
  const { data } = await http.get('/api/supply-chain/verifications?image_name=' + encodeURIComponent(imageName))
  return data
}

// ---------------------------------------------------------------------------
// Tenant Admin
// ---------------------------------------------------------------------------

export interface TenantInfo {
  id: number
  name: string
  domain: string | null
  sso_config: Record<string, string> | null
}

export interface TenantUserInfo {
  user_id: number
  email: string
  nome: string
  role: string
}

export async function listarTenants(): Promise<TenantInfo[]> {
  const { data } = await http.get<TenantInfo[]>('/api/auth/tenants')
  return data
}

export async function listarUsuariosTenant(tenantId: number): Promise<TenantUserInfo[]> {
  const { data } = await http.get<TenantUserInfo[]>(`/api/auth/tenants/${tenantId}/users`)
  return data
}