with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("_habilitar_saida_utf8()\n\n    # Falhar aqui", "_habilitar_saida_utf8()\n    setup_telemetry()\n\n    # Falhar aqui")

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
