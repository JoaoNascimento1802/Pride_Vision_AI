# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
rastreabilidade.py — O gate que torna o projeto spec-driven.

Liga cada critério de aceitação da `SDD/` ao teste que o prova. Sem esse vínculo
verificado por máquina, "o sistema está de acordo com a especificação" é opinião.

Falha (código 1) quando:

- um AC declarado na SDD não é citado por nenhum teste          (AC órfão)
- um teste cita um AC que não existe na SDD                     (AC fantasma)
- o mesmo AC é declarado em dois lugares                        (AC duplicado)
- um AC é declarado sem texto ou fora do formato Dado/Então     (AC não testável)
- um documento da SDD referencia um AC inexistente              (referência quebrada)

Uso:

    python scripts/rastreabilidade.py            # verifica e relata
    python scripts/rastreabilidade.py --emitir   # verifica e regrava RASTREABILIDADE.md
    python scripts/rastreabilidade.py --silencioso

Só biblioteca padrão: o gate não pode depender de o ambiente estar instalado.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_SDD = RAIZ / "SDD"
SAIDA = DIR_SDD / "RASTREABILIDADE.md"

# Onde procurar testes. Só arquivos que o pytest e o vitest realmente executam:
# uma citação na docstring de um módulo auxiliar (`analise_estatica.py`) não
# prova nada e não pode contar como cobertura.
PADROES_DE_TESTE: tuple[tuple[Path, str], ...] = (
    (RAIZ / "backend" / "tests", "**/test_*.py"),
    (RAIZ / "frontend" / "src", "**/*.test.ts"),
    (RAIZ / "frontend" / "src", "**/*.test.tsx"),
)

# Documentos da SDD que só referenciam ACs, nunca os declaram.
SEM_DECLARACAO = frozenset({"00-INDICE.md", "10-mvp.md", "RASTREABILIDADE.md"})

# `- **AC-RISCO-01** — texto` ou `- **AC-INV-E1** — texto`
RE_DECLARACAO = re.compile(r"^\s*-\s+\*\*(AC-[A-Z]+-E?\d+)\*\*\s*(?:—|-|–)?\s*(.*)$")

# Qualquer menção, em qualquer lugar
RE_MENCAO = re.compile(r"\bAC-[A-Z]+-E?\d+\b")

# O formato exigido: Dado … quando … então. "quando" é opcional porque alguns
# critérios de proibição ficam mais claros sem ele.
RE_DADO = re.compile(r"\bdado\b", re.IGNORECASE)
RE_ENTAO = re.compile(r"\bent[aã]o\b", re.IGNORECASE)


@dataclass
class CriterioAceitacao:
    """Um AC declarado na SDD."""

    id: str
    documento: str
    linha: int
    texto: str
    extensao: bool = False
    proibicao: bool = False
    testes: list[str] = field(default_factory=list)

    @property
    def marca(self) -> str:
        if self.proibicao:
            return "proibição"
        if self.extensao:
            return "extensão"
        return "PDF"

    @property
    def resumo(self) -> str:
        """O texto do critério, sem marcação, curto o bastante para a tabela."""
        limpo = re.sub(r"`([^`]*)`", r"\1", self.texto)
        limpo = limpo.replace("**", "").replace("[extensão]", "").replace("[proibição]", "")
        limpo = " ".join(limpo.split())
        # Nos ACs marcados, o travessão vem depois da marca e sobra ao removê-la
        limpo = limpo.lstrip("—–- ")
        return limpo[:157] + "…" if len(limpo) > 158 else limpo


@dataclass
class Problema:
    tipo: str
    detalhe: str
    onde: str


def _habilitar_utf8() -> None:
    """O relatório tem acento; o console do Windows nasce em cp1252."""
    for fluxo in (sys.stdout, sys.stderr):
        reconfigure = getattr(fluxo, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):  # pragma: no cover — fluxos exóticos
                pass


def _relativo(caminho: Path) -> str:
    try:
        return caminho.relative_to(RAIZ).as_posix()
    except ValueError:  # pragma: no cover — fora da raiz do projeto
        return caminho.as_posix()


def coletar_criterios() -> tuple[dict[str, CriterioAceitacao], list[Problema]]:
    """
    Lê a SDD e devolve os ACs declarados, mais os problemas de declaração.

    Um AC é declarado por um item de lista que começa com o ID em negrito. Menção
    em tabela, em prosa ou em título é referência, não declaração — é isso que
    permite ao `10-mvp.md` citar dezenas de ACs sem redeclarar nenhum.
    """
    criterios: dict[str, CriterioAceitacao] = {}
    problemas: list[Problema] = []

    if not DIR_SDD.is_dir():
        problemas.append(
            Problema("sdd-ausente", f"Diretório não encontrado: {_relativo(DIR_SDD)}", "-")
        )
        return criterios, problemas

    for documento in sorted(DIR_SDD.glob("*.md")):
        if documento.name in SEM_DECLARACAO:
            continue

        linhas = documento.read_text(encoding="utf-8").splitlines()
        atual: CriterioAceitacao | None = None

        for numero, linha in enumerate(linhas, start=1):
            casamento = RE_DECLARACAO.match(linha)

            if casamento is not None:
                identificador, resto = casamento.group(1), casamento.group(2)
                atual = CriterioAceitacao(
                    id=identificador,
                    documento=documento.name,
                    linha=numero,
                    texto=resto.strip(),
                    extensao="[extensão]" in resto,
                    proibicao="[proibição]" in resto,
                )

                anterior = criterios.get(identificador)
                if anterior is not None:
                    problemas.append(
                        Problema(
                            "AC duplicado",
                            f"{identificador} declarado em "
                            f"{anterior.documento}:{anterior.linha} e "
                            f"{documento.name}:{numero}",
                            f"SDD/{documento.name}:{numero}",
                        )
                    )
                else:
                    criterios[identificador] = atual
                continue

            # Continuação do item: linha indentada logo abaixo, sem linha em branco
            if atual is not None:
                if linha.strip() and linha.startswith((" ", "\t")):
                    atual.texto = f"{atual.texto} {linha.strip()}"
                    continue
                atual = None

    for criterio in criterios.values():
        onde = f"SDD/{criterio.documento}:{criterio.linha}"
        if not criterio.texto:
            problemas.append(Problema("AC sem texto", criterio.id, onde))
        elif not (RE_DADO.search(criterio.texto) and RE_ENTAO.search(criterio.texto)):
            problemas.append(
                Problema(
                    "AC não testável",
                    f"{criterio.id} não segue o formato Dado/Quando/Então",
                    onde,
                )
            )

    return criterios, problemas


def coletar_referencias_da_sdd(conhecidos: set[str]) -> list[Problema]:
    """Referências a AC dentro da própria SDD que não apontam para nada."""
    problemas: list[Problema] = []

    for documento in sorted(DIR_SDD.glob("*.md")):
        if documento.name == "RASTREABILIDADE.md":
            continue
        for numero, linha in enumerate(
            documento.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for identificador in dict.fromkeys(RE_MENCAO.findall(linha)):
                if identificador not in conhecidos:
                    problemas.append(
                        Problema(
                            "referência quebrada",
                            f"{documento.name} cita {identificador}, que não é declarado",
                            f"SDD/{documento.name}:{numero}",
                        )
                    )
    return problemas


def coletar_citacoes_dos_testes() -> dict[str, list[str]]:
    """Mapeia cada AC citado nos testes para os locais que o citam."""
    citacoes: dict[str, list[str]] = {}

    for base, padrao in PADROES_DE_TESTE:
        if not base.is_dir():
            continue
        for arquivo in sorted(base.glob(padrao)):
            if "node_modules" in arquivo.parts or "__pycache__" in arquivo.parts:
                continue
            try:
                linhas = arquivo.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):  # pragma: no cover
                continue
            for numero, linha in enumerate(linhas, start=1):
                for identificador in dict.fromkeys(RE_MENCAO.findall(linha)):
                    citacoes.setdefault(identificador, []).append(
                        f"{_relativo(arquivo)}:{numero}"
                    )

    return citacoes


def montar_relatorio(criterios: dict[str, CriterioAceitacao]) -> str:
    """Gera o conteúdo de SDD/RASTREABILIDADE.md."""
    por_documento: dict[str, list[CriterioAceitacao]] = {}
    for criterio in criterios.values():
        por_documento.setdefault(criterio.documento, []).append(criterio)

    total = len(criterios)
    cobertos = sum(1 for c in criterios.values() if c.testes)
    do_pdf = sum(1 for c in criterios.values() if not c.extensao)
    proibicoes = sum(1 for c in criterios.values() if c.proibicao)

    partes = [
        "# Rastreabilidade — AC ↔ teste",
        "",
        "> **Arquivo gerado.** Não edite à mão: rode `python scripts/rastreabilidade.py --emitir`.",
        "> Cada critério da `SDD/` aparece aqui com os testes que o provam. AC sem teste",
        "> reprova o gate.",
        "",
        "## Resumo",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Critérios declarados | {total} |",
        f"| Com ao menos um teste | {cobertos} |",
        f"| Sem teste | {total - cobertos} |",
        f"| Vindos do PDF | {do_pdf} |",
        f"| Extensões (decisão de projeto) | {total - do_pdf} |",
        f"| Proibições (o que o sistema não pode fazer) | {proibicoes} |",
        "",
    ]

    for documento in sorted(por_documento):
        partes.append(f"## {documento}")
        partes.append("")
        partes.append("| AC | Origem | Critério | Testes |")
        partes.append("|---|---|---|---|")
        for criterio in sorted(
            por_documento[documento], key=lambda c: (len(c.id), c.id)
        ):
            testes = "<br>".join(f"`{t}`" for t in criterio.testes) or "**SEM TESTE**"
            resumo = criterio.resumo.replace("|", "\\|")
            partes.append(f"| `{criterio.id}` | {criterio.marca} | {resumo} | {testes} |")
        partes.append("")

    return "\n".join(partes) + "\n"


def main() -> int:
    _habilitar_utf8()

    analisador = argparse.ArgumentParser(
        description="Verifica a rastreabilidade entre os ACs da SDD e os testes."
    )
    analisador.add_argument(
        "--emitir", action="store_true", help="regrava SDD/RASTREABILIDADE.md"
    )
    analisador.add_argument(
        "--silencioso", action="store_true", help="só imprime se houver problema"
    )
    argumentos = analisador.parse_args()

    criterios, problemas = coletar_criterios()
    citacoes = coletar_citacoes_dos_testes()

    for identificador, locais in citacoes.items():
        criterio = criterios.get(identificador)
        if criterio is None:
            problemas.append(
                Problema(
                    "AC fantasma",
                    f"{identificador} é citado por teste mas não existe na SDD",
                    locais[0],
                )
            )
        else:
            criterio.testes = locais

    problemas.extend(coletar_referencias_da_sdd(set(criterios)))

    for criterio in sorted(criterios.values(), key=lambda c: (c.documento, c.linha)):
        if not criterio.testes:
            problemas.append(
                Problema(
                    "AC órfão",
                    f"{criterio.id} não é citado por nenhum teste",
                    f"SDD/{criterio.documento}:{criterio.linha}",
                )
            )

    if argumentos.emitir:
        SAIDA.write_text(montar_relatorio(criterios), encoding="utf-8")

    total = len(criterios)
    cobertos = sum(1 for c in criterios.values() if c.testes)

    if problemas:
        print("RASTREABILIDADE: REPROVADO")
        print(f"  {cobertos}/{total} critérios com teste")
        print("")
        por_tipo: dict[str, list[Problema]] = {}
        for problema in problemas:
            por_tipo.setdefault(problema.tipo, []).append(problema)
        for tipo in sorted(por_tipo):
            lista = por_tipo[tipo]
            print(f"  {tipo} ({len(lista)}):")
            for problema in lista:
                print(f"    - {problema.detalhe}")
                print(f"      {problema.onde}")
            print("")
        if argumentos.emitir:
            print(f"  Relatório regravado mesmo assim: {_relativo(SAIDA)}")
        return 1

    if not argumentos.silencioso:
        print("RASTREABILIDADE: APROVADO")
        print(f"  {cobertos}/{total} critérios da SDD com ao menos um teste")
        if argumentos.emitir:
            print(f"  Relatório: {_relativo(SAIDA)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
