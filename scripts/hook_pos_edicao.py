# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
hook_pos_edicao.py — Hook PostToolUse do Claude Code.

Roda depois de cada Edit/Write e devolve, na hora, o que costuma ser descoberto
tarde demais: erro de sintaxe, lint sujo, AC órfão e violação da regra 3 do
`AGENTS.md` (a IA não pode participar da decisão de risco).

Recebe o JSON do hook no stdin. Sai sempre com código 0: o hook informa, não
bloqueia — quem decide o que fazer com o achado é quem está conduzindo a sessão.

Feito em Python, e não em bash+jq, porque o ambiente principal deste projeto é
Windows e o Python já é dependência obrigatória do backend.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BACKEND = RAIZ / "backend"

# Tempo máximo por verificação. O hook roda a cada edição: travar a sessão
# esperando uma ferramenta lenta seria pior do que não verificar.
LIMITE_SEGUNDOS = 60


def _habilitar_utf8() -> None:
    for fluxo in (sys.stdout, sys.stderr):
        reconfigure = getattr(fluxo, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):  # pragma: no cover
                pass


def _rodar(rotulo: str, comando: list[str], diretorio: Path) -> None:
    """Executa uma verificação e imprime o resultado em uma linha, ou o erro."""
    try:
        processo = subprocess.run(  # noqa: S603 — comando fixo, sem entrada do usuário
            comando,
            cwd=diretorio,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=LIMITE_SEGUNDOS,
        )
    except FileNotFoundError:
        print(f"  {rotulo}: ferramenta não encontrada — pulado")
        return
    except subprocess.TimeoutExpired:
        print(f"  {rotulo}: excedeu {LIMITE_SEGUNDOS}s — pulado")
        return

    if processo.returncode == 0:
        print(f"  {rotulo}: OK")
        return

    print(f"  {rotulo}: FALHOU")
    saida = (processo.stdout or "") + (processo.stderr or "")
    for linha in saida.strip().splitlines()[:20]:
        print(f"    {linha}")


def _verificar_pureza_do_motor_de_risco(arquivo: Path) -> None:
    """
    Regra 3 do AGENTS.md: o motor de risco não pode conhecer a IA.

    O gate completo cobre isso por teste (`AC-RISCO-17`), mas descobrir na hora
    da edição é muito mais barato do que descobrir na suíte.
    """
    proibidos = ("ai_explainer", "ai_service", "openai", "google.generativeai")
    try:
        conteudo = arquivo.read_text(encoding="utf-8")
    except OSError:  # pragma: no cover
        return

    encontrados = [
        termo
        for termo in proibidos
        if f"import {termo}" in conteudo or f"from app.services.{termo}" in conteudo
    ]

    if encontrados:
        print(f"  pureza do motor de risco: VIOLADA — importa {', '.join(encontrados)}")
        print("    AGENTS.md regra 3: a IA nunca decide risco. Reverta este import.")
    else:
        print("  pureza do motor de risco: OK")


def main() -> int:
    _habilitar_utf8()

    try:
        entrada = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    bruto = (entrada.get("tool_input") or {}).get("file_path")
    if not bruto:
        return 0

    arquivo = Path(str(bruto))
    if not arquivo.is_absolute():
        arquivo = (RAIZ / arquivo).resolve()

    try:
        relativo = arquivo.relative_to(RAIZ).as_posix()
    except ValueError:
        return 0  # arquivo fora do projeto

    if not arquivo.is_file():
        return 0

    verificacoes: list[str] = []

    # --- Backend Python ---
    if relativo.startswith("backend/") and arquivo.suffix == ".py":
        verificacoes.append("python")
        print(f"[hook] {relativo}")
        _rodar("sintaxe (py_compile)", [sys.executable, "-m", "py_compile", str(arquivo)], BACKEND)
        _rodar("lint (ruff)", [sys.executable, "-m", "ruff", "check", str(arquivo)], BACKEND)

        if arquivo.name == "risk_engine.py":
            _verificar_pureza_do_motor_de_risco(arquivo)

    # --- SDD ---
    if relativo.startswith("SDD/") and arquivo.suffix == ".md":
        verificacoes.append("sdd")
        print(f"[hook] {relativo}")
        _rodar(
            "rastreabilidade",
            [sys.executable, "scripts/rastreabilidade.py", "--silencioso"],
            RAIZ,
        )

    # --- Testes: a citação do AC é obrigatória ---
    if relativo.startswith("backend/tests/") and arquivo.name.startswith("test_"):
        verificacoes.append("teste")
        conteudo = arquivo.read_text(encoding="utf-8", errors="replace")
        if "AC-" not in conteudo:
            print(f"[hook] {relativo}")
            print("  citação de AC: AUSENTE")
            print("    backend/tests/CLAUDE.md: todo teste cita o AC que prova.")

    if not verificacoes:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
