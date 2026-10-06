# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/tests/test_runtime.py', 'r', encoding='utf-8') as f:
    text = f.read()

import uuid
text = re.sub(r'App Test RT[12] [0-9\.]+', lambda x: f'App Test RT {uuid.uuid4().hex[:8]}', text)

with open('backend/tests/test_runtime.py', 'w', encoding='utf-8') as f:
    f.write(text)
