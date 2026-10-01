"""
popular_demo.py — Popula a plataforma com um cenário de demonstração.

Cadastra quatro aplicações em contextos diferentes e envia os MESMOS relatórios
para todas. O ponto é justamente esse: o mesmo achado recebe prioridades
distintas conforme o ambiente, a exposição e a importância da aplicação — que é
o que diferencia uma plataforma de ASPM de um comparador de arquivos.

Uso, com o backend rodando:

    python popular_demo.py
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8002"
EMAIL = "admin@pride.com"
SENHA = "admin"

# ---------------------------------------------------------------------------
# Relatórios de exemplo — dados fictícios, domínio inexistente
# ---------------------------------------------------------------------------

SEMGREP = json.dumps(
    {
        "results": [
            {
                "check_id": "python.flask.security.xss.reflected-xss",
                "path": "src/views/busca.py",
                "start": {"line": 42},
                "extra": {
                    "message": "Parâmetro de busca renderizado no HTML sem escaping.",
                    "severity": "ERROR",
                    "metadata": {"cwe": ["CWE-79"], "owasp": ["A03:2021"]},
                },
            },
            {
                "check_id": "python.django.security.injection.sql-injection",
                "path": "src/api/usuarios.py",
                "start": {"line": 87},
                "extra": {
                    "message": "SQL montado por concatenação de string.",
                    "severity": "ERROR",
                    "metadata": {"cwe": ["CWE-89"], "route": "/api/usuarios"},
                },
            },
            {
                "check_id": "python.lang.security.audit.command-injection",
                "path": "src/jobs/relatorios.py",
                "start": {"line": 15},
                "extra": {
                    "message": "Comando do sistema montado com entrada do usuário.",
                    "severity": "ERROR",
                    "metadata": {"cwe": ["CWE-78"], "route": "/relatorios"},
                },
            },
        ],
        "version": "1.86.0",
    }
)

# Formato real do Nuclei v3: a resposta HTTP inteira vai no campo "response"
NUCLEI = "\n".join(
    [
        json.dumps(
            {
                "template-id": "reflected-xss",
                "info": {"name": "Reflected Cross-Site Scripting", "severity": "high"},
                "matched-at": "https://demo.target.com/busca?q=%3Cscript%3E",
                "response": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html></html>",
                "extracted-results": ["<script>alert(1)</script>"],
            }
        ),
        json.dumps(
            {
                "template-id": "remote-code-execution",
                "info": {"name": "Remote Code Execution", "severity": "critical"},
                "matched-at": "https://demo.target.com/relatorios",
                "response": "HTTP/1.1 500 Internal Server Error\r\n\r\n",
            }
        ),
        json.dumps(
            {
                "template-id": "http-missing-security-headers",
                "info": {"name": "Missing Security Headers", "severity": "info"},
                "matched-at": "https://demo.target.com/painel",
            }
        ),
    ]
)

# As mesmas varreduras em contextos diferentes, para a demonstração mostrar que
# o contexto de negócio muda a prioridade. O Site Institucional recebe só o
# Nuclei de propósito: o RCE fica sem confirmação cruzada (base Alto pela
# matriz) e sobe para Crítico pela severidade — é o caso que exercita o quinto
# fator da priorização.
APLICACOES = [
    ("Portal do Cliente", "Time Web", "producao", "internet", "alta",
     "https://portal.exemplo.com", True, True),
    ("API de Pagamentos", "Time Core", "producao", "interna", "alta", None, True, False),
    ("Site Institucional", "Time Marketing", "producao", "internet", "media",
     "https://www.exemplo.com", False, True),
    ("Painel Interno", "Time Ops", "homologacao", "interna", "media", None, True, True),
    ("Sandbox de Testes", "Time QA", "teste", "interna", "baixa", None, True, True),
]


def chamar(metodo, caminho, *, json_body=None, form=None, token=None, arquivo=None, nome=None):
    cabecalhos = {}
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"

    if arquivo is not None:
        limite = "----pride-demo"
        corpo = (
            f"--{limite}\r\n"
            f'Content-Disposition: form-data; name="arquivo"; filename="{nome}"\r\n\r\n'
            f"{arquivo}\r\n--{limite}--\r\n"
        ).encode()
        cabecalhos["Content-Type"] = f"multipart/form-data; boundary={limite}"
    elif form is not None:
        corpo = urllib.parse.urlencode(form).encode()
        cabecalhos["Content-Type"] = "application/x-www-form-urlencoded"
    elif json_body is not None:
        corpo = json.dumps(json_body).encode()
        cabecalhos["Content-Type"] = "application/json"
    else:
        corpo = None

    pedido = urllib.request.Request(BASE + caminho, data=corpo, headers=cabecalhos, method=metodo)
    with urllib.request.urlopen(pedido) as resposta:
        texto = resposta.read().decode()
        return json.loads(texto) if texto else None


def main() -> int:
    try:
        chamar("GET", "/api/saude")
    except urllib.error.URLError:
        print(f"[ERRO] O backend não respondeu em {BASE}.", file=sys.stderr)
        print("       Suba-o com: python -m uvicorn app.main:app --port 8002", file=sys.stderr)
        return 1

    # O usuário pode já existir de uma execução anterior
    try:
        pass # chamar\("POST", "/api/auth/registrar",
               # json_body={"email": EMAIL, "nome": "Ana Souza", "senha": SENHA})
        print(f"usuário criado: {EMAIL}")
    except urllib.error.HTTPError as exc:
        if exc.code != 409:
            raise
        print(f"usuário já existia: {EMAIL}")

    token = chamar("POST", "/api/auth/login", form={"username": EMAIL, "password": SENHA})[
        "access_token"
    ]

    print()
    for nome, resp, ambiente, exposicao, importancia, url, com_semgrep, com_nuclei in APLICACOES:
        app = chamar("POST", "/api/aplicacoes", token=token, json_body={
            "nome": nome, "responsavel": resp, "ambiente": ambiente,
            "exposicao": exposicao, "importancia": importancia, "url": url,
        })
        if com_semgrep:
            chamar("POST", f"/api/aplicacoes/{app['id']}/uploads/semgrep",
                   token=token, arquivo=SEMGREP, nome="semgrep.json")
        if com_nuclei:
            chamar("POST", f"/api/aplicacoes/{app['id']}/uploads/nuclei",
                   token=token, arquivo=NUCLEI, nome="nuclei.jsonl")
        print(f"  {nome:22} {ambiente:12} {exposicao:9} {importancia}")

    # Um pouco de acompanhamento, para o dashboard não ficar todo "Nova"
    vulns = chamar("GET", "/api/vulnerabilidades", token=token)
    chamar("PATCH", f"/api/vulnerabilidades/{vulns[0]['id']}/status", token=token,
           json_body={"status": "em_correcao", "comentario": "Time web assumiu a correção."})
    chamar("PATCH", f"/api/vulnerabilidades/{vulns[-1]['id']}/status", token=token,
           json_body={"status": "falso_positivo", "comentario": "Endpoint já desativado."})

    painel = chamar("GET", "/api/dashboard", token=token)
    print()
    print("dashboard:", {k: v for k, v in painel.items() if k.startswith("total")})
    print("por risco:", {i["label"]: i["total"] for i in painel["por_risco"]})
    print()
    print(f"Pronto. Entre em http://localhost:5173 com {EMAIL} / {SENHA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())





