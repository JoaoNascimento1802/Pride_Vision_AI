# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes de configuração e leitura do .env — SDD/09-arquitetura.md.

A configuração é o que separa "roda na minha máquina" de "roda publicado": chave
fraca, limite de upload e nomes internos mascarados vêm todos daqui.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import os
from pathlib import Path

from app.config import Settings, load_dotenv


class TestLoadDotenv:
    def test_le_pares_chave_valor(self, tmp_path: Path, monkeypatch):
        """AC-ARQ-07, AC-ARQ-E2 — pares viram variáveis; comentário e lixo são ignorados."""
        arquivo = tmp_path / ".env"
        arquivo.write_text(
            "# comentário\n"
            "\n"
            'OPENAI_API_KEY="sk-do-arquivo"\n'
            "AI_DEFAULT_PROVIDER=gemini\n"
            "linha invalida sem igual\n",
            encoding="utf-8",
        )
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("AI_DEFAULT_PROVIDER", raising=False)

        load_dotenv(arquivo)

        assert os.environ["OPENAI_API_KEY"] == "sk-do-arquivo"
        assert os.environ["AI_DEFAULT_PROVIDER"] == "gemini"

    def test_ambiente_tem_precedencia(self, tmp_path: Path, monkeypatch):
        """AC-ARQ-07 — permite configurar a hospedagem sem editar arquivo."""
        arquivo = tmp_path / ".env"
        arquivo.write_text("OPENAI_API_KEY=do-arquivo\n", encoding="utf-8")
        monkeypatch.setenv("OPENAI_API_KEY", "do-ambiente")

        load_dotenv(arquivo)

        assert os.environ["OPENAI_API_KEY"] == "do-ambiente"

    def test_arquivo_ausente_e_ignorado(self, tmp_path: Path):
        """AC-ARQ-E1 — sem `.env` nada quebra e valem os padrões."""
        load_dotenv(tmp_path / "nao-existe.env")  # não pode levantar erro


class TestSecretKey:
    def test_chave_longa_nao_e_fraca(self, monkeypatch):
        """AC-ARQ-09 — chave com 32 bytes ou mais não é sinalizada."""
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        assert not Settings().secret_key_fraca

    def test_chave_curta_e_sinalizada(self, monkeypatch):
        """AC-ARQ-09 — chave curta permite forjar token de qualquer usuário."""
        monkeypatch.setenv("SECRET_KEY", "curta")
        assert Settings().secret_key_fraca

    def test_chave_gerada_automaticamente_nao_e_fraca(self, monkeypatch):
        """AC-ARQ-08 — sem SECRET_KEY, a chave gerada tem tamanho seguro e é sinalizada."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        s = Settings()
        assert not s.SECRET_KEY_DEFINIDA
        assert not s.secret_key_fraca
        assert len(s.SECRET_KEY.encode()) >= s.SECRET_KEY_MIN_BYTES


class TestIaConfigurada:
    def test_openai_com_chave(self, monkeypatch):
        """AC-ARQ-10 — com provedor openai e chave, a IA é reportada como configurada."""
        monkeypatch.setenv("AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-teste")
        assert Settings().ia_configurada

    def test_openai_sem_chave(self, monkeypatch):
        """AC-ARQ-10 — sem chave, a IA é reportada como não configurada."""
        monkeypatch.setenv("AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "")
        assert not Settings().ia_configurada

    def test_gemini_olha_a_chave_do_gemini(self, monkeypatch):
        """AC-ARQ-10 — cada provedor olha a própria chave, não a do outro."""
        monkeypatch.setenv("AI_DEFAULT_PROVIDER", "gemini")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-teste")
        monkeypatch.setenv("GEMINI_API_KEY", "")
        assert not Settings().ia_configurada

        monkeypatch.setenv("GEMINI_API_KEY", "AIza-teste")
        assert Settings().ia_configurada


class TestLimiteDeUpload:
    def test_valor_do_ambiente_vale(self, monkeypatch):
        """AC-ARQ-11 — MAX_UPLOAD_BYTES define o teto por arquivo."""
        monkeypatch.setenv("MAX_UPLOAD_BYTES", "1024")
        assert Settings().MAX_UPLOAD_BYTES == 1024

    def test_padrao_quando_ausente(self, monkeypatch):
        """AC-ARQ-11 — sem a variável, vale o padrão de 20 MB."""
        monkeypatch.delenv("MAX_UPLOAD_BYTES", raising=False)
        assert Settings().MAX_UPLOAD_BYTES == 20 * 1024 * 1024


class TestNomesInternos:
    def test_lista_separada_por_virgula(self, monkeypatch):
        """AC-ARQ-12 — os nomes internos a mascarar vêm de PRIDE_INTERNAL_NAMES."""
        monkeypatch.setenv("PRIDE_INTERNAL_NAMES", "servidor-prod-01, banco-interno ,")
        assert Settings().PRIDE_INTERNAL_NAMES == ["servidor-prod-01", "banco-interno"]

    def test_ausente_vira_lista_vazia(self, monkeypatch):
        """AC-ARQ-12 — sem a variável, não há nome interno configurado."""
        monkeypatch.delenv("PRIDE_INTERNAL_NAMES", raising=False)
        assert Settings().PRIDE_INTERNAL_NAMES == []


class TestModelosDeIA:
    """
    Nome de modelo e configuracao, nao constante.

    Provedores aposentam modelos sem aviso; quando os padroes do projeto
    caducarem, a saida precisa ser mexer no `.env`, nao no codigo.
    """

    def test_lista_de_candidatos_vem_do_ambiente(self, monkeypatch):
        """AC-ARQ-14 — OPENAI_MODELS define os candidatos, na ordem informada."""
        monkeypatch.setenv("OPENAI_MODELS", "modelo-a, modelo-b ,, modelo-c")
        assert Settings().OPENAI_MODELS == ["modelo-a", "modelo-b", "modelo-c"]

    def test_lista_do_gemini_tambem(self, monkeypatch):
        """AC-ARQ-14 — GEMINI_MODELS funciona do mesmo jeito."""
        monkeypatch.setenv("GEMINI_MODELS", "gemini-x,gemini-y")
        assert Settings().GEMINI_MODELS == ["gemini-x", "gemini-y"]

    def test_sem_configuracao_valem_os_padroes_do_projeto(self, monkeypatch):
        """AC-ARQ-15 — sem variável, as listas padrão; sem modelo explícito, vazio."""
        from app.services.ai_explainer import MODELOS_GEMINI, MODELOS_OPENAI

        for variavel in ("OPENAI_MODEL", "GEMINI_MODEL", "OPENAI_MODELS", "GEMINI_MODELS"):
            monkeypatch.delenv(variavel, raising=False)

        s = Settings()
        assert s.OPENAI_MODEL == ""
        assert s.GEMINI_MODEL == ""
        assert s.OPENAI_MODELS == list(MODELOS_OPENAI)
        assert s.GEMINI_MODELS == list(MODELOS_GEMINI)

    def test_modelo_explicito_e_o_previsto(self, monkeypatch):
        """AC-ARQ-16 — com modelo explícito, é ele que será usado."""
        monkeypatch.setenv("AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_MODEL", "modelo-escolhido")
        assert Settings().modelo_ia_previsto == "modelo-escolhido"

    def test_sem_modelo_explicito_o_previsto_e_o_primeiro_candidato(self, monkeypatch):
        """AC-ARQ-16 — sem modelo explícito, o primeiro da lista de candidatos."""
        monkeypatch.setenv("AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        monkeypatch.setenv("OPENAI_MODELS", "primeiro,segundo")
        assert Settings().modelo_ia_previsto == "primeiro"

    def test_o_previsto_segue_o_provedor_ativo(self, monkeypatch):
        """AC-ARQ-16 — trocar o provedor troca o modelo previsto."""
        monkeypatch.setenv("AI_DEFAULT_PROVIDER", "gemini")
        monkeypatch.delenv("GEMINI_MODEL", raising=False)
        monkeypatch.setenv("GEMINI_MODELS", "gemini-configurado,outro")
        assert Settings().modelo_ia_previsto == "gemini-configurado"


class TestCors:
    def test_origens_do_ambiente(self, monkeypatch):
        """AC-ARQ-13 — apenas as origens declaradas em CORS_ORIGINS são liberadas."""
        monkeypatch.setenv("CORS_ORIGINS", "https://pride.exemplo.com, http://localhost:5173")
        assert Settings().CORS_ORIGINS == [
            "https://pride.exemplo.com",
            "http://localhost:5173",
        ]

    def test_padrao_libera_o_vite_local(self, monkeypatch):
        """AC-ARQ-13 — sem a variável, valem as origens do Vite em desenvolvimento."""
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        assert Settings().CORS_ORIGINS == [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]


class TestUrlDoBanco:
    """
    Postgres gerenciado entrega a string sem driver. `postgres://` o SQLAlchemy
    recusa; `postgresql://` ele aceita e resolve para psycopg2, que este projeto
    não instala. Os dois precisam apontar para o psycopg 3.
    """

    def test_esquema_historico_do_postgres_e_normalizado(self, monkeypatch):
        """AC-ARQ-17 — postgres:// vira postgresql+psycopg://, que o SQLAlchemy aceita."""
        monkeypatch.setenv(
            "DATABASE_URL", "postgres://ana:senha@host.neon.tech/pride?sslmode=require"
        )

        assert Settings().DATABASE_URL == (
            "postgresql+psycopg://ana:senha@host.neon.tech/pride?sslmode=require"
        )

    def test_postgresql_sem_driver_tambem_e_normalizado(self, monkeypatch):
        """AC-ARQ-17 — sem driver, o SQLAlchemy escolheria psycopg2, que não é instalado."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://ana@host.neon.tech/pride?sslmode=require")

        assert Settings().DATABASE_URL == (
            "postgresql+psycopg://ana@host.neon.tech/pride?sslmode=require"
        )

    def test_sqlite_passa_intacto(self, monkeypatch):
        """AC-ARQ-17 — o padrão de desenvolvimento não é afetado pela normalização."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///./pride_vision.db")
        assert Settings().DATABASE_URL == "sqlite:///./pride_vision.db"

    def test_driver_ja_declarado_passa_intacto(self, monkeypatch):
        """AC-ARQ-17 — quem escolheu o driver não é sobrescrito."""
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://ana@host/pride")
        assert Settings().DATABASE_URL == "postgresql+asyncpg://ana@host/pride"

    def test_psycopg_ja_declarado_nao_e_duplicado(self, monkeypatch):
        """AC-ARQ-17 — normalizar duas vezes não pode produzir esquema inválido."""
        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://ana@host/pride")
        assert Settings().DATABASE_URL == "postgresql+psycopg://ana@host/pride"
