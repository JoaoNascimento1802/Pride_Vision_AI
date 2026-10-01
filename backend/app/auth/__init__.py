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
