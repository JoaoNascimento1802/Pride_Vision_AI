# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/auth/dependencies.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('usuario.role = tu.role', 'usuario.current_role = tu.role')
text = text.replace('if self.permission not in get_permissions(user.role):', 'if self.permission not in get_permissions(getattr(user, "current_role", user.role)):')

with open('backend/app/auth/dependencies.py', 'w', encoding='utf-8') as f:
    f.write(text)
