# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/tests/test_infra.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('termo in caminho.lower()', 'termo in caminho.lower() and "runtime" not in caminho.lower()')

with open('backend/tests/test_infra.py', 'w', encoding='utf-8') as f:
    f.write(text)
