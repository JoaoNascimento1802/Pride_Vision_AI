# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
normalizer.py — Leitura e normalização dos relatórios do Semgrep e do Nuclei.

Migrado da POC. A diferença é que aqui os parsers recebem o conteúdo em memória
(o que chega no upload) em vez de um caminho de arquivo, e devolvem os avisos
em vez de imprimi-los.

Todas as funções são puras: nada de banco, nada de rede.
"""

from __future__ import annotations

import hashlib
import json
from urllib.parse import urlparse

from app.models.enums import Ferramenta
from app.services.dominio import AchadoNormalizado, ResultadoParse

# ---------------------------------------------------------------------------
# Tabela de normalização de tipos
# Chave: termo em minúsculas (casado por substring) → tipo canônico
# ---------------------------------------------------------------------------
MAPA_TIPOS: dict[str, str] = {
    # Família XSS
    "cross-site scripting": "xss",
    "reflected-xss": "xss",
    "stored-xss": "xss",
    "dom-xss": "xss",
    "xss": "xss",
    # Família SQL Injection
    "sql injection": "sqli",
    "sqli": "sqli",
    "sql-injection": "sqli",
    "blind-sqli": "sqli",
    # Família SSRF
    "server-side request forgery": "ssrf",
    "ssrf": "ssrf",
    "blind-ssrf": "ssrf",
    # Família RCE / Command Injection
    "remote code execution": "rce",
    "rce": "rce",
    "command injection": "rce",
    # Família Path Traversal
    "path traversal": "path_traversal",
    "directory traversal": "path_traversal",
    "lfi": "path_traversal",
}

# Extensões de código removidas do último segmento antes de comparar endpoints
_EXTENSOES_CODIGO = (
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".php",
    ".rb",
    ".java",
    ".go",
)

# Um último segmento menor que isto não estabelece compatibilidade, para que
# nomes genéricos curtos não juntem endpoints sem relação.
_MIN_SEGMENTO = 3


def afrouxar_separadores(texto: str) -> str:
    """
    Troca separadores de palavra por espaços simples.

    O Nuclei chama um template de "Remote Code Execution" enquanto o Semgrep
    escreve a mesma coisa como "...audit.command-injection". Comparar as duas
    formas afrouxadas faz a tabela casar independentemente do separador.
    """
    for separador in ("-", "_", "."):
        texto = texto.replace(separador, " ")
    return " ".join(texto.split())


def normalizar_tipo(bruto: str) -> str:
    """
    Converte o nome de uma vulnerabilidade para o tipo canônico.

    Casa os termos da tabela sem diferenciar maiúsculas, tanto no texto original
    quanto na forma sem separadores. Tipos desconhecidos são preservados em
    minúsculas — continuam sendo correlacionados e classificados, apenas não são
    unificados com sinônimos.
    """
    minusculo = bruto.lower()
    afrouxado = afrouxar_separadores(minusculo)
    for termo, canonico in MAPA_TIPOS.items():
        if termo in minusculo or afrouxar_separadores(termo) in afrouxado:
            return canonico
    return minusculo


def normalizar_endpoint(url: str) -> str:
    """
    Extrai o caminho de uma URL, descartando esquema, domínio, porta e query.

    Exemplos:
        https://exemplo.com/busca?q=teste  →  /busca
        https://exemplo.com/               →  /
    """
    try:
        caminho = urlparse(url).path
        return caminho if caminho else "/"
    except ValueError:
        return "/"


def canonizar_endpoint(endpoint: str) -> str:
    """
    Reduz um endpoint à forma canônica de comparação.

    Minúsculas, contrabarras viram barras, query e fragmento saem, barras
    repetidas colapsam, barra final some (exceto na raiz) e a extensão de código
    é removida do último segmento.
    """
    texto = endpoint.strip().lower().replace("\\", "/")

    for separador in ("?", "#"):
        if separador in texto:
            texto = texto.split(separador, 1)[0]

    while "//" in texto:
        texto = texto.replace("//", "/")

    if len(texto) > 1:
        texto = texto.rstrip("/")

    for extensao in _EXTENSOES_CODIGO:
        if texto.endswith(extensao):
            texto = texto[: -len(extensao)]
            break

    return texto


def _segmentos(canonico: str) -> list[str]:
    return [s for s in canonico.split("/") if s]


def endpoints_compativeis(a: str, b: str) -> bool:
    """
    Decide se dois endpoints apontam para o mesmo lugar.

    A especificação pede correlação quando o endpoint for "igual ou compatível".
    O Semgrep reporta caminho de arquivo e o Nuclei reporta caminho de URL, então
    igualdade pura nunca casaria os dois. São compatíveis quando:

    1. As formas canônicas são idênticas.
       "/busca" ~ "/busca/" ~ "/busca?q=1"
    2. Um é prefixo do outro em fronteira de segmento.
       "/busca" ~ "/busca/avancada"
    3. Compartilham o último segmento, com ao menos 3 caracteres.
       "src/views/busca.py" ~ "/busca"

    Reflexiva e simétrica, o que garante agrupamento estável.
    """
    canon_a = canonizar_endpoint(a)
    canon_b = canonizar_endpoint(b)

    if canon_a == canon_b:
        return True

    seg_a = _segmentos(canon_a)
    seg_b = _segmentos(canon_b)

    if not seg_a or not seg_b:
        return False

    menor, maior = sorted((seg_a, seg_b), key=len)
    if maior[: len(menor)] == menor:
        return True

    return seg_a[-1] == seg_b[-1] and len(seg_a[-1]) >= _MIN_SEGMENTO


def _extrair_status_http(entrada: dict[str, object]) -> int | None:
    """
    Extrai o código de status HTTP de uma entrada do Nuclei.

    O Nuclei grava a resposta HTTP inteira em "response", então o código precisa
    ser lido da linha de status ("HTTP/1.1 200 OK"). Algumas versões e relatórios
    feitos à mão trazem "status-code" ou um número puro; todos são tratados.
    """
    status_bruto = entrada.get("status-code")
    if status_bruto is not None:
        try:
            return int(str(status_bruto).strip())
        except ValueError:
            pass

    resposta = entrada.get("response")
    if not resposta:
        return None

    linhas = str(resposta).splitlines()
    if not linhas:
        return None

    partes = linhas[0].split()
    if not partes:
        return None

    # "HTTP/1.1 200 OK" → segundo token; um "200" puro → primeiro token
    candidato = (
        partes[1] if partes[0].upper().startswith("HTTP/") and len(partes) > 1 else partes[0]
    )

    try:
        return int(candidato)
    except ValueError:
        return None


def ler_semgrep(conteudo: str) -> ResultadoParse:
    """
    Lê um relatório JSON do Semgrep.

    Resultados sem campo obrigatório são descartados com aviso, e o
    processamento continua: relatórios reais vêm com lixo, e perder o arquivo
    inteiro por causa de uma entrada ruim seria pior.

    Raises:
        ValueError: se o conteúdo não for JSON válido.
    """
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError(f"O arquivo do Semgrep não é um JSON válido: {exc}") from exc

    if not isinstance(dados, dict):
        raise ValueError("O relatório do Semgrep deve ser um objeto JSON.")

    resultado = ResultadoParse()

    for indice, item in enumerate(dados.get("results", [])):
        try:
            regra_id = item["check_id"]
            arquivo = item["path"]
            linha_bruta = item.get("start", {}).get("line")
            if linha_bruta is None:
                raise KeyError("start.line")
            linha = int(linha_bruta)
            extra = item.get("extra", {})
            mensagem = extra["message"]
            severidade = extra["severity"]
        except (KeyError, TypeError, ValueError) as exc:
            faltando = str(exc).strip("'")
            resultado.ignorados += 1
            resultado.avisos.append(
                f"Resultado #{indice} do Semgrep ignorado — campo ausente ou inválido: {faltando}"
            )
            continue

        metadata = item.get("extra", {}).get("metadata", {})

        cwe: str | None = None
        lista_cwe = metadata.get("cwe") or []
        if isinstance(lista_cwe, list) and lista_cwe:
            cwe = str(lista_cwe[0])

        # metadata.route, quando presente, é a rota que aquele código atende e
        # dá a correlação exata. Sem ela, o caminho do arquivo ainda casa pelas
        # regras de compatibilidade.
        rota = metadata.get("route")
        endpoint = str(rota) if rota else normalizar_endpoint(arquivo)

        resultado.achados.append(
            AchadoNormalizado(
                origem=Ferramenta.SEMGREP,
                tipo_vuln=normalizar_tipo(regra_id),
                endpoint=endpoint,
                severidade=str(severidade),
                mensagem=str(mensagem),
                regra_id=str(regra_id),
                arquivo=str(arquivo),
                linha=linha,
                cwe=cwe,
            )
        )

    return resultado


def ler_nuclei(conteudo: str) -> ResultadoParse:
    """
    Lê um relatório JSONL do Nuclei — um objeto JSON por linha.

    Linhas inválidas são descartadas com aviso; linhas em branco são ignoradas
    silenciosamente.
    """
    resultado = ResultadoParse()

    for numero, linha_bruta in enumerate(conteudo.splitlines(), start=1):
        linha = linha_bruta.strip()
        if not linha:
            continue

        try:
            entrada = json.loads(linha)
        except json.JSONDecodeError:
            resultado.ignorados += 1
            resultado.avisos.append(f"Linha {numero} do Nuclei ignorada — JSON inválido")
            continue

        if not isinstance(entrada, dict):
            resultado.ignorados += 1
            resultado.avisos.append(f"Linha {numero} do Nuclei ignorada — não é um objeto")
            continue

        template_id = str(entrada.get("template-id", "desconhecido"))
        info = entrada.get("info", {})
        if not isinstance(info, dict):
            info = {}

        tipo_bruto = info.get("name") or entrada.get("type") or template_id
        url = str(entrada.get("matched-at", ""))

        evidencia: str | None = None
        extraidos = entrada.get("extracted-results")
        if isinstance(extraidos, list) and extraidos:
            evidencia = str(extraidos[0])

        resultado.achados.append(
            AchadoNormalizado(
                origem=Ferramenta.NUCLEI,
                tipo_vuln=normalizar_tipo(str(tipo_bruto)),
                endpoint=normalizar_endpoint(url) if url else "/",
                severidade=str(info.get("severity", "desconhecida")),
                mensagem=str(info.get("name", template_id)),
                regra_id=template_id,
                url=url or None,
                http_status=_extrair_status_http(entrada),
                evidencia=evidencia,
            )
        )

    return resultado


def ler_trivy(conteudo: str) -> ResultadoParse:
    """
    Lê um relatório JSON do Trivy (suporta SCA e Container Scanning).

    Raises:
        ValueError: se o conteúdo não for JSON válido.
    """
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError(f"O arquivo do Trivy não é um JSON válido: {exc}") from exc

    if not isinstance(dados, dict):
        raise ValueError("O relatório do Trivy deve ser um objeto JSON.")

    resultado = ResultadoParse()

    artifact_type = dados.get("ArtifactType")
    is_container = artifact_type == "container_image"

    image_name = dados.get("ArtifactName")
    image_digest = None
    image_tag = None
    image_repository = image_name
    os_name = None
    architecture = None

    if is_container:
        metadata = dados.get("Metadata", {})
        repo_tags = metadata.get("RepoTags", [])
        if repo_tags:
            full_tag = repo_tags[0]
            if ":" in full_tag.split("/")[-1]:
                image_tag = full_tag.split("/")[-1].split(":")[-1]
                image_repository = full_tag.rsplit(":", 1)[0]
            else:
                image_repository = full_tag

        repo_digests = metadata.get("RepoDigests", [])
        if repo_digests:
            digest_str = repo_digests[0]
            image_digest = digest_str.split("@")[-1] if "@" in digest_str else digest_str

        os_info = metadata.get("OS", {})
        if os_info:
            os_name = f"{os_info.get('Family', '')} {os_info.get('Name', '')}".strip()

        img_config = metadata.get("ImageConfig", {})
        architecture = img_config.get("architecture")

    tipo_padrao = "container_vulnerability" if is_container else "sca"

    for indice_resultado, item in enumerate(dados.get("Results", [])):
        alvo = item.get("Target", "desconhecido")
        for indice_vuln, vuln in enumerate(item.get("Vulnerabilities", [])):
            try:
                regra_id = vuln["VulnerabilityID"]
                pacote = vuln.get("PkgName", "desconhecido")
                titulo = vuln.get("Title") or vuln.get("Description") or regra_id
                severidade = vuln.get("Severity", "UNKNOWN")
                installed_version = vuln.get("InstalledVersion")
                fixed_version = vuln.get("FixedVersion")
                layer_info = vuln.get("Layer", {})
                layer_digest = layer_info.get("Digest") if isinstance(layer_info, dict) else None
            except (KeyError, TypeError) as exc:
                resultado.ignorados += 1
                resultado.avisos.append(
                    f"Vulnerabilidade #{indice_vuln} do Target {alvo} ignorada — campo ausente: {exc}"
                )
                continue

            # Se for container, o endpoint pode ser a imagem. Se for SCA, é o arquivo.
            base_endpoint = image_digest or image_repository or alvo
            endpoint_str = f"{base_endpoint} ({pacote})" if is_container else f"{alvo} ({pacote})"

            resultado.achados.append(
                AchadoNormalizado(
                    origem=Ferramenta.TRIVY,
                    tipo_vuln=normalizar_tipo(tipo_padrao),
                    endpoint=endpoint_str,
                    severidade=str(severidade),
                    mensagem=str(titulo),
                    regra_id=str(regra_id),
                    arquivo=str(alvo) if not is_container else None,
                    image_name=image_name if is_container else None,
                    image_repository=image_repository if is_container else None,
                    image_tag=image_tag if is_container else None,
                    image_digest=image_digest if is_container else None,
                    os=os_name if is_container else None,
                    architecture=architecture if is_container else None,
                    layer=layer_digest if is_container else None,
                    pacote=pacote if is_container else None,
                    versao=installed_version if is_container else None,
                    versao_corrigida=fixed_version if is_container else None,
                )
            )

    return resultado


def _mascarar_segredo(segredo: str) -> str:
    """Mascara um segredo mantendo apenas os 4 primeiros caracteres visíveis, se possível."""
    if len(segredo) <= 4:
        return "[REDACTED_SECRET]"
    return f"{segredo[:4]}" + "*" * 10


def _gerar_fingerprint_segredo(regra: str, arquivo: str, linha: int, segredo_cru: str) -> str:
    """Gera um hash seguro para deduplicação sem salvar o segredo em texto puro."""
    base = f"{regra}:{arquivo}:{linha}:{segredo_cru}".encode()
    return hashlib.sha256(base).hexdigest()


def ler_gitleaks(conteudo: str) -> ResultadoParse:
    """
    Lê um relatório JSON do Gitleaks.

    Raises:
        ValueError: se o conteúdo não for JSON válido.
    """
    import json

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError(f"O arquivo do Gitleaks não é um JSON válido: {exc}") from exc

    if not isinstance(dados, list):
        raise ValueError("O relatório do Gitleaks deve ser uma lista JSON.")

    resultado = ResultadoParse()

    for indice, item in enumerate(dados):
        if not isinstance(item, dict):
            resultado.ignorados += 1
            resultado.avisos.append(f"Item #{indice} ignorado — não é um objeto")
            continue

        try:
            regra_id = item["RuleID"]
            secret = item.get("Secret", "")
            match = item.get("Match", "")
            secret_value = secret or match

            arquivo = item.get("File", "desconhecido")
            linha = item.get("StartLine", 0)

            repositorio = item.get("Repo", "desconhecido")
            commit = item.get("Commit", "")
            descricao = item.get("Description", regra_id)
        except (KeyError, TypeError) as exc:
            resultado.ignorados += 1
            resultado.avisos.append(f"Vulnerabilidade #{indice} ignorada — campo ausente: {exc}")
            continue

        fingerprint = _gerar_fingerprint_segredo(regra_id, arquivo, linha, secret_value)
        segredo_mascarado = _mascarar_segredo(secret_value)

        # Evidência segura
        evidencia_segura = f"Segredo detectado (mascarado): {segredo_mascarado}\nCommit: {commit}"

        resultado.achados.append(
            AchadoNormalizado(
                origem=Ferramenta.GITLEAKS,
                tipo_vuln="secrets",
                endpoint=f"{arquivo}:{linha}",
                severidade="critical",  # Por padrão, secrets expostos são críticos
                mensagem=str(descricao),
                regra_id=str(regra_id),
                arquivo=str(arquivo),
                linha=int(linha) if str(linha).isdigit() else None,
                repository=str(repositorio),
                commit=str(commit),
                fingerprint=fingerprint,
                evidencia=evidencia_segura,
            )
        )

    return resultado


def ler_checkov(conteudo: str) -> ResultadoParse:
    """
    Normaliza a saída JSON do Checkov.
    Trata múltiplos recursos e lida com falhas no arquivo.
    """
    resultado = ResultadoParse()

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as exc:
        raise ValueError(f"O relatório do Checkov não é um JSON válido: {exc}") from exc

    # O Checkov pode retornar uma lista (vários frameworks/arquivos) ou um objeto
    resultados_lista = dados if isinstance(dados, list) else [dados]

    for relatorio in resultados_lista:
        results = relatorio.get("results", {})
        if not results:
            continue

        failed_checks = results.get("failed_checks", [])

        for achado in failed_checks:
            try:
                check_id = achado.get("check_id")
                mensagem = achado.get("check_name")

                if not check_id or not mensagem:
                    resultado.ignorados += 1
                    resultado.avisos.append(
                        "Checkov finding ignorado: ausência de check_id ou check_name."
                    )
                    continue

                severidade = achado.get("severity") or "MEDIUM"

                arquivo = achado.get("file_path", "desconhecido")
                if arquivo and arquivo.startswith("/"):
                    arquivo = arquivo[1:]

                linha = None
                line_range = achado.get("file_line_range")
                if line_range and isinstance(line_range, list) and len(line_range) > 0:
                    linha = line_range[0]

                resource = achado.get("resource")
                resource_type = resource.split(".")[0] if resource and "." in resource else None

                tipo_vuln = normalizar_tipo(check_id)
                if not tipo_vuln or tipo_vuln == check_id.lower():
                    tipo_vuln = "iac_misconfiguration"

                resultado.achados.append(
                    AchadoNormalizado(
                        origem=Ferramenta.CHECKOV,
                        tipo_vuln=tipo_vuln,
                        endpoint=resource or arquivo,
                        severidade=str(severidade).lower(),
                        mensagem=str(mensagem),
                        regra_id=str(check_id),
                        arquivo=str(arquivo),
                        linha=int(linha) if linha is not None and str(linha).isdigit() else None,
                        resource=str(resource) if resource else None,
                        resource_type=str(resource_type) if resource_type else None,
                        guideline=str(achado.get("guideline", "")),
                        framework=str(relatorio.get("check_type", "")),
                    )
                )
            except Exception as e:
                resultado.ignorados += 1
                resultado.avisos.append(f"Checkov finding malformado: {str(e)}")

    if not resultado.achados and resultado.ignorados == 0:
        resultado.avisos.append("Nenhum problema encontrado no relatório do Checkov.")

    return resultado


def ler_api_security(conteudo: str) -> ResultadoParse:
    try:
        dados = json.loads(conteudo)
    except Exception:
        return ResultadoParse()

    resultado = ResultadoParse()
    for item in dados:
        try:
            achado = AchadoNormalizado(
                origem=Ferramenta.API_SECURITY,
                tipo_vuln=item.get("titulo", "API Security Finding"),
                endpoint=item.get("endpoint", ""),
                severidade=item.get("severidade", "medium"),
                mensagem=item.get("descricao", ""),
                regra_id=item.get("titulo", "API Security Finding"),
                evidencia=item.get("log", "")
            )
            resultado.achados.append(achado)
        except Exception:
            continue

    return resultado

def ler_supply_chain(conteudo: str) -> ResultadoParse:
    import json
    achados: list[AchadoNormalizado] = []
    erros: list[str] = []
    try:
        dados = json.loads(conteudo)
        if not isinstance(dados, list):
            erros.append('O JSON de supply_chain deve ser uma lista de objetos.')
            return ResultadoParse(achados=achados, ignorados=len(erros), avisos=erros)

        for idx, item in enumerate(dados):
            try:
                achado = AchadoNormalizado(
                    origem=Ferramenta.SUPPLY_CHAIN,
                    tipo_vuln=normalizar_tipo(item['titulo']),
                    endpoint='',
                    severidade=item.get('severidade', 'CRITICO'),
                    mensagem=item.get('descricao', ''),
                    regra_id=item['titulo'],
                    arquivo=item.get('arquivo'),
                    linha=None,
                    cwe=None,
                )
                achados.append(achado)
            except KeyError as e:
                erros.append(f'Falta o campo obrigatório {e} no item {idx}')
    except json.JSONDecodeError:
        erros.append('Falha ao fazer parse do JSON de supply_chain.')

    return ResultadoParse(achados=achados, ignorados=len(erros), avisos=erros)

