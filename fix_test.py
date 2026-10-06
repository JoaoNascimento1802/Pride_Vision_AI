# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Application(nome="App T1", tenant_id=1', 'Application(nome="App T1", responsavel="TI", url="http://", tenant_id=1')
text = text.replace('Application(nome="App T2", tenant_id=2', 'Application(nome="App T2", responsavel="TI", url="http://", tenant_id=2')

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
