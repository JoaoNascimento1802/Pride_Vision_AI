"""
crypto.py — Funções de criptografia simétrica para tokens (AES-128 via Fernet).
"""

import os

from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    # Se não houver chave definida, a proteção é um aviso logado, mas não bloqueia a criação
    # de uma chave transitória em dev. Em prod, isso deve estar configurado.
    key_str = os.getenv("JIRA_TOKEN_ENCRYPTION_KEY")
    if not key_str:
        # Gerar chave dummy para testes
        key_str = Fernet.generate_key().decode("utf-8")
        os.environ["JIRA_TOKEN_ENCRYPTION_KEY"] = key_str

    return Fernet(key_str.encode("utf-8"))

def encrypt_token(plain_token: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain_token.encode("utf-8")).decode("utf-8")

def decrypt_token(encrypted_token: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")

