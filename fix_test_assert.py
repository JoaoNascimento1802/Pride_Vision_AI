# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """    res = client.get("/api/v1/applications", headers=auth)
    assert res.status_code == 200

    h2 = auth.copy()
    h2["X-Tenant-ID"] = "2"
    res2 = client.get("/api/v1/applications", headers=h2)
    assert res2.status_code == 403"""

text = re.sub(r'    # Request without explicit tenant ID uses default \(1\)[\s\S]*?assert res2.status_code == 403', replacement, text)

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
