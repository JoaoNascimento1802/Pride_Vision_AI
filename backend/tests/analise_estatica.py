"""
analise_estatica.py — Utilidades para os testes que verificam estrutura.

Vários ACs deste projeto são proibições arquiteturais: o motor de risco não pode
conhecer a IA (`AC-RISCO-17`), a IA não pode conhecer o motor de risco
(`AC-IA-13`), a plataforma não pode alcançar o alvo (`AC-FLUXO-03`). Todos são
provados olhando o que cada módulo importa.

Ler a árvore sintática, e não o texto, evita dois enganos: um `import` citado
dentro de comentário ou docstring contaria como violação, e um import feito
dentro de função passaria despercebido por uma busca linha a linha.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import ModuleType


def modulos_importados(alvo: ModuleType | Path) -> set[str]:
    """
    Nomes de módulo importados por um arquivo Python.

    Args:
        alvo: um módulo já importado ou o caminho do arquivo-fonte.

    Returns:
        Os nomes como aparecem no `import` — `app.services.ai_explainer` para
        `from app.services.ai_explainer import x`, `openai` para `import openai`.
    """
    caminho = Path(alvo.__file__ or "") if isinstance(alvo, ModuleType) else alvo
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    nomes: set[str] = set()

    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)

    return nomes


def importa_algum(alvo: ModuleType | Path, prefixos: tuple[str, ...]) -> set[str]:
    """Subconjunto dos módulos importados que começa com algum dos prefixos."""
    return {nome for nome in modulos_importados(alvo) if nome.startswith(prefixos)}
