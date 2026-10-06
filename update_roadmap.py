# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('ROADMAP_IMPLEMENTACAO.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('⚪ Multi-tenancy / SSO corporativo', '✅ Multi-tenancy / SSO corporativo')

with open('ROADMAP_IMPLEMENTACAO.md', 'w', encoding='utf-8') as f:
    f.write(text)
