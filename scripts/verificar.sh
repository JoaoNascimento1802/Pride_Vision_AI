#!/usr/bin/env bash
#
# verificar.sh — O gate único do PRIDE Vision AI (equivalente POSIX do verificar.ps1).
#
# Roda tudo que precisa estar verde para uma tarefa ser considerada concluída.
# NÃO aborta no primeiro erro de propósito: um ruff vermelho não pode esconder o
# resultado da suíte.
#
# Uso:
#   ./scripts/verificar.sh
#   ./scripts/verificar.sh --rapido    # pula o build do frontend

set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$RAIZ/backend"
FRONTEND="$RAIZ/frontend"

RAPIDO=0
if [ "${1:-}" = "--rapido" ]; then
    RAPIDO=1
fi

NOMES=()
CODIGOS=()

etapa() {
    local nome="$1"
    local diretorio="$2"
    shift 2

    echo ""
    echo "=== $nome ==="

    (cd "$diretorio" && "$@")
    local codigo=$?

    if [ $codigo -eq 0 ]; then
        echo "OK — $nome"
    else
        echo "FALHOU — $nome (código $codigo)"
    fi

    NOMES+=("$nome")
    CODIGOS+=("$codigo")
}

# --- Backend ---------------------------------------------------------------

etapa "Suíte do backend (pytest)"        "$BACKEND" python -m pytest -q
etapa "Lint do backend (ruff)"           "$BACKEND" python -m ruff check app/ tests/
etapa "Tipos do backend (mypy --strict)" "$BACKEND" python -m mypy --strict app/

# --- Frontend --------------------------------------------------------------

if [ ! -d "$FRONTEND/node_modules" ]; then
    echo ""
    echo "=== Frontend ==="
    echo "FALHOU — node_modules ausente. Rode: npm install --prefix frontend"
    NOMES+=("Dependências do frontend")
    CODIGOS+=(1)
else
    etapa "Testes do frontend (vitest)" "$FRONTEND" npm run test --silent
    if [ $RAPIDO -eq 1 ]; then
        echo ""
        echo "PULADO — Build do frontend (--rapido)"
    else
        etapa "Build do frontend (tsc + vite)" "$FRONTEND" npm run build --silent
    fi
fi

# --- O gate que define o projeto -------------------------------------------

etapa "Rastreabilidade AC <-> teste" "$RAIZ" python scripts/rastreabilidade.py --emitir

# --- Resumo ----------------------------------------------------------------

echo ""
echo "================ RESUMO ================"
falhas=0
for i in "${!NOMES[@]}"; do
    if [ "${CODIGOS[$i]}" -eq 0 ]; then
        echo "  [ OK ]  ${NOMES[$i]}"
    else
        echo "  [FALHA] ${NOMES[$i]}"
        falhas=$((falhas + 1))
    fi
done

echo ""
if [ $falhas -eq 0 ]; then
    echo "GATE VERDE — a tarefa pode ser considerada concluída."
    exit 0
fi

echo "GATE VERMELHO — $falhas etapa(s) falharam. A tarefa NÃO está concluída."
exit 1
