# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("_habilitar_saida_utf8()\n\n    # Falhar aqui", "_habilitar_saida_utf8()\n    setup_telemetry()\n\n    # Falhar aqui")

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
