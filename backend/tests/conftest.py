"""
conftest.py — Fixtures compartilhadas.

Cada teste recebe um banco em memória próprio, criado e destruído no escopo do
teste. Nenhum teste enxerga dados de outro, e nada toca o banco de trabalho.
"""

from __future__ import annotations

import os

# Precisa vir antes de qualquer import de `app`: o engine global é montado na
# importação de app.database, lendo esta variável.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
# Fixa para os testes, e com 32+ bytes para não disparar o aviso de chave fraca
os.environ.setdefault(
    "SECRET_KEY", "chave-fixa-de-testes-com-comprimento-suficiente-para-hmac-sha256"
)

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.database import Base, criar_engine, get_db  # noqa: E402
from app.main import app  # noqa: E402

SENHA_PADRAO = "senha-de-teste-123"


@pytest.fixture
def db() -> Iterator[Session]:
    """Sessão ligada a um banco em memória exclusivo deste teste."""
    engine = criar_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)


    fabrica = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    sessao = fabrica()

    from app.models.tenant import Tenant
    if not sessao.query(Tenant).filter_by(id=1).first():
        sessao.add(Tenant(id=1, name="Default Organization", domain="default.local"))
        sessao.commit()

    try:
        yield sessao
    finally:
        sessao.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    """Cliente HTTP com o banco do teste injetado no lugar do global."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def usuario_cadastrado(client: TestClient, db: Session) -> dict[str, str]:
    """Cria um usuário e devolve suas credenciais (promovido a ADMIN)."""
    email = "ana@exemplo.com"
    client.post(
        "/api/auth/registrar",
        json={"email": email, "nome": "Ana Souza", "senha": SENHA_PADRAO},
    )

    from app.models.enums import Role
    from app.models.user import User

    user = db.query(User).filter(User.email == email).first()
    if user:
        user.role = Role.ADMIN
        db.commit()

    return {"email": email, "senha": SENHA_PADRAO}


@pytest.fixture
def auth(client: TestClient, usuario_cadastrado: dict[str, str]) -> dict[str, str]:
    """Cabeçalho Authorization de um usuário autenticado."""
    resposta = client.post(
        "/api/auth/login",
        data={
            "username": usuario_cadastrado["email"],
            "password": usuario_cadastrado["senha"],
        },
    )
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def aplicacao_producao(client: TestClient, auth: dict[str, str]) -> dict[str, object]:
    """
    Aplicação em produção, exposta à internet e de alta importância.

    É o contexto de maior risco da especificação — o que transforma um achado
    correlacionado em Crítico.
    """
    resposta = client.post(
        "/api/aplicacoes",
        headers=auth,
        json={
            "nome": "Portal do Cliente",
            "responsavel": "Time Web",
            "ambiente": "producao",
            "exposicao": "internet",
            "importancia": "alta",
            "url": "https://portal.exemplo.com",
        },
    )
    return dict(resposta.json())
