import re

with open('backend/tests/test_ai.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'    def test_analise_nao_altera_o_status\(\n        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch\n    \):\n        """AC-IA-15 — a IA não aprova correção: o acompanhamento fica intacto\."""\n        client\.patch\(\n            f"/api/vulnerabilidades/\{vulnerabilidade_id\}/status",\n            headers=auth,\n            json=\{"status": "em_analise"\},\n        \)',
    r'    def test_analise_nao_altera_o_status(\n        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch\n    ):\n        """AC-IA-15 — a IA não aprova correção: o acompanhamento fica intacto."""\n        client.patch(\n            f"/api/vulnerabilidades/{vulnerabilidade_id}/status",\n            headers=auth,\n            json={"status": "em_analise"},\n        )\n        client.patch(\n            f"/api/vulnerabilidades/{vulnerabilidade_id}/status",\n            headers=auth,\n            json={"status": "em_correcao"},\n        )',
    text
)

with open('backend/tests/test_ai.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed ai test")

