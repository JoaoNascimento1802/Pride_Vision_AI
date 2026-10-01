import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: Undefined resp at 147
text = text.replace('''        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth
        )

        assert resp.status_code == 200''', '''        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth
        )

        assert resp.status_code == 200''')

# Fix 2: Undefined resp at 281
text = text.replace('''        client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",
            json={"evidence_type": "commit", "description": "Desc", "reference": "https://ref"},
            headers=auth,
        )
        assert resp_post.status_code == 200''', '''        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",
            json={"evidence_type": "commit", "description": "Desc", "reference": "https://ref"},
            headers=auth,
        )
        assert resp_post.status_code == 200''')

# Fix 3: unused resp at 305, undefined resp_falha at 310
text = text.replace('''        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo"},
            headers=auth,
        )
        assert resp_falha.status_code == 422''', '''        resp_falha = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo"},
            headers=auth,
        )
        assert resp_falha.status_code == 422''')

# Fix 4: Undefined resp_sucesso at 323
text = text.replace('''        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo", "reason": "Motivo"},
            headers=auth,
        )
        assert resp_sucesso.status_code == 200''', '''        resp_sucesso = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo", "reason": "Motivo"},
            headers=auth,
        )
        assert resp_sucesso.status_code == 200''')

# Fix 5: Duplicate json at 342, undefined resp_sucesso at 345
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

# Fix 6: unused vuln_id at 361
text = text.replace('''        vuln_id = vuln["id"]

        vuln_id = resp_lista.json()[0]["id"]''', '''        vuln_id = vuln["id"]''')

# Fix 7: undefined resp_falha at 436, undefined resp at 438
text = text.replace('''        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aceito_como_risco", "reason": "Motivo risco"},
            headers=auth,
        )
        assert resp_falha.status_code == 422

        assert "detected_at" in resp.json() or "identificada_em" in resp.json()
        assert resp.json()["resolved_at"] is not None''', '''        resp_falha = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aceito_como_risco", "reason": "Motivo risco"},
            headers=auth,
        )
        assert resp_falha.status_code == 422
        
        # O teste de resolved_at devia verificar no resp_sucesso anterior
        # mas como não tem o objecto, vamos apenas pegar a vuln do DB para ver
        resp = client.get(f"/api/vulnerabilidades/{vuln_id}", headers=auth)
        assert "detected_at" in resp.json() or "identificada_em" in resp.json()
        assert resp.json()["resolved_at"] is not None''')

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 7")

