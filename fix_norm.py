# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import sys

with open('backend/app/services/normalizer.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('titulo=item.get("titulo", "API Security Finding"),', 'regra_id=item.get("titulo", "API Security Finding"),')
text = text.replace('descricao=item.get("descricao", ""),', 'mensagem=item.get("descricao", ""),')
text = text.replace('log=item.get("log", ""),', 'evidencia=item.get("log", ""),')
text = text.replace('ferramenta=item.get("ferramenta", "api_security"),', 'origem=item.get("ferramenta", "api_security"),')

with open('backend/app/services/normalizer.py', 'w', encoding='utf-8') as f:
    f.write(text)
