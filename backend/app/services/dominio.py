"""
dominio.py — Tipos puros usados pelos serviços.

Estes objetos não conhecem banco de dados. Os serviços de normalização,
correlação e risco trabalham só com eles, o que os mantém testáveis sem subir
nada e preserva a auditabilidade que a especificação exige da classificação.

Não confundir com os modelos ORM de `app/models`: `AchadoNormalizado` é o que
sai do parser, `Finding` é o que fica gravado; `GrupoCorrelacionado` é o que sai
do correlacionador, `Vulnerability` é o que fica gravado.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.enums import Ferramenta


@dataclass(frozen=True)
class AchadoNormalizado:
    """
    Um achado de qualquer das duas ferramentas, já no formato comum.

    Congelado para poder ser usado como chave e para deixar claro que o parser
    não altera achados depois de produzi-los.
    """

    origem: Ferramenta
    tipo_vuln: str
    endpoint: str
    severidade: str
    mensagem: str
    regra_id: str

    # Presentes apenas no Semgrep
    arquivo: str | None = None
    linha: int | None = None
    cwe: str | None = None

    # Presentes apenas no Nuclei
    url: str | None = None
    http_status: int | None = None
    evidencia: str | None = None

    # Presentes apenas no Gitleaks / Secrets
    repository: str | None = None
    commit: str | None = None
    fingerprint: str | None = None

    # Presentes apenas no IaC (Checkov / Tfsec)
    resource: str | None = None
    resource_type: str | None = None
    iac_provider: str | None = None
    framework: str | None = None
    guideline: str | None = None

    # Presentes apenas no Container Scanning
    image_name: str | None = None
    image_digest: str | None = None


    # Presentes apenas no Cloud CSPM
    cloud_provider: str | None = None
    region: str | None = None
    compliance_control: str | None = None

    # Presentes apenas no Runtime / eBPF (Falco, Tetragon)
    process_name: str | None = None
    pid: int | None = None
    syscall: str | None = None
    container_id: str | None = None
    hit_count: int = 1
    last_seen_at: str | None = None
    image_tag: str | None = None
    image_repository: str | None = None
    registry: str | None = None
    base_image: str | None = None
    os: str | None = None
    architecture: str | None = None
    layer: str | None = None
    pacote: str | None = None
    versao: str | None = None
    versao_corrigida: str | None = None


@dataclass
class ResultadoParse:
    """
    Saída de um parser.

    Os avisos são devolvidos em vez de impressos: a API mostra ao usuário o que
    foi descartado, para que um relatório com lixo não pareça ter sido aceito
    por inteiro.
    """

    achados: list[AchadoNormalizado] = field(default_factory=list)
    ignorados: int = 0
    avisos: list[str] = field(default_factory=list)


@dataclass
class GrupoCorrelacionado:
    """Achados agrupados por tipo e endpoint compatível."""

    tipo_vuln: str
    endpoint: str
    achados: list[AchadoNormalizado]

    @property
    def origens(self) -> frozenset[Ferramenta]:
        return frozenset(a.origem for a in self.achados)

    @property
    def encontrada_semgrep(self) -> bool:
        return Ferramenta.SEMGREP in self.origens

    @property
    def confirmada_nuclei(self) -> bool:
        return Ferramenta.NUCLEI in self.origens

    @property
    def correlacionada(self) -> bool:
        """True quando as duas ferramentas apontaram a mesma coisa."""
        return self.encontrada_semgrep and self.confirmada_nuclei

    def achado_de(self, ferramenta: Ferramenta) -> AchadoNormalizado | None:
        return next((a for a in self.achados if a.origem is ferramenta), None)

    @property
    def tem_evidencia(self) -> bool:
        """
        True quando algum achado traz prova concreta.

        Evidência extraída ou status HTTP significam que o Nuclei realmente
        alcançou a aplicação. É o que separa um achado teórico de um confirmado.
        """
        return any(a.evidencia is not None or a.http_status is not None for a in self.achados)
