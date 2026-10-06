// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * dados.ts — Respostas de exemplo da API, para os testes de tela.
 *
 * Espelham o formato real do backend. Dados fictícios: `demo.target.com` não
 * existe e nenhum valor aqui corresponde a sistema real.
 */
import type {
  AplicacaoNaLista,
  Dashboard,
  Opcoes,
  UploadResumo,
  Usuario,
  Vulnerabilidade,
  VulnerabilidadeDetalhe,
} from '../api/types'

export const USUARIO: Usuario = {
  id: 1,
  email: 'ana@exemplo.com',
  nome: 'Ana Souza',
  criado_em: '2026-01-10T09:00:00',
  role: 'admin',
  permissions: ['application:read', 'application:write', 'finding:read', 'finding:write', 'finding:close', 'ticket:read', 'ticket:create', 'ticket:sync', 'upload:create', 'policy:read', 'policy:write', 'exception:read', 'exception:write'],
}

export const DASHBOARD: Dashboard = {
  total_aplicacoes: 3,
  total_vulnerabilidades: 17,
  total_criticas: 4,
  total_em_correcao: 2,
  total_abertas: 15,
  total_corrigidas: 2,
  por_risco: [
    { valor: 'critico', label: 'Crítico', total: 4 },
    { valor: 'alto', label: 'Alto', total: 6 },
    { valor: 'medio', label: 'Médio', total: 5 },
    { valor: 'baixo', label: 'Baixo', total: 2 },
  ],
  por_status: [
    { valor: 'nova', label: 'Nova', total: 10 },
    { valor: 'em_analise', label: 'Em análise', total: 3 },
    { valor: 'em_correcao', label: 'Em correção', total: 2 },
    { valor: 'corrigida', label: 'Corrigida', total: 2 },
    { valor: 'falso_positivo', label: 'Falso positivo', total: 0 },
  ],
  cloud_posture: { aws_issues: 2, gcp_issues: 0, azure_issues: 0, compliance_score: 85 },
  aplicacoes_em_risco: [
    {
      id: 1,
      nome: 'Portal do Cliente',
      ambiente: 'Produção',
      exposicao: 'Internet',
      criticas: 4,
      altas: 3,
      medias: 3,
      baixas: 2,
      total: 12,
      pontuacao: 460,
    },
  ],
}

export const DASHBOARD_VAZIO: Dashboard = {
  total_aplicacoes: 0,
  total_vulnerabilidades: 0,
  total_criticas: 0,
  total_em_correcao: 0,
  total_abertas: 0,
  total_corrigidas: 0,
  por_risco: DASHBOARD.por_risco.map((item) => ({ ...item, total: 0 })),
  por_status: DASHBOARD.por_status.map((item) => ({ ...item, total: 0 })),
  aplicacoes_em_risco: [],
  cloud_posture: { aws_issues: 0, gcp_issues: 0, azure_issues: 0, compliance_score: 100 }
}

export const APLICACAO: AplicacaoNaLista = {
  id: 1,
  nome: 'Portal do Cliente',
  responsavel: 'Time Web',
  url: 'https://demo.target.com',
  ambiente: 'producao',
  exposicao: 'internet',
  importancia: 'alta',
  ambiente_label: 'Produção',
  exposicao_label: 'Internet',
  importancia_label: 'Alta',
  criado_em: '2026-01-10T09:00:00',
  atualizado_em: '2026-01-10T09:00:00',
  total_vulnerabilidades: 12,
  total_criticas: 4,
  total_abertas: 10,
}

export const OPCOES: Opcoes = {
  ambientes: [
    { valor: 'producao', label: 'Produção' },
    { valor: 'homologacao', label: 'Homologação' },
    { valor: 'teste', label: 'Teste' },
  ],
  exposicoes: [
    { valor: 'internet', label: 'Internet' },
    { valor: 'interna', label: 'Interna' },
  ],
  importancias: [
    { valor: 'alta', label: 'Alta' },
    { valor: 'media', label: 'Média' },
    { valor: 'baixa', label: 'Baixa' },
  ],
  riscos: [
    { valor: 'critico', label: 'Crítico' },
    { valor: 'alto', label: 'Alto' },
    { valor: 'medio', label: 'Médio' },
    { valor: 'baixo', label: 'Baixo' },
  ],
  status: [
    { valor: 'nova', label: 'Nova' },
    { valor: 'em_analise', label: 'Em análise' },
    { valor: 'em_correcao', label: 'Em correção' },
    { valor: 'corrigida', label: 'Corrigida' },
    { valor: 'falso_positivo', label: 'Falso positivo' },
  ],
}

export const UPLOADS: UploadResumo[] = [
  {
    id: 1,
    ferramenta: 'semgrep',
    ferramenta_label: 'Semgrep',
    nome_arquivo: 'semgrep.json',
    tamanho_bytes: 2048,
    total_achados: 2,
    total_ignorados: 0,
    criado_em: '2026-01-11T10:00:00',
  },
]

/** Confirmada pelas duas ferramentas, em produção exposta: o caso Crítico. */
export const VULNERABILIDADE_CRITICA: Vulnerabilidade = {
  id: 10,
  aplicacao_id: 1,
  aplicacao_nome: 'Portal do Cliente',
  aplicacao_ambiente: 'Produção',
  tipo_vuln: 'xss',
  endpoint: '/busca',
  correlacionada: true,
  encontrada_semgrep: true,
  confirmada_nuclei: true,
  origens: ['Semgrep', 'Nuclei'],
  risco: 'critico',
  risco_label: 'Crítico',
  severidade_original: 'ERROR',
  status: 'nova',
  status_label: 'Nova',
  tem_analise_ia: false,
  identificada_em: '2026-01-11T10:05:00',
}

/** Só o Semgrep viu, e sem severidade reportada: exercita a célula com traço. */
export const VULNERABILIDADE_SEM_SEVERIDADE: Vulnerabilidade = {
  ...VULNERABILIDADE_CRITICA,
  id: 11,
  tipo_vuln: 'sqli',
  endpoint: '/api/usuarios',
  correlacionada: false,
  confirmada_nuclei: false,
  origens: ['Semgrep'],
  risco: 'alto',
  risco_label: 'Alto',
  severidade_original: null,
  status: 'em_correcao',
  status_label: 'Em correção',
}

export const DETALHE: VulnerabilidadeDetalhe = {
  ...VULNERABILIDADE_CRITICA,
  justificativa:
    'Vulnerabilidade identificada no código pelo Semgrep e confirmada na aplicação pelo ' +
    'Nuclei, em ambiente de produção, exposta à internet, importância alta para o negócio.',
  atualizada_em: '2026-01-11T10:05:00',
  tickets: [],
  owner_id: null,
  owner_team: null,
  assigned_at: null,
  due_at: null,
  resolved_at: null,
  false_positive_reason: null,
  risk_acceptance_reason: null,
  risk_acceptance_approver_id: null,
  risk_accepted_at: null,
  comments: [],
  evidences: [],
  achados: [
    {
      id: 100,
      origem: 'semgrep',
      origem_label: 'Semgrep',
      severidade: 'ERROR',
      mensagem: 'Parâmetro renderizado no HTML sem escaping.',
      regra_id: 'python.flask.security.xss.reflected-xss',
      arquivo: 'src/views/busca.py',
      linha: 42,
      cwe: 'CWE-79',
      url: null,
      http_status: null,
      evidencia: null,
      repository: null,
      commit: null,
      fingerprint: null,
    resource: null,
    resource_type: null,
    iac_provider: null,
    framework: null,
    guideline: null,
    },
    {
      id: 101,
      origem: 'nuclei',
      origem_label: 'Nuclei',
      severidade: 'high',
      mensagem: 'Reflected Cross-Site Scripting',
      regra_id: 'reflected-xss',
      arquivo: null,
      linha: null,
      cwe: null,
      url: 'https://demo.target.com/busca?q=teste',
      http_status: 200,
      evidencia: '<script>alert(1)</script>',
      repository: null,
      commit: null,
      fingerprint: null,
      resource: null,
      resource_type: null,
      iac_provider: null,
      framework: null,
      guideline: null,
    },
  ],
  analise_ia: null,
  historico: [
    {
      id: 200,
      status_anterior: null,
      status_novo: 'nova',
      status_anterior_label: null,
      status_novo_label: 'Nova',
      comentario: 'Vulnerabilidade identificada na ingestão do relatório.',
      criado_em: '2026-01-11T10:05:00',
      usuario_nome: null,
    },
  ],
}

export const DETALHE_COM_IA: VulnerabilidadeDetalhe = {
  ...DETALHE,
  tem_analise_ia: true,
  analise_ia: {
    explicacao: 'O parâmetro de busca é refletido no HTML sem escaping.',
    impacto: 'Um atacante poderia roubar a sessão de quem abrir o link.',
    priorizacao: 'Crítica porque as duas ferramentas confirmaram em produção exposta.',
    sugestao: 'Aplicar escaping na saída do template.',
    validacao: 'Reenviar o payload e conferir que sai escapado.',
    descricao_ticket: '[XSS] Corrigir reflexão do parâmetro de busca em /busca',
    gerada_em: '2026-01-12T08:00:00',
  },
}
