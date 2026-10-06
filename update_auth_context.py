# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('frontend/src/auth/AuthContext.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '  sair: () => void\n}',
    '  sair: () => void\n  tenantId: string | null\n  setTenantId: (id: string) => void\n}'
)

text = text.replace(
    'const [carregando, setCarregando] = useState(() => Boolean(lerToken()))',
    'const [carregando, setCarregando] = useState(() => Boolean(lerToken()))\n  const [tenantId, setTenantIdState] = useState(() => localStorage.getItem(\'@pride:tenant_id\'))\n\n  const setTenantId = useCallback((id: string) => {\n    localStorage.setItem(\'@pride:tenant_id\', id)\n    setTenantIdState(id)\n    window.location.reload() // Reload to fetch fresh data for the new tenant\n  }, [])'
)

text = text.replace(
    'if (!cancelado) setUsuario(dados)',
    'if (!cancelado) {\n          setUsuario(dados)\n          if (dados.tenants?.length && !localStorage.getItem(\'@pride:tenant_id\')) {\n            localStorage.setItem(\'@pride:tenant_id\', dados.tenants[0].id.toString())\n            setTenantIdState(dados.tenants[0].id.toString())\n          }\n        }'
)

text = text.replace(
    'guardarToken(resposta.access_token)',
    'guardarToken(resposta.access_token)\n    if (resposta.usuario.tenants?.length) {\n      localStorage.setItem(\'@pride:tenant_id\', resposta.usuario.tenants[0].id.toString())\n      setTenantIdState(resposta.usuario.tenants[0].id.toString())\n    }'
)

text = text.replace(
    'setUsuario(null)\n  }, [])',
    'setUsuario(null)\n    localStorage.removeItem(\'@pride:tenant_id\')\n    setTenantIdState(null)\n  }, [])'
)

text = text.replace(
    '() => ({ usuario, carregando, entrar, sair }),\n    [usuario, carregando, entrar, sair],',
    '() => ({ usuario, carregando, entrar, sair, tenantId, setTenantId }),\n    [usuario, carregando, entrar, sair, tenantId, setTenantId],'
)

with open('frontend/src/auth/AuthContext.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
