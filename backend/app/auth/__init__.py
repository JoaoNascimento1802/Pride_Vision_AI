# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""auth — Autenticação por token JWT."""

from app.auth.dependencies import usuario_atual
from app.auth.security import (
    SENHA_MAX_BYTES,
    SenhaMuitoLongaError,
    criar_token,
    gerar_hash_senha,
    ler_token,
    verificar_senha,
)

__all__ = [
    "SENHA_MAX_BYTES",
    "SenhaMuitoLongaError",
    "criar_token",
    "gerar_hash_senha",
    "ler_token",
    "usuario_atual",
    "verificar_senha",
]
