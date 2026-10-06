// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.


export interface CloudPosture {
  aws_issues: number;
  gcp_issues: number;
  azure_issues: number;
  compliance_score: number;
}
/**
 * Tipos que espelham os schemas do backend.
 *
 * Os slugs (`producao`, `critico`) são o que trafega na API e serve para
 * filtrar; os campos `*_label` trazem o texto acentuado pronto para exibir, o
 * que evita manter aqui uma tabela de tradução que sairia de sincronia.
 */

export type Ambiente = 'producao' | 'homologacao' | 'teste'
export type Exposicao = 'internet' | 'interna'
export type Importancia = 'alta' | 'media' | 'baixa'
export type Ferramenta = 'semgrep' | 'nuclei' | 'trivy' | 'gitleaks'
export type Risco = 'critico' | 'alto' | 'medio' | 'baixo'
export type StatusVulnerabilidade =
  | 'nova'
  | 'em_analise'
  | 'em_correcao'
  | 'aguardando_validacao'
  | 'corrigida'
  | 'falso_positivo'
  | 'aceito_como_risco'
  | 'excecao_temporaria'
  | 'duplicado'

export interface Usuario {
  id: number
  email: string
  nome: string
  criado_em: string
  role: string
  permissions: string[]
  tenants?: { id: number; name: string }[]
}

export interface RespostaLogin {
  access_token: string
  token_type: string
  usuario: Usuario
}

export interface Aplicacao {
  id: number
  nome: string
  responsavel: string
  url: string | null
  ambiente: Ambiente
  exposicao: Exposicao
  importancia: Importancia
  ambiente_label: string
  exposicao_label: string
  importancia_label: string
  criado_em: string
  atualizado_em: string
}

export interface AplicacaoNaLista extends Aplicacao {
  total_vulnerabilidades: number
  total_criticas: number
  total_abertas: number
}

export interface NovaAplicacao {
  nome: string
  responsavel: string
  ambiente: Ambiente
  exposicao: Exposicao
  importancia: Importancia
  url?: string | null
}

export interface Achado {
  id: number
  origem: Ferramenta
  origem_label: string
  severidade: string
  mensagem: string
  regra_id: string
  arquivo: string | null
  linha: number | null
  cwe: string | null
  url: string | null
  http_status: number | null
  evidencia: string | null
  repository: string | null
  commit: string | null
  fingerprint: string | null
  resource: string | null
  resource_type: string | null
  iac_provider: string | null
  framework: string | null
  guideline: string | null
  
  // Runtime / eBPF
  process_name?: string | null
  pid?: number | null
  syscall?: string | null
  container_id?: string | null
  hit_count?: number
  last_seen_at?: string | null

  // Container
  layer?: string | null
  pacote?: string | null
  versao?: string | null
  versao_corrigida?: string | null
  image_name?: string | null
  image_repository?: string | null
  image_tag?: string | null
  image_digest?: string | null
  os?: string | null
  architecture?: string | null
  registry_name?: string | null
  base_image?: string | null
}

export interface AnaliseIA {
  explicacao: string | null
  impacto: string | null
  priorizacao: string | null
  sugestao: string | null
  validacao: string | null
  descricao_ticket: string | null
  gerada_em: string | null
}

export interface ItemHistorico {
  id: number
  status_anterior: StatusVulnerabilidade | null
  status_novo: StatusVulnerabilidade
  status_anterior_label: string | null
  status_novo_label: string
  comentario: string | null
  criado_em: string
  usuario_nome: string | null
}

export interface SlaResponse {
  status: string
  status_label: string
  due_at: string | null
  dias_restantes: number | null
  dias_em_atraso: number | null
  idade_em_dias: number
}

export interface Vulnerabilidade {
  id: number
  aplicacao_id: number
  aplicacao_nome: string
  aplicacao_ambiente: string
  tipo_vuln: string
  endpoint: string
  correlacionada: boolean
  encontrada_semgrep: boolean
  confirmada_nuclei: boolean
  origens: string[]
  risco: Risco
  risco_label: string
  severidade_original: string | null
  status: StatusVulnerabilidade
  status_label: string
  tem_analise_ia: boolean
  sla?: SlaResponse
  identificada_em: string
}

export interface VulnerabilidadeDetalhe extends Vulnerabilidade {
  justificativa: string
  atualizada_em: string
  achados: Achado[]
  analise_ia: AnaliseIA | null
  historico: ItemHistorico[]
  tickets: TicketResumo[]
  
  // Remediation
  owner_id: number | null
  owner_team: string | null
  assigned_at: string | null
  due_at: string | null
  resolved_at: string | null
  false_positive_reason: string | null
  risk_acceptance_reason: string | null
  risk_acceptance_approver_id: number | null
  risk_accepted_at: string | null
  
  comments: RemediationComment[]
  evidences: RemediationEvidence[]
}

export interface RemediationComment {
  id: number
  vulnerability_id: number
  author_id: number | null
  author_name: string | null
  content: string
  created_at: string
}

export interface RemediationEvidence {
  id: number
  vulnerability_id: number
  author_id: number | null
  author_name: string | null
  evidence_type: string
  description: string
  reference: string | null
  created_at: string
}

export interface ResultadoUpload {
  upload_id: number
  ferramenta: Ferramenta
  ferramenta_label: string
  achados_lidos: number
  achados_ignorados: number
  avisos: string[]
  vulnerabilidades_totais: number
  vulnerabilidades_novas: number
  vulnerabilidades_atualizadas: number
}

export interface UploadResumo {
  id: number
  ferramenta: Ferramenta
  ferramenta_label: string
  nome_arquivo: string
  tamanho_bytes: number
  total_achados: number
  total_ignorados: number
  criado_em: string
  tenants?: { id: number; name: string }[]
}

export interface Contagem {
  valor: string
  label: string
  total: number
}

export interface AplicacaoEmRisco {
  id: number
  nome: string
  ambiente: string
  exposicao: string
  criticas: number
  altas: number
  medias: number
  baixas: number
  total: number
  pontuacao: number
}

export type TicketProvider = 'jira' | 'github' | 'gitlab' | 'azure_devops'

export interface TicketResumo {
  id: number
  provider: TicketProvider
  external_id: string
  external_key: string | null
  url: string
  title: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  created_at: string
  updated_at: string
  last_synced_at: string | null
}

export interface Dashboard {
  total_aplicacoes: number
  total_vulnerabilidades: number
  total_criticas: number
  total_em_correcao: number
  total_abertas: number
  total_corrigidas: number
  por_risco: Contagem[]
  por_status: Contagem[]
  aplicacoes_em_risco: AplicacaoEmRisco[];
  cloud_posture: CloudPosture;
}

export interface Opcao {
  valor: string
  label: string
}

export interface Opcoes {
  ambientes: Opcao[]
  exposicoes: Opcao[]
  importancias: Opcao[]
  riscos: Opcao[]
  status: Opcao[]
}

export interface FiltrosVulnerabilidade {
  aplicacao_id?: number
  risco?: Risco
  status?: StatusVulnerabilidade
  tipo_vuln?: string
  apenas_correlacionadas?: boolean
}

// ---------------------------------------------------------------------------
// CI/CD Security Gates
// ---------------------------------------------------------------------------

export type GateDecision = 'pass' | 'warn' | 'block'

export interface PolicyViolation {
  policy_id: number
  policy_nome: string
  acao: GateDecision
  vulnerabilidade_id: number
  vulnerabilidade_tipo: string
  risco: Risco
}

export interface GateResult {
  id: number
  pipeline_run_id: number
  decision: GateDecision
  reason: string
  total_findings: number
  total_violations: number
  avaliado_em: string
}

export interface PipelineRun {
  id: number
  aplicacao_id: number
  provider: string | null
  pipeline_id: string | null
  commit_sha: string | null
  branch: string | null
  ambiente: string | null
  criado_em: string
  ultimo_resultado: GateResult | null
}

export interface Policy {
  id: number
  nome: string
  descricao: string | null
  aplicacao_id: number | null
  risco_minimo: Risco
  acao: GateDecision
  ativa: boolean
  criada_em: string
}

export interface PolicyException {
  id: number
  policy_id: number
  vulnerabilidade_id: number
  justificativa: string
  expira_em: string | null
  valida: boolean
  criada_em: string
}

export interface CiCheckResponse {
  decision: GateDecision
  decision_label: string
  reason: string
  policy_violations: PolicyViolation[]
  findings: number[]
  total_findings: number
  total_violations: number
  gate_result_id: number
  pipeline_run_id: number
}
