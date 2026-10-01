import json
from pathlib import Path

content = Path('backend/app/services/normalizer.py').read_text(encoding='utf-8')

new_func = '''

def ler_trivy(conteudo: str) -> ResultadoParse:
    """
    Lê um relatório JSON do Trivy.

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

    for indice_resultado, item in enumerate(dados.get("Results", [])):
        alvo = item.get("Target", "desconhecido")
        for indice_vuln, vuln in enumerate(item.get("Vulnerabilities", [])):
            try:
                regra_id = vuln["VulnerabilityID"]
                pacote = vuln.get("PkgName", "desconhecido")
                titulo = vuln.get("Title") or vuln.get("Description") or regra_id
                severidade = vuln.get("Severity", "UNKNOWN")
            except (KeyError, TypeError) as exc:
                resultado.ignorados += 1
                resultado.avisos.append(
                    f"Vulnerabilidade #{indice_vuln} do Target {alvo} ignorada — campo ausente: {exc}"
                )
                continue

            resultado.achados.append(
                AchadoNormalizado(
                    origem=Ferramenta.TRIVY,
                    tipo_vuln=normalizar_tipo("sca"),
                    endpoint=f"{alvo} ({pacote})",
                    severidade=str(severidade),
                    mensagem=str(titulo),
                    regra_id=str(regra_id),
                    arquivo=str(alvo),
                )
            )

    return resultado
'''

if 'ler_trivy' not in content:
    Path('backend/app/services/normalizer.py').write_text(content + new_func, encoding='utf-8')

