import re

with open('backend/tests/test_vulnerabilities.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    def test_contagem_por_status_cobre_todos_os_nove(self, client: TestClient, auth, cenario):
        \"\"\"AC-STATUS-08 — o dashboard traz a contagem por status, agora com os nove status do Remediation.\"\"\"
        dados = client.get("/api/dashboard", headers=auth).json()
        assert [i["valor"] for i in dados["por_status"]] == [
        assert set([i["valor"] for i in dados["por_status"]]) == {
            "nova",
            "em_analise",
            "em_correcao",
            "aguardando_validacao",
            "excecao_temporaria",
            "corrigida",
            "falso_positivo",
        ]
            "aceito_como_risco",
            "duplicado",
        }"""

replacement = """    def test_contagem_por_status_cobre_todos_os_nove(self, client: TestClient, auth, cenario):
        \"\"\"AC-STATUS-08 — o dashboard traz a contagem por status, agora com os nove status do Remediation.\"\"\"
        dados = client.get("/api/dashboard", headers=auth).json()
        assert set([i["valor"] for i in dados["por_status"]]) == {
            "nova",
            "em_analise",
            "em_correcao",
            "aguardando_validacao",
            "excecao_temporaria",
            "corrigida",
            "falso_positivo",
            "aceito_como_risco",
            "duplicado",
        }"""

content = content.replace(target, replacement)

with open('backend/tests/test_vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")

