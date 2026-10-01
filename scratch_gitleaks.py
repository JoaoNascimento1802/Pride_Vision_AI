import json
import hashlib
from pathlib import Path

content = Path('backend/app/services/normalizer.py').read_text(encoding='utf-8')

new_func = '''
def _mascarar_segredo(segredo: str) -> str:
    """Mascara um segredo mantendo apenas os 4 primeiros caracteres visíveis, se possível."""
    if len(segredo) <= 4:
        return "[REDACTED_SECRET]"
    return f"{segredo[:4]}" + "*" * 10

def _gerar_fingerprint_segredo(regra: str, arquivo: str, linha: int, segredo_cru: str) -> str:
    """Gera um hash seguro para deduplicação sem salvar o segredo em texto puro."""
    base = f"{regra}:{arquivo}:{linha}:{segredo_cru}".encode("utf-8")
    return hashlib.sha256(base).hexdigest()

def ler_gitleaks(conteudo: str) -> ResultadoParse:
    """
    Lê um relatório JSON do Gitleaks.
    
    Raises:
        ValueError: se o conteúdo não for JSON válido.
    """
    import json
    import hashlib
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
            resultado.avisos.append(
                f"Vulnerabilidade #{indice} ignorada — campo ausente: {exc}"
            )
            continue
            
        fingerprint = _gerar_fingerprint_segredo(regra_id, arquivo, linha, secret_value)
        segredo_mascarado = _mascarar_segredo(secret_value)
        
        # Evidência segura
        evidencia_segura = f"Segredo detectado (mascarado): {segredo_mascarado}\\nCommit: {commit}"

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
                evidencia=evidencia_segura
            )
        )

    return resultado
'''

if 'ler_gitleaks' not in content:
    Path('backend/app/services/normalizer.py').write_text(content + '\n' + new_func, encoding='utf-8')

