# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SbomComponentParsed:
    nome: str
    versao: str | None = None
    ecossistema: str | None = None
    tipo_componente: str | None = None
    purl: str | None = None
    cpe: str | None = None
    fornecedor: str | None = None
    licenca: str | None = None
    hashes: str | None = None


@dataclass
class SbomParseResult:
    formato: str
    versao_formato: str | None = None
    serial_number: str | None = None
    generated_at: datetime | None = None
    componentes: list[SbomComponentParsed] = field(default_factory=list)


def _parse_cyclonedx(dados: dict[str, Any]) -> SbomParseResult:
    resultado = SbomParseResult(
        formato="cyclonedx",
        versao_formato=dados.get("specVersion"),
        serial_number=dados.get("serialNumber"),
    )
    metadata = dados.get("metadata", {})
    timestamp_str = metadata.get("timestamp")
    if timestamp_str:
        try:
            # Handle some basic ISO formats, mostly CycloneDX uses Z
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            resultado.generated_at = datetime.fromisoformat(timestamp_str)
        except Exception:
            pass

    for comp in dados.get("components", []):
        nome = comp.get("name")
        if not nome:
            continue

        licencas = comp.get("licenses", [])
        licenca_str = None
        if licencas and isinstance(licencas, list):
            # Tenta pegar a primeira licenca, por id ou name
            prim = licencas[0].get("license", {})
            licenca_str = prim.get("id") or prim.get("name")

        purl = comp.get("purl")
        ecossistema = None
        if purl and purl.startswith("pkg:"):
            partes = purl.split("/")
            if len(partes) > 1:
                ecos = partes[0].split(":")[1]
                ecossistema = ecos

        resultado.componentes.append(
            SbomComponentParsed(
                nome=nome,
                versao=comp.get("version"),
                ecossistema=ecossistema,
                tipo_componente=comp.get("type"),
                purl=purl,
                cpe=comp.get("cpe"),
                fornecedor=comp.get("supplier", {}).get("name"),
                licenca=licenca_str,
            )
        )

    return resultado


def _parse_spdx(dados: dict[str, Any]) -> SbomParseResult:
    resultado = SbomParseResult(
        formato="spdx",
        versao_formato=dados.get("spdxVersion"),
        serial_number=dados.get("documentNamespace"),
    )
    creation_info = dados.get("creationInfo", {})
    timestamp_str = creation_info.get("created")
    if timestamp_str:
        try:
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            resultado.generated_at = datetime.fromisoformat(timestamp_str)
        except Exception:
            pass

    for pkg in dados.get("packages", []):
        nome = pkg.get("name")
        if not nome:
            continue

        purl = None
        for ref in pkg.get("externalRefs", []):
            if ref.get("referenceType") == "purl":
                purl = ref.get("referenceLocator")
                break

        ecossistema = None
        if purl and purl.startswith("pkg:"):
            partes = purl.split("/")
            if len(partes) > 1:
                ecos = partes[0].split(":")[1]
                ecossistema = ecos

        resultado.componentes.append(
            SbomComponentParsed(
                nome=nome,
                versao=pkg.get("versionInfo"),
                ecossistema=ecossistema,
                purl=purl,
                fornecedor=pkg.get("supplier"),
                licenca=pkg.get("licenseConcluded") or pkg.get("licenseDeclared"),
            )
        )

    return resultado


def ler_sbom(conteudo: str) -> SbomParseResult:
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError("O arquivo não é um JSON válido.") from exc

    if not isinstance(dados, dict):
        raise ValueError("O formato SBOM deve ser um objeto JSON.")

    if "bomFormat" in dados and dados["bomFormat"] == "CycloneDX":
        return _parse_cyclonedx(dados)
    elif "spdxVersion" in dados:
        return _parse_spdx(dados)
    else:
        raise ValueError("Formato não suportado. Envie um JSON de CycloneDX ou SPDX.")
