# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
security.py — Hash de senha e emissão/validação de token.

Duas responsabilidades, ambas puras: transformar senha em hash e transformar
identidade em token. Nada aqui toca o banco.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.config import settings

# bcrypt trunca silenciosamente em 72 bytes. Em vez de aceitar uma senha longa e
# validar só os primeiros 72 bytes — o que faria senhas diferentes colidirem —,
# o limite é recusado explicitamente na entrada.
SENHA_MAX_BYTES = 72


class SenhaMuitoLongaError(ValueError):
    """Senha excede o limite que o bcrypt consegue processar."""


def gerar_hash_senha(senha: str) -> str:
    """
    Retorna o hash bcrypt da senha.

    Raises:
        SenhaMuitoLongaError: se a senha passar de 72 bytes em UTF-8.
    """
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > SENHA_MAX_BYTES:
        raise SenhaMuitoLongaError(
            f"A senha excede o limite de {SENHA_MAX_BYTES} bytes suportado pelo bcrypt."
        )
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """
    Confere a senha contra o hash.

    Retorna False em vez de propagar erro quando o hash está corrompido ou a
    senha é longa demais: do ponto de vista do login, o resultado é o mesmo.
    """
    try:
        senha_bytes = senha.encode("utf-8")
        if len(senha_bytes) > SENHA_MAX_BYTES:
            return False
        return bcrypt.checkpw(senha_bytes, senha_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def criar_token(usuario_id: int, email: str) -> str:
    """
    Emite um JWT assinado identificando o usuário.

    O `sub` vai como string porque é o que a especificação do JWT exige; alguns
    validadores recusam `sub` numérico.
    """
    agora = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(usuario_id),
        "email": email,
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.TOKEN_EXPIRA_MINUTOS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def ler_token(token: str) -> int | None:
    """
    Valida o token e devolve o id do usuário, ou None se for inválido.

    Cobre assinatura errada, token expirado e formato corrompido — todos são
    tratados igualmente como "não autenticado".
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

    sub = payload.get("sub")
    if sub is None:
        return None

    try:
        return int(sub)
    except (TypeError, ValueError):
        return None
