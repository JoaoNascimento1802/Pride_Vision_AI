# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from pathlib import Path

content = Path('backend/app/services/risk_engine.py').read_text(encoding='utf-8')

old_str = """    # Encontrada por apenas uma das ferramentas
    origem = "análise estática (Semgrep)" if grupo.encontrada_semgrep else "varredura dinâmica (Nuclei)"
    faltando = (
        "sem confirmação dinâmica pelo Nuclei"
        if grupo.encontrada_semgrep
        else "sem correspondência no código analisado pelo Semgrep"
    )"""

new_str = """    # Encontrada por apenas uma das ferramentas
    if grupo.encontrada_semgrep:
        origem = "análise estática (Semgrep)"
        faltando = "sem confirmação dinâmica pelo Nuclei"
    elif grupo.confirmada_nuclei:
        origem = "varredura dinâmica (Nuclei)"
        faltando = "sem correspondência no código analisado pelo Semgrep"
    else:
        origem = "análise de composição (Trivy)"
        faltando = "sem confirmação de outras ferramentas" """

if old_str in content:
    content = content.replace(old_str, new_str)
    Path('backend/app/services/risk_engine.py').write_text(content, encoding='utf-8')

