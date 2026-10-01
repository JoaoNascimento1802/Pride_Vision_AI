with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('''        assert resp_sucesso.status_code == 200
        assert resp_sucesso.json()["status"] == "falso_positivo"
        assert resp_sucesso.json()["false_positive_reason"] == "É código de teste"
        assert resp.status_code == 200
        assert resp.json()["false_positive_reason"] == "Motivo"''', '''        assert resp_sucesso.status_code == 200
        assert resp_sucesso.json()["status"] == "falso_positivo"
        assert resp_sucesso.json()["false_positive_reason"] == "Motivo"''')

text = text.replace('''        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")
        vuln_id = resp_lista.json()[0]["id"]''', '''        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")
        vuln_id = vuln["id"]''')

text = text.replace('''        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"},
            json={"status": "aceito_como_risco"},
            headers=auth,
        )
        assert resp_sucesso.status_code == 200''', '''        resp_sucesso = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"},
            headers=auth,
        )
        assert resp_sucesso.status_code == 200''')

text = text.replace('''        assert resp_sucesso.json()["status"] == "aceito_como_risco"
        assert resp_sucesso.json()["risk_acceptance_reason"] == "Baixo impacto no negócio"
        assert resp_sucesso.json()["risk_acceptance_approver_id"] == 1
        assert resp.status_code == 422''', '''        assert resp_sucesso.json()["status"] == "aceito_como_risco"
        assert resp_sucesso.json()["risk_acceptance_reason"] == "Baixo impacto no negócio"
        assert resp_sucesso.json()["risk_acceptance_approver_id"] == 1''')

text = text.replace('''        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")
        vuln_id = vuln["id"]

        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "em_analise"},
            headers=auth
        )''', '''        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")
        vuln_id = vuln["id"]

        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "em_analise"},
            headers=auth
        )''')

text = text.replace('''        resp_falha = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "corrigida"},
            headers=auth,
        )
        assert resp_falha.status_code == 422''', '''        resp_falha = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "corrigida"},
            headers=auth,
        )
        assert resp_falha.status_code == 422''')

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("done")

