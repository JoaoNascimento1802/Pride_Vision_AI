# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
database.py — Engine, sessão e base declarativa do SQLAlchemy.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextvars import ContextVar
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker, with_loader_criteria
from sqlalchemy.pool import StaticPool

from app.config import settings

current_tenant_id: ContextVar[int | None] = ContextVar("current_tenant_id", default=None)



@event.listens_for(Session, "do_orm_execute")
def _add_tenant_filter(execute_state: Any) -> None:
    tenant_id = current_tenant_id.get()
    if tenant_id is not None:
        # Avoid infinite recursion when querying Tenant itself
        if execute_state.is_select and not execute_state.is_column_load and not execute_state.is_relationship_load:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Base,
                    lambda cls: cls.tenant_id == tenant_id if hasattr(cls, "tenant_id") else True,  # type: ignore
                    include_aliases=True,
                )
            )

class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os modelos."""


def _e_sqlite_em_memoria(url: str) -> bool:
    return url.startswith("sqlite") and (":memory:" in url or url.endswith("sqlite://"))


def criar_engine(url: str):  # type: ignore[no-untyped-def]
    """
    Monta o engine com os ajustes que cada tipo de banco exige.

    SQLite em arquivo: `check_same_thread=False`, porque o FastAPI atende
    requisições em threads diferentes e o SQLite recusa, por padrão, o uso da
    conexão fora da thread que a criou.

    SQLite em memória: além disso, `StaticPool`. Sem ele cada conexão nova
    recebe um banco vazio e distinto — as tabelas criadas na inicialização
    simplesmente não existiriam nas requisições seguintes.
    """
    if _e_sqlite_em_memoria(url):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

    # pool_pre_ping evita erro de conexão morta após ociosidade na hospedagem
    return create_engine(url, pool_pre_ping=True)


@event.listens_for(Engine, "connect")
def _ativar_chaves_estrangeiras(dbapi_connection: object, _record: object) -> None:
    """
    Liga a verificação de chaves estrangeiras no SQLite.

    O SQLite ignora chaves estrangeiras por padrão, o que torna inertes todos os
    `ondelete="CASCADE"` declarados nos modelos: apagar uma aplicação deixaria
    para trás achados e uploads órfãos, e o dashboard passaria a contar
    vulnerabilidades de aplicações que não existem mais (`AC-INV-09`).

    Ligado por evento de conexão porque o PRAGMA vale por conexão, não por banco.

    A guarda de dialeto não é zelo: o evento é registrado na **classe** `Engine`,
    então dispara para qualquer banco. No Postgres o PRAGMA é sintaxe inválida, e
    capturar o erro não basta — ele aborta a transação, e todo statement seguinte
    na mesma conexão falha com `InFailedSqlTransaction`. Silenciar a exceção,
    como se fazia aqui antes, deixava toda conexão Postgres inutilizável sem uma
    linha de log. Ver `AC-ARQ-18`.
    """
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Criados sob demanda, nunca na importação. Ver `obter_engine`.
_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def obter_engine() -> Engine:
    """
    O engine da aplicação, montado na primeira vez que alguém precisa dele.

    Criar o engine na importação parece inofensivo e não é: `create_engine`
    resolve o dialeto e **importa o driver na hora**. Driver ausente do pacote
    ou esquema inválido viram, então, erro de importação — e este módulo deixa
    de carregar, levando junto todo módulo que depende dele, que é o produto
    inteiro.

    Numa hospedagem serverless o efeito é o pior possível: a função morre antes
    de qualquer rota existir, e até `GET /api/opcoes`, que só enumera constantes
    e nunca encosta no banco, passa a responder o erro genérico do provedor.
    Nenhum log da aplicação chega a ser escrito, porque nada da aplicação chegou
    a rodar.

    Adiando para o primeiro uso, a aplicação sempre importa e sempre consegue
    relatar o que há de errado. Ver `AC-ARQ-20`.
    """
    global _engine, _SessionLocal

    if _engine is None:
        _engine = criar_engine(settings.DATABASE_URL)
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

    return _engine


def _fabrica_de_sessoes() -> sessionmaker[Session]:
    """A fábrica de sessões ligada ao engine, criando os dois se preciso."""
    obter_engine()

    if _SessionLocal is None:  # pragma: no cover — obter_engine sempre define
        raise RuntimeError("fábrica de sessões não inicializada")

    return _SessionLocal


def get_db() -> Iterator[Session]:
    """
    Dependência do FastAPI que entrega uma sessão e garante o fechamento.

    Usada como `db: Session = Depends(get_db)` nas rotas.
    """
    db = _fabrica_de_sessoes()()
    try:
        yield db
    finally:
        db.close()


def criar_tabelas() -> None:
    """
    Cria as tabelas que ainda não existem.

    Para uma aplicação deste porte isso substitui um sistema de migrações. Se o
    esquema mudar depois de haver dados em produção, será preciso migrar à mão
    ou adotar Alembic.
    """
    # Importar os modelos registra as tabelas no metadata da Base
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=obter_engine())
