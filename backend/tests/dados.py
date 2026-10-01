"""
dados.py — Relatórios de exemplo usados nos testes.

Dados fictícios: o domínio `demo.target.com` não existe, e nenhum valor aqui
corresponde a sistema real.
"""

from __future__ import annotations

import json

# XSS sem `metadata.route`: o endpoint sai do caminho do arquivo e ainda assim
# precisa correlacionar com "/busca" pelas regras de compatibilidade.
SEMGREP_XSS_SQLI = json.dumps(
    {
        "results": [
            {
                "check_id": "python.flask.security.xss.reflected-xss",
                "path": "src/views/busca.py",
                "start": {"line": 42, "col": 5},
                "extra": {
                    "message": "Parâmetro renderizado no HTML sem escaping.",
                    "severity": "ERROR",
                    "metadata": {"cwe": ["CWE-79"], "owasp": ["A03:2021"]},
                },
            },
            {
                "check_id": "python.django.security.injection.sql-injection",
                "path": "src/api/usuarios.py",
                "start": {"line": 87, "col": 12},
                "extra": {
                    "message": "SQL montado por concatenação de string.",
                    "severity": "ERROR",
                    "metadata": {"cwe": ["CWE-89"], "route": "/api/usuarios"},
                },
            },
        ],
        "version": "1.86.0",
    }
)

# Confirma o XSS do Semgrep no mesmo endpoint. Usa o formato real do Nuclei v3,
# em que "response" traz a resposta HTTP inteira.
NUCLEI_XSS = json.dumps(
    {
        "template-id": "reflected-xss",
        "info": {"name": "Reflected Cross-Site Scripting", "severity": "high"},
        "type": "http",
        "matched-at": "https://demo.target.com/busca?q=%3Cscript%3E",
        "response": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html></html>",
        "extracted-results": ["<script>alert(1)</script>"],
    }
)

# Achado informativo, sem evidência: exercita a regra do "achado teórico"
NUCLEI_INFORMATIVO = json.dumps(
    {
        "template-id": "http-missing-security-headers",
        "info": {"name": "Missing Security Headers", "severity": "info"},
        "type": "http",
        "matched-at": "https://demo.target.com/painel",
    }
)

SEMGREP_VAZIO = json.dumps({"results": []})

SEMGREP_COM_ENTRADA_INVALIDA = json.dumps(
    {
        "results": [
            {
                "check_id": "regra.valida",
                "path": "src/a.py",
                "start": {"line": 1},
                "extra": {"message": "ok", "severity": "ERROR"},
            },
            {
                # Sem start.line: precisa ser descartado com aviso
                "check_id": "regra.incompleta",
                "path": "src/b.py",
                "extra": {"message": "faltando linha", "severity": "ERROR"},
            },
        ]
    }
)

NUCLEI_COM_LINHA_INVALIDA = "\n".join([NUCLEI_XSS, "{isto não é json", "", NUCLEI_INFORMATIVO])


def arquivo(conteudo: str, nome: str) -> dict[str, tuple[str, bytes]]:
    """Monta o parâmetro `files` do TestClient."""
    return {"arquivo": (nome, conteudo.encode("utf-8"))}


def arquivo_bruto(conteudo: bytes, nome: str) -> dict[str, tuple[str, bytes]]:
    """
    Versão de `arquivo` para bytes que não formam UTF-8 válido.

    Existe porque o AC-ING-E4 exige provar a recusa de arquivo mal codificado, e
    não há como produzir esses bytes a partir de uma string já decodificada.
    """
    return {"arquivo": (nome, conteudo)}
