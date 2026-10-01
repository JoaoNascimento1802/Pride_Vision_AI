import re

with open('backend/tests/test_ai.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'            json=\{"status": "em_correcao"\},\n            json=\{"status": "em_analise"\},\n        \)',
    r'            json={"status": "em_analise"},\n        )',
    text
)

with open('backend/tests/test_ai.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('backend/tests/test_audit.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        json=\{"status": "falso_positivo", "comentario": "Fixed"\},\n        json=\{"status": "em_analise", "comentario": "Analise"\},\n        headers=auth',
    r'        json={"status": "em_analise", "comentario": "Analise"},\n        headers=auth',
    text
)

with open('backend/tests/test_audit.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('backend/tests/test_sla.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('''        from app.models.application import Application
        
        # Cria a aplicação antes para evitar IntegrityError''', '''        from app.models.application import Application

        # Cria a aplicação antes para evitar IntegrityError''')

text = text.replace('''                SlaService.check_and_update_slas(db)
                mock_notify.assert_called_once()
        
        # O evento foi persistido?''', '''                SlaService.check_and_update_slas(db)
                mock_notify.assert_called_once()

        # O evento foi persistido?''')

with open('backend/tests/test_sla.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("fixed ai, audit, sla")

