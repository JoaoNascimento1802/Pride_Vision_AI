# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from app.models.application import Application', 'from app.models.application import Application\nfrom app.models.enums import Exposicao, Ambiente, Importancia')
text = text.replace('exposicao="INTERNA"', 'exposicao=Exposicao.INTERNA')
text = text.replace('ambiente="DESENVOLVIMENTO"', 'ambiente=Ambiente.DESENVOLVIMENTO')
text = text.replace('importancia="BAIXA"', 'importancia=Importancia.BAIXA')

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
