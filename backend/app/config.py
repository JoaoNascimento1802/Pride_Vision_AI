# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
config.py — Configuração da aplicação, lida do ambiente.

O arquivo .env é carregado na inicialização, mas variáveis já definidas no
ambiente sempre têm precedência: é isso que permite configurar a hospedagem sem
editar arquivo nenhum.
"""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

# Raiz do backend (…/backend), usada para resolver caminhos relativos
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Modelos de IA
#
# Fixar o nome de um modelo no código apodrece: este projeto já foi mordido duas
# vezes. O `gemini-1.5-flash` original foi aposentado, e o `gemini-2.0-flash`
# que o substituiria foi desativado logo depois — nos dois casos o sintoma é o
# mesmo, "modelo inválido", com a chave do usuário perfeitamente válida.
#
# Por isso o modelo é configuração, e em três níveis:
#
#   OPENAI_MODEL / GEMINI_MODEL    um modelo só, escolha explícita do usuário.
#                                  Falha visivelmente em vez de ser trocado.
#   OPENAI_MODELS / GEMINI_MODELS  a lista de candidatos, em ordem. O primeiro
#                                  que a chave aceitar é o usado.
#   (nada definido)                as listas abaixo, que são só o padrão.
#
# Quando todos os padrões caducarem, a correção é no `.env`, não aqui.
# ---------------------------------------------------------------------------

MODELOS_GEMINI_PADRAO = (
    "gemini-flash-latest",  # alias que acompanha o Flash atual, quando existe
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
)

MODELOS_OPENAI_PADRAO = (
    "gpt-5.6-luna",  # o mais econômico da geração atual
    "gpt-5.6-terra",
    "gpt-4o-mini",  # gerações anteriores, para contas mais antigas
    "gpt-4o",
)


def _lista_do_ambiente(variavel: str, padrao: tuple[str, ...]) -> list[str]:
    """Lista separada por vírgula vinda do ambiente, ou o padrão do projeto."""
    itens = [item.strip() for item in os.environ.get(variavel, "").split(",")]
    preenchidos = [item for item in itens if item]
    return preenchidos or list(padrao)


# As duas formas em que um Postgres gerenciado entrega a string: nenhuma declara
# o driver, e é justamente o driver que precisa ser fixado.
_ESQUEMAS_SEM_DRIVER = ("postgres://", "postgresql://")
_ESQUEMA_COM_DRIVER = "postgresql+psycopg://"


def _normalizar_url_do_banco(url: str) -> str:
    """
    Aponta a URL do Postgres para o driver que o projeto realmente instala.

    Postgres gerenciado entrega a string sem driver, e nenhuma das duas formas
    serve como está:

    - `postgres://` o SQLAlchemy 2.0 recusa de saída, com
      `Can't load plugin: sqlalchemy.dialects:postgres`.
    - `postgresql://` ele aceita — e então resolve para o **psycopg2**, que não é
      dependência deste projeto. O erro vira `ModuleNotFoundError: No module
      named 'psycopg2'`, que aponta para uma biblioteca ausente em vez de para o
      esquema da URL. É o caso mais traiçoeiro, porque a string parece correta.

    Os dois passam a apontar para `psycopg` (versão 3), que está no
    `pyproject.toml`. Assim a string do provedor é colável como veio.

    Passa intacto: SQLite e qualquer esquema que já declare o driver — aí a
    escolha foi de quem configurou, inclusive um `postgresql+psycopg://` que já
    veio normalizado. Ver AC-ARQ-17.
    """
    for esquema in _ESQUEMAS_SEM_DRIVER:
        if url.startswith(esquema):
            return _ESQUEMA_COM_DRIVER + url[len(esquema) :]
    return url


def load_dotenv(path: Path | None = None) -> None:
    """
    Carrega pares CHAVE=VALOR de um arquivo .env para os.environ.

    Variáveis já presentes no ambiente não são sobrescritas. Linhas em branco,
    comentários e linhas malformadas são ignoradas. Só usa biblioteca padrão.
    """
    env_path = path if path is not None else BASE_DIR / ".env"
    if not env_path.is_file():
        return

    try:
        conteudo = env_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover — permissão/disco
        print(f"[WARN] Não foi possível ler '{env_path}': {exc}", file=sys.stderr)
        return

    for linha_bruta in conteudo.splitlines():
        linha = linha_bruta.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        valor = valor.strip().strip("\"'")

        if chave and chave not in os.environ:
            os.environ[chave] = valor


load_dotenv()


class Settings:
    """Configuração efetiva da aplicação."""

    # --- Banco de dados ---
    # A RFC 7518 recomenda chave de pelo menos 32 bytes para HMAC-SHA256. Uma
    # chave curta é mais fácil de quebrar por força bruta, e quem quebra a chave
    # forja tokens de qualquer usuário.
    SECRET_KEY_MIN_BYTES = 32
    JWT_ALGORITHM = "HS256"

    def __init__(self) -> None:
        """
        Lê a configuração do ambiente.

        Os valores são atributos de instância, não de classe: assim uma nova
        instância reflete o ambiente atual, o que torna a configuração testável
        e evita a armadilha de parecer dinâmica sendo congelada na importação.
        """
        # --- Banco de dados ---
        # SQLite por padrão, como o projeto especifica. DATABASE_URL permite
        # apontar para outro banco na hospedagem sem alterar código.
        self.DATABASE_URL: str = _normalizar_url_do_banco(
            os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'pride_vision.db'}")
        )

        # --- Autenticação ---
        # Sem SECRET_KEY definida, uma chave aleatória é gerada a cada
        # inicialização. Isso é seguro para desenvolvimento (os tokens
        # simplesmente deixam de valer ao reiniciar), mas em produção precisa
        # ser fixa — veja o aviso em main.py.
        self.SECRET_KEY_DEFINIDA: bool = bool(os.environ.get("SECRET_KEY"))
        self.SECRET_KEY: str = os.environ.get("SECRET_KEY", "") or secrets.token_urlsafe(32)
        self.TOKEN_EXPIRA_MINUTOS: int = int(os.environ.get("TOKEN_EXPIRA_MINUTOS", "480"))

        # --- IA ---
        self.AI_DEFAULT_PROVIDER: str = (
            os.environ.get("AI_DEFAULT_PROVIDER", "openai").strip().lower()
        )
        self.OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
        self.GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

        # Modelo único, escolha explícita do usuário. Vazio = usar a lista.
        self.OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "").strip()
        self.GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "").strip()

        # Candidatos em ordem de preferência, com o padrão do projeto como base
        self.OPENAI_MODELS: list[str] = _lista_do_ambiente("OPENAI_MODELS", MODELOS_OPENAI_PADRAO)
        self.GEMINI_MODELS: list[str] = _lista_do_ambiente("GEMINI_MODELS", MODELOS_GEMINI_PADRAO)

        # Nomes internos mascarados antes de qualquer envio à IA
        self.PRIDE_INTERNAL_NAMES: list[str] = [
            n.strip() for n in os.environ.get("PRIDE_INTERNAL_NAMES", "").split(",") if n.strip()
        ]

        # --- CORS ---
        # Origens do frontend autorizadas a chamar a API.
        self.CORS_ORIGINS: list[str] = [
            o.strip()
            for o in os.environ.get(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if o.strip()
        ]

        # URL do frontend para redirecionamentos (ex: OAuth callback)
        self.FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:5173")

        # --- Upload ---
        # Limite por arquivo. Relatórios reais raramente passam de poucos MB; o
        # teto evita que um upload gigante derrube o processo.
        self.MAX_UPLOAD_BYTES: int = int(os.environ.get("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))

        # --- CI/CD Integrations ---
        self.GITHUB_APP_ID: str = os.environ.get("GITHUB_APP_ID", "")
        self.GITHUB_INSTALLATION_ID: str = os.environ.get("GITHUB_INSTALLATION_ID", "")
        self.GITHUB_PRIVATE_KEY: str = os.environ.get("GITHUB_PRIVATE_KEY", "").replace("\\n", "\n")
        self.GITHUB_WEBHOOK_SECRET: str = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
        self.GITHUB_API_URL: str = os.environ.get("GITHUB_API_URL", "https://api.github.com")

        self.GITLAB_BASE_URL: str = os.environ.get("GITLAB_BASE_URL", "https://gitlab.com")
        self.GITLAB_TOKEN: str = os.environ.get("GITLAB_TOKEN", "")
        self.GITLAB_WEBHOOK_SECRET: str = os.environ.get("GITLAB_WEBHOOK_SECRET", "")
        self.GITLAB_API_URL: str = os.environ.get("GITLAB_API_URL", "https://gitlab.com/api/v4")

        # --- Jira OAuth 2.0 (3LO) ---
        self.JIRA_CLIENT_ID: str = os.environ.get("JIRA_CLIENT_ID", "")
        self.JIRA_CLIENT_SECRET: str = os.environ.get("JIRA_CLIENT_SECRET", "")
        self.JIRA_REDIRECT_URI: str = os.environ.get("JIRA_REDIRECT_URI", "http://localhost:8000/api/integrations/jira/callback")
        # Write scopes e offline_access para refresh token
        self.JIRA_SCOPES: str = os.environ.get("JIRA_SCOPES", "read:jira-work write:jira-work offline_access")

    @property
    def ia_configurada(self) -> bool:
        """True quando há chave para o provedor selecionado."""
        if self.usando_gemini:
            return bool(self.GEMINI_API_KEY)
        return bool(self.OPENAI_API_KEY)

    @property
    def usando_gemini(self) -> bool:
        return self.AI_DEFAULT_PROVIDER == "gemini"

    @property
    def modelo_ia_previsto(self) -> str:
        """
        Modelo que o provedor ativo tentará primeiro.

        Serve para a rota de saúde: descobrir qual modelo está em uso é
        justamente a parte difícil de diagnosticar quando um provedor aposenta
        um nome e a API passa a responder "modelo inválido".
        """
        if self.usando_gemini:
            return self.GEMINI_MODEL or self.GEMINI_MODELS[0]
        return self.OPENAI_MODEL or self.OPENAI_MODELS[0]

    @property
    def secret_key_fraca(self) -> bool:
        """True quando a SECRET_KEY foi definida, porém é curta demais."""
        return (
            self.SECRET_KEY_DEFINIDA
            and len(self.SECRET_KEY.encode("utf-8")) < self.SECRET_KEY_MIN_BYTES
        )


settings = Settings()
