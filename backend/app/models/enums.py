"""
enums.py — Vocabulário controlado do domínio.

Os valores armazenados são slugs ASCII em minúsculas (`producao`), estáveis para
banco e URL. O rótulo acentuado para exibição fica em `label`, usado pela API e
pela interface.
"""

from __future__ import annotations

from enum import StrEnum


class EnumRotulado(StrEnum):
    """
    Base dos enums do domínio.

    Todo membro expõe `value` (slug estável para banco e URL) e `label` (texto
    acentuado para exibição). Ter a base comum permite que a rota `/api/opcoes`
    percorra qualquer um deles com um único tipo.
    """

    @property
    def label(self) -> str:
        """Rótulo legível. Cada enum concreto sobrescreve."""
        return str(self.value)


class Ambiente(EnumRotulado):
    """Ambiente onde a aplicação roda. Entra no cálculo de risco."""

    PRODUCAO = "producao"
    HOMOLOGACAO = "homologacao"
    TESTE = "teste"

    @property
    def label(self) -> str:
        return {"producao": "Produção", "homologacao": "Homologação", "teste": "Teste"}[self.value]


class Exposicao(EnumRotulado):
    """Alcance da aplicação. Uma aplicação na internet é mais atacável."""

    INTERNET = "internet"
    INTERNA = "interna"

    @property
    def label(self) -> str:
        return {"internet": "Internet", "interna": "Interna"}[self.value]


class Importancia(EnumRotulado):
    """Importância da aplicação para o negócio."""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

    @property
    def label(self) -> str:
        return {"alta": "Alta", "media": "Média", "baixa": "Baixa"}[self.value]


class Ferramenta(EnumRotulado):
    """
    Origem do achado.
    """

    SEMGREP = "semgrep"
    NUCLEI = "nuclei"
    TRIVY = "trivy"
    GITLEAKS = "gitleaks"
    CHECKOV = "checkov"
    API_SECURITY = "api_security"
    SUPPLY_CHAIN = "supply_chain"
    RUNTIME = "runtime"
    CLOUD_POSTURE = "cloud_posture"

    @property
    def label(self) -> str:
        return {
            "semgrep": "Semgrep",
            "nuclei": "Nuclei",
            "trivy": "Trivy",
            "gitleaks": "Gitleaks",
            "checkov": "Checkov",
            "api_security": "API Security",
            "supply_chain": "Supply Chain",
            "runtime": "Runtime Security",
            "cloud_posture": "Cloud CSPM",
        }[self.value]


class Risco(EnumRotulado):
    """
    Nível de risco calculado pelo PRIDE.

    Quatro níveis, conforme a seção 5 da especificação. Não confundir com a
    severidade original da ferramenta, que é preservada separadamente.
    """

    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"

    @property
    def label(self) -> str:
        return {"critico": "Crítico", "alto": "Alto", "medio": "Médio", "baixo": "Baixo"}[
            self.value
        ]

    @property
    def ordem(self) -> int:
        """Chave de ordenação: menor número aparece primeiro no relatório."""
        return {"critico": 0, "alto": 1, "medio": 2, "baixo": 3}[self.value]


class StatusVulnerabilidade(EnumRotulado):
    """Ciclo de tratamento de uma vulnerabilidade, conforme a seção 4 do projeto."""

    NOVA = "nova"
    EM_ANALISE = "em_analise"
    EM_CORRECAO = "em_correcao"
    AGUARDANDO_VALIDACAO = "aguardando_validacao"
    CORRIGIDA = "corrigida"
    FALSO_POSITIVO = "falso_positivo"
    ACEITO_COMO_RISCO = "aceito_como_risco"
    EXCECAO_TEMPORARIA = "excecao_temporaria"
    DUPLICADO = "duplicado"

    @property
    def label(self) -> str:
        return {
            "nova": "Nova",
            "em_analise": "Em análise",
            "em_correcao": "Em correção",
            "aguardando_validacao": "Aguardando validação",
            "corrigida": "Corrigida",
            "falso_positivo": "Falso positivo",
            "aceito_como_risco": "Aceito como risco",
            "excecao_temporaria": "Exceção temporária",
            "duplicado": "Duplicado",
        }[self.value]

    @property
    def encerrada(self) -> bool:
        """True para status que tiram a vulnerabilidade da fila de trabalho ativa."""
        return self in (
            StatusVulnerabilidade.CORRIGIDA,
            StatusVulnerabilidade.FALSO_POSITIVO,
            StatusVulnerabilidade.ACEITO_COMO_RISCO,
            StatusVulnerabilidade.DUPLICADO,
        )

    @property
    def exige_reason(self) -> bool:
        """True para status que exigem justificativa explícita."""
        return self in (
            StatusVulnerabilidade.FALSO_POSITIVO,
            StatusVulnerabilidade.ACEITO_COMO_RISCO,
        )


class TicketProvider(EnumRotulado):
    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    AZURE_DEVOPS = "azure_devops"

    @property
    def label(self) -> str:
        return {
            "jira": "Jira",
            "github": "GitHub Issues",
            "gitlab": "GitLab Issues",
            "azure_devops": "Azure DevOps",
        }[self.value]


class TicketStatus(EnumRotulado):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    @property
    def label(self) -> str:
        return {
            "open": "Aberto",
            "in_progress": "Em Progresso",
            "resolved": "Resolvido",
            "closed": "Fechado",
        }[self.value]


class Role(EnumRotulado):
    ADMIN = "admin"
    APPSEC = "appsec"
    DEVELOPER = "developer"
    TECH_LEAD = "tech_lead"
    MANAGER = "manager"
    AUDITOR = "auditor"

    @property
    def label(self) -> str:
        return {
            "admin": "Admin",
            "appsec": "AppSec",
            "developer": "Developer",
            "tech_lead": "Tech Lead",
            "manager": "Manager",
            "auditor": "Auditor",
        }[self.value]


class GateDecision(EnumRotulado):
    """
    Decisão do Security Gate para um pipeline.

    PASS — nenhuma violação de política; o pipeline pode prosseguir.
    WARN — há alertas não bloqueantes; o pipeline prossegue com aviso.
    BLOCK — há violações bloqueantes; o pipeline deve ser interrompido.
    """

    PASS = "pass"
    WARN = "warn"
    BLOCK = "block"

    @property
    def label(self) -> str:
        return {"pass": "Aprovado", "warn": "Com aviso", "block": "Bloqueado"}[self.value]

    @property
    def icone(self) -> str:
        return {"pass": "✅", "warn": "⚠️", "block": "❌"}[self.value]



class AuditAction(EnumRotulado):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"

    CREATE_FINDING = "CREATE_FINDING"
    UPDATE_FINDING = "UPDATE_FINDING"
    STATUS_CHANGED = "STATUS_CHANGED"
    CLOSE_FINDING = "CLOSE_FINDING"
    REOPEN_FINDING = "REOPEN_FINDING"

    # Remediation workflow
    ASSIGNMENT_CHANGED = "ASSIGNMENT_CHANGED"
    COMMENT_ADDED = "COMMENT_ADDED"
    FALSE_POSITIVE_MARKED = "FALSE_POSITIVE_MARKED"
    RISK_ACCEPTED = "RISK_ACCEPTED"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    REVALIDATION_REQUESTED = "REVALIDATION_REQUESTED"
    REVALIDATION_PASSED = "REVALIDATION_PASSED"
    REVALIDATION_FAILED = "REVALIDATION_FAILED"

    # SLA
    SLA_BREACHED = "SLA_BREACHED"
    SLA_WARNING = "SLA_WARNING"
    SLA_DUE_SOON = "SLA_DUE_SOON"

    CREATE_POLICY = "CREATE_POLICY"
    UPDATE_POLICY = "UPDATE_POLICY"
    DELETE_POLICY = "DELETE_POLICY"

    CREATE_EXCEPTION = "CREATE_EXCEPTION"
    APPROVE_EXCEPTION = "APPROVE_EXCEPTION"
    REJECT_EXCEPTION = "REJECT_EXCEPTION"
    REVOKE_EXCEPTION = "REVOKE_EXCEPTION"

    CREATE_TICKET = "CREATE_TICKET"
    UPDATE_TICKET = "UPDATE_TICKET"
    SYNC_TICKET = "SYNC_TICKET"

    GATE_EXECUTED = "GATE_EXECUTED"

    JIRA_CONNECT = "JIRA_CONNECT"
    JIRA_DISCONNECT = "JIRA_DISCONNECT"
    CREATE_API_ASSET = "CREATE_API_ASSET"
    DELETE_API_ASSET = "DELETE_API_ASSET"
    API_SCAN_STARTED = "API_SCAN_STARTED"
    API_SCAN_FINISHED = "API_SCAN_FINISHED"
    SUPPLY_CHAIN_VERIFICATION_STARTED = "SUPPLY_CHAIN_VERIFICATION_STARTED"
    SUPPLY_CHAIN_VERIFICATION_FINISHED = "SUPPLY_CHAIN_VERIFICATION_FINISHED"

    @property
    def label(self) -> str:
        return self.value


class EntityType(EnumRotulado):
    USER = "USER"
    FINDING = "FINDING"
    POLICY = "POLICY"
    EXCEPTION = "EXCEPTION"
    TICKET = "TICKET"
    PIPELINE = "PIPELINE"
    INTEGRATION = "INTEGRATION"
    SECURITY_GATE = "SECURITY_GATE"
    COMMENT = "COMMENT"
    EVIDENCE = "EVIDENCE"
    SLA_STARTED = "SLA_STARTED"
    SLA_BREACHED = "SLA_BREACHED"
    SLA_DUE_SOON = "SLA_DUE_SOON"
    API_ASSET = "API_ASSET"
    API_ENDPOINT = "API_ENDPOINT"

    @property
    def label(self) -> str:
        return self.value


class StatusSla(EnumRotulado):
    """Estados do relógio de SLA."""

    ON_TRACK = "on_track"
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXEMPT = "exempt"

    @property
    def label(self) -> str:
        return {
            self.ON_TRACK: "Dentro do prazo",
            self.DUE_SOON: "Próximo do vencimento",
            self.OVERDUE: "Vencido",
            self.PAUSED: "Pausado",
            self.COMPLETED: "Concluído",
            self.EXEMPT: "Isento",
        }[self]
