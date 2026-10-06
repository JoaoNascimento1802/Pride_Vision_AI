# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/app/models/enums.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"runtime": "Runtime Security",', '"runtime": "Runtime Security",\n            "cloud_posture": "Cloud CSPM",')

with open('backend/app/models/enums.py', 'w', encoding='utf-8') as f:
    f.write(text)
