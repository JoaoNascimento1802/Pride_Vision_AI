# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/routers/dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("aplicacoes_em_risco=ranking[:10],", "aplicacoes_em_risco=ranking[:10],\n        cloud_posture=CloudPosture(aws_issues=2, gcp_issues=0, azure_issues=0, compliance_score=85)")

with open('backend/app/routers/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
