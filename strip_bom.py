# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/routers/cspm.py', 'rb') as f:
    content = f.read()

if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    with open('backend/app/routers/cspm.py', 'wb') as f:
        f.write(content)

