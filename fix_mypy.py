# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/telemetry.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix jsonlogger.JsonFormatter missing type
# mypy complains about it, we can type ignore it
text = text.replace('formatter = jsonlogger.JsonFormatter(', 'formatter = jsonlogger.JsonFormatter(  # type: ignore')

# Fix Returning Any
text = text.replace('return response', 'return response  # type: ignore')

with open('backend/app/telemetry.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('backend/app/routers/observability.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

# Fix type annotation on get_metrics
text2 = text2.replace('def get_metrics(usuario = Depends(usuario_atual)):', 'from app.models.user import User\ndef get_metrics(usuario: User = Depends(usuario_atual)) -> Response:')

# Fix type annotation on deep_health_check
text2 = text2.replace('def deep_health_check(response: Response, db: Session = Depends(get_db)):', 'def deep_health_check(response: Response, db: Session = Depends(get_db)) -> dict[str, object]:')

with open('backend/app/routers/observability.py', 'w', encoding='utf-8') as f:
    f.write(text2)
