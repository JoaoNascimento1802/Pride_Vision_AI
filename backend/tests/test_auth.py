# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes de cadastro, login e proteção das rotas — SDD/09-arquitetura.md.

"Login simples" é o que o PDF §10 pede. Simples não quer dizer frouxo: senha com
hash, token assinado e mensagem de erro que não revela quem está cadastrado.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.security import criar_token, gerar_hash_senha, ler_token, verificar_senha
from tests.conftest import SENHA_PADRAO


class TestHashDeSenha:
    def test_hash_nao_e_a_senha(self):
        """AC-LOGIN-01 — a senha nunca é guardada em texto."""
        assert gerar_hash_senha("segredo123") != "segredo123"

    def test_senhas_iguais_geram_hashes_diferentes(self):
        """AC-LOGIN-01 — o salt evita que dois usuários com a mesma senha se revelem."""
        assert gerar_hash_senha("segredo123") != gerar_hash_senha("segredo123")

    def test_verificacao_aceita_a_senha_correta(self):
        """AC-LOGIN-01 — o hash gravado valida a senha original."""
        assert verificar_senha("segredo123", gerar_hash_senha("segredo123"))

    def test_verificacao_recusa_a_senha_errada(self):
        """AC-LOGIN-01 — senha diferente não valida."""
        assert not verificar_senha("errada", gerar_hash_senha("segredo123"))

    def test_hash_corrompido_nao_levanta_erro(self):
        """AC-LOGIN-01 — hash inválido no banco recusa o login em vez de quebrar."""
        assert not verificar_senha("segredo123", "isto-nao-e-um-hash")


class TestToken:
    def test_token_carrega_o_usuario(self):
        """AC-LOGIN-02 — o token assinado identifica o usuário que o recebeu."""
        assert ler_token(criar_token(42, "ana@exemplo.com")) == 42

    def test_token_adulterado_e_recusado(self):
        """AC-LOGIN-06 — assinatura quebrada invalida o token."""
        token = criar_token(42, "ana@exemplo.com")
        assert ler_token(token[:-4] + "aaaa") is None

    def test_lixo_e_recusado(self):
        """AC-LOGIN-06 — texto que não é token não vira sessão."""
        assert ler_token("nao-e-um-token") is None


class TestRegistro:
    def test_cadastra_usuario(self, client: TestClient):
        """AC-LOGIN-01 — o registro cria o usuário e devolve seus dados."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "novo@exemplo.com", "nome": "Novo", "senha": SENHA_PADRAO},
        )
        assert r.status_code == 201
        assert r.json()["email"] == "novo@exemplo.com"

    def test_nunca_devolve_a_senha(self, client: TestClient):
        """AC-LOGIN-01 — nem a senha nem o hash aparecem na resposta."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "novo@exemplo.com", "nome": "Novo", "senha": SENHA_PADRAO},
        )
        corpo = r.text.lower()
        assert SENHA_PADRAO not in corpo
        assert "senha" not in r.json()

    def test_email_e_normalizado_para_minusculas(self, client: TestClient):
        """AC-LOGIN-08 — o login não depende de como o e-mail foi digitado."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "MAIUSCULO@Exemplo.com", "nome": "Teste", "senha": SENHA_PADRAO},
        )
        assert r.json()["email"] == "maiusculo@exemplo.com"

    def test_email_duplicado_e_recusado(self, client: TestClient, usuario_cadastrado):
        """AC-LOGIN-07 — e-mail já cadastrado responde 409."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": usuario_cadastrado["email"], "nome": "Outra", "senha": SENHA_PADRAO},
        )
        assert r.status_code == 409

    def test_duplicado_ignora_caixa_do_email(self, client: TestClient, usuario_cadastrado):
        """AC-LOGIN-07, AC-LOGIN-08 — mudar a caixa não cria conta paralela."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "ANA@EXEMPLO.COM", "nome": "Outra", "senha": SENHA_PADRAO},
        )
        assert r.status_code == 409

    def test_email_invalido_recusado(self, client: TestClient):
        """AC-LOGIN-E2 — e-mail em formato inválido responde 422."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "sem-arroba", "nome": "Teste", "senha": SENHA_PADRAO},
        )
        assert r.status_code == 422

    def test_senha_curta_recusada(self, client: TestClient):
        """AC-LOGIN-E3 — senha abaixo do mínimo responde 422."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "a@b.com", "nome": "Teste", "senha": "curta"},
        )
        assert r.status_code == 422

    def test_senha_acima_do_limite_do_bcrypt_recusada(self, client: TestClient):
        """AC-LOGIN-E1 — aceitar em silêncio faria senhas diferentes colidirem em 72 bytes."""
        r = client.post(
            "/api/auth/registrar",
            json={"email": "a@b.com", "nome": "Teste", "senha": "x" * 80},
        )
        assert r.status_code == 422


class TestLogin:
    def test_login_devolve_token(self, client: TestClient, usuario_cadastrado):
        """AC-LOGIN-02 — credenciais corretas devolvem token e dados do usuário."""
        r = client.post(
            "/api/auth/login",
            data={"username": usuario_cadastrado["email"], "password": SENHA_PADRAO},
        )
        assert r.status_code == 200
        assert r.json()["token_type"] == "bearer"
        assert r.json()["access_token"]
        assert r.json()["usuario"]["nome"] == "Ana Souza"

    def test_senha_errada_recusada(self, client: TestClient, usuario_cadastrado):
        """AC-LOGIN-03 — senha incorreta responde 401."""
        r = client.post(
            "/api/auth/login",
            data={"username": usuario_cadastrado["email"], "password": "errada"},
        )
        assert r.status_code == 401

    def test_usuario_inexistente_recusado(self, client: TestClient):
        """AC-LOGIN-03 — e-mail não cadastrado responde 401."""
        r = client.post(
            "/api/auth/login", data={"username": "ninguem@exemplo.com", "password": "x"}
        )
        assert r.status_code == 401

    def test_mensagem_nao_revela_se_o_email_existe(self, client: TestClient, usuario_cadastrado):
        """AC-LOGIN-04 — mensagens distintas permitiriam enumerar os e-mails cadastrados."""
        existente = client.post(
            "/api/auth/login",
            data={"username": usuario_cadastrado["email"], "password": "errada"},
        )
        inexistente = client.post(
            "/api/auth/login", data={"username": "ninguem@exemplo.com", "password": "errada"}
        )
        assert existente.json()["detail"] == inexistente.json()["detail"]


class TestRotasProtegidas:
    def test_sem_token_recusado(self, client: TestClient):
        """AC-LOGIN-06 — rota protegida sem token responde 401."""
        assert client.get("/api/aplicacoes").status_code == 401

    def test_token_invalido_recusado(self, client: TestClient):
        """AC-LOGIN-06 — token inválido responde 401."""
        r = client.get("/api/aplicacoes", headers={"Authorization": "Bearer lixo"})
        assert r.status_code == 401

    def test_token_de_usuario_removido_recusado(self, client: TestClient, db):
        """AC-LOGIN-06 — token válido de quem não existe mais não pode ser aceito."""
        from app.models import User

        token = criar_token(99999, "fantasma@exemplo.com")
        assert db.get(User, 99999) is None
        r = client.get("/api/aplicacoes", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_com_token_liberado(self, client: TestClient, auth):
        """AC-LOGIN-02 — o token emitido no login abre as rotas protegidas."""
        assert client.get("/api/aplicacoes", headers=auth).status_code == 200

    def test_eu_devolve_o_usuario_do_token(self, client: TestClient, auth):
        """AC-LOGIN-05 — a rota de identificação devolve o usuário do token."""
        r = client.get("/api/auth/eu", headers=auth)
        assert r.status_code == 200
        assert r.json()["email"] == "ana@exemplo.com"
