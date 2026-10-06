# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/database.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('from typing import Any\n', '')
text = 'from typing import Any\n' + text
with open('backend/app/database.py', 'w', encoding='utf-8') as f:
    f.write(text)
