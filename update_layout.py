# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('frontend/src/components/Layout.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """          <div className="flex items-center gap-3 text-sm">
            {usuario?.tenants && usuario.tenants.length > 1 && (
              <select
                value={tenantId || ''}
                onChange={(e) => setTenantId(e.target.value)}
                className="rounded-md border-slate-300 py-1 pl-3 pr-8 text-sm focus:border-violet-500 focus:outline-none focus:ring-violet-500"
              >
                {usuario.tenants.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}
            <span className="text-slate-600">{usuario?.nome}</span>"""

text = text.replace('          <div className="flex items-center gap-3 text-sm">\n            <span className="text-slate-600">{usuario?.nome}</span>', replacement)

text = text.replace('const { usuario, sair } = useAuth()', 'const { usuario, sair, tenantId, setTenantId } = useAuth()')

with open('frontend/src/components/Layout.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
