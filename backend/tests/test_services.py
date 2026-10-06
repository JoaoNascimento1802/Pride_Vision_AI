# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes das funções puras: normalização, correlação e mascaramento.

Cobrem SDD/03-ingestao.md (parsers e normalização), SDD/04-correlacao.md e a
parte de mascaramento de SDD/06-ia.md. Incluem os casos de regressão dos três
bugs que só apareceram com o formato real das ferramentas.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import json

import pytest

from app.models.enums import Ferramenta
from app.services.correlator import correlacionar
from app.services.data_masker import mascarar
from app.services.dominio import AchadoNormalizado
from app.services.normalizer import (
    canonizar_endpoint,
    endpoints_compativeis,
    ler_nuclei,
    ler_semgrep,
    normalizar_endpoint,
    normalizar_tipo,
)


class TestNormalizarTipo:
    @pytest.mark.parametrize(
        ("bruto", "esperado"),
        [
            ("xss", "xss"),
            ("reflected-xss", "xss"),
            ("cross-site scripting", "xss"),
            ("Reflected-XSS", "xss"),
            ("python.flask.security.xss.reflected-xss", "xss"),
            ("sql injection", "sqli"),
            ("blind-sqli", "sqli"),
            ("server-side request forgery", "ssrf"),
            ("remote code execution", "rce"),
            ("lfi", "path_traversal"),
        ],
    )
    def test_sinonimos(self, bruto, esperado):
        """AC-ING-03 — sinônimos da mesma família chegam ao mesmo tipo canônico."""
        assert normalizar_tipo(bruto) == esperado

    def test_desconhecido_preservado_em_minusculas(self):
        """AC-ING-E7 — tipo fora das famílias conhecidas mantém o nome original."""
        assert normalizar_tipo("Open Redirect") == "open redirect"

    @pytest.mark.parametrize(
        ("regra_semgrep", "nome_nuclei"),
        [
            ("python.lang.security.audit.command-injection", "Remote Code Execution"),
            ("java.lang.security.audit.path-traversal-open", "Directory Traversal"),
            ("js.security.audit.command_injection", "Command Injection"),
            ("python.django.security.injection.sql-injection", "SQL Injection"),
        ],
    )
    def test_separadores_diferentes_chegam_ao_mesmo_tipo(self, regra_semgrep, nome_nuclei):
        """
        AC-ING-03 — separador diferente não separa a família.

        Regressão: a tabela tinha "command injection" com espaço e as regras do
        Semgrep usam hífen. Sem tratar isso, o mesmo achado nas duas ferramentas
        virava dois grupos médios em vez de um crítico.
        """
        assert normalizar_tipo(regra_semgrep) == normalizar_tipo(nome_nuclei)


class TestNormalizarEndpoint:
    @pytest.mark.parametrize(
        ("url", "esperado"),
        [
            ("https://exemplo.com/busca?q=teste", "/busca"),
            ("http://localhost:8080/admin", "/admin"),
            ("https://exemplo.com", "/"),
            ("https://exemplo.com/", "/"),
        ],
    )
    def test_extrai_o_caminho(self, url, esperado):
        """AC-ING-04 — esquema, domínio, porta e query são descartados."""
        assert normalizar_endpoint(url) == esperado

    def test_caminho_de_arquivo_passa_direto(self):
        """AC-ING-04 — caminho de arquivo não é uma URL e passa inalterado."""
        assert normalizar_endpoint("src/views/busca.py") == "src/views/busca.py"


class TestCompatibilidadeDeEndpoint:
    @pytest.mark.parametrize(
        ("a", "b"),
        [
            pytest.param("/busca", "/busca", id="AC-COR-03-identicos"),
            pytest.param("/busca/", "/busca?q=teste", id="AC-COR-03-barra-e-query"),
            pytest.param("busca", "/busca", id="AC-COR-03-sem-barra-inicial"),
            pytest.param("/busca", "/busca/avancada", id="AC-COR-04-prefixo"),
            pytest.param("src/views/busca.py", "/busca", id="AC-COR-05-arquivo-e-rota"),
            pytest.param("src\\views\\Busca.PY", "/busca", id="AC-COR-05-windows"),
        ],
    )
    def test_compativeis(self, a, b):
        """As três regras de compatibilidade da SDD/04-correlacao.md."""
        assert endpoints_compativeis(a, b)

    @pytest.mark.parametrize(
        ("a", "b"),
        [
            pytest.param("/busca", "/perfil", id="AC-COR-13-sem-relacao"),
            pytest.param(
                "/api/usuarios", "/api/usuarios-antigos", id="AC-COR-04-fora-da-fronteira"
            ),
            pytest.param("src/models/id.py", "/v1/id", id="AC-COR-06-segmento-curto"),
            pytest.param("", "/busca", id="AC-COR-E3-endpoint-vazio"),
        ],
    )
    def test_incompativeis(self, a, b):
        """Nenhuma das três regras se aplica: não são compatíveis."""
        assert not endpoints_compativeis(a, b)

    def test_simetrica(self):
        """AC-COR-07 — a compatibilidade não depende da ordem dos argumentos."""
        assert endpoints_compativeis("/busca", "src/views/busca.py") == endpoints_compativeis(
            "src/views/busca.py", "/busca"
        )

    def test_canonizacao(self):
        """AC-COR-03 — maiúsculas, extensão, barra repetida e barra final somem."""
        assert canonizar_endpoint("src/views/Busca.py") == "src/views/busca"
        assert canonizar_endpoint("/api//usuarios/") == "/api/usuarios"
        assert canonizar_endpoint("/") == "/"


class TestLerSemgrep:
    def test_le_achado_completo(self):
        """AC-ING-01 — cada resultado vira achado com tipo, endpoint, arquivo e linha."""
        conteudo = json.dumps(
            {
                "results": [
                    {
                        "check_id": "python.flask.security.xss.reflected-xss",
                        "path": "src/views/busca.py",
                        "start": {"line": 42},
                        "extra": {
                            "message": "XSS refletido",
                            "severity": "ERROR",
                            "metadata": {"cwe": ["CWE-79"]},
                        },
                    }
                ]
            }
        )
        resultado = ler_semgrep(conteudo)
        assert len(resultado.achados) == 1
        achado = resultado.achados[0]
        assert achado.origem is Ferramenta.SEMGREP
        assert achado.tipo_vuln == "xss"
        assert achado.arquivo == "src/views/busca.py"
        assert achado.linha == 42
        assert achado.cwe == "CWE-79"

    def test_severidade_original_e_preservada(self):
        """AC-ING-05 — a severidade que a ferramenta reportou chega intacta ao achado."""
        conteudo = json.dumps(
            {
                "results": [
                    {
                        "check_id": "regra.xss",
                        "path": "a.py",
                        "start": {"line": 1},
                        "extra": {"message": "m", "severity": "WARNING"},
                    }
                ]
            }
        )
        assert ler_semgrep(conteudo).achados[0].severidade == "WARNING"

    def test_metadata_route_vira_endpoint(self):
        """AC-ING-11 — `extra.metadata.route` tem precedência sobre o caminho do arquivo."""
        conteudo = json.dumps(
            {
                "results": [
                    {
                        "check_id": "regra.sqli",
                        "path": "src/api/x.py",
                        "start": {"line": 1},
                        "extra": {
                            "message": "m",
                            "severity": "ERROR",
                            "metadata": {"route": "/api/usuarios"},
                        },
                    }
                ]
            }
        )
        assert ler_semgrep(conteudo).achados[0].endpoint == "/api/usuarios"

    def test_entrada_incompleta_e_descartada_com_aviso(self):
        """AC-ING-06 — resultado sem campo obrigatório sai com aviso; os demais passam."""
        from tests.dados import SEMGREP_COM_ENTRADA_INVALIDA

        resultado = ler_semgrep(SEMGREP_COM_ENTRADA_INVALIDA)
        assert len(resultado.achados) == 1
        assert resultado.ignorados == 1
        assert resultado.avisos

    def test_json_invalido_levanta_erro(self):
        """AC-ING-E2 — arquivo que não é JSON válido é recusado explicando o problema."""
        with pytest.raises(ValueError, match="não é um JSON válido"):
            ler_semgrep("{{{ quebrado")

    def test_relatorio_vazio(self):
        """AC-ING-01 — relatório sem resultados produz zero achados, sem erro."""
        assert ler_semgrep(json.dumps({"results": []})).achados == []


class TestLerNuclei:
    def test_le_achado_completo(self):
        """AC-ING-02 — cada linha vira achado com tipo, endpoint, URL e evidência."""
        from tests.dados import NUCLEI_XSS

        resultado = ler_nuclei(NUCLEI_XSS)
        assert len(resultado.achados) == 1
        achado = resultado.achados[0]
        assert achado.origem is Ferramenta.NUCLEI
        assert achado.tipo_vuln == "xss"
        assert achado.endpoint == "/busca"
        assert achado.evidencia == "<script>alert(1)</script>"

    @pytest.mark.parametrize(
        ("resposta", "esperado"),
        [
            ("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>", 200),
            ("HTTP/2 403 Forbidden\r\n\r\n", 403),
            ("HTTP/1.1 500 Internal Server Error\r\n\r\n", 500),
            ("200", 200),
            ("lixo", None),
        ],
    )
    def test_status_http_do_formato_real(self, resposta, esperado):
        """
        AC-ING-02 — o status HTTP é extraído da resposta bruta do Nuclei.

        Regressão: o Nuclei v3 grava a resposta HTTP inteira em "response". O
        parser antigo tentava converter "HTTP/1.1" em número, falhava calado, e
        um campo obrigatório da especificação sumia de todo relatório real.
        """
        entrada = json.dumps(
            {
                "template-id": "t",
                "info": {"name": "XSS", "severity": "high"},
                "matched-at": "https://a.com/x",
                "response": resposta,
            }
        )
        assert ler_nuclei(entrada).achados[0].http_status == esperado

    def test_status_code_explicito_tem_precedencia(self):
        """AC-ING-02 — `status-code` explícito vence a linha de status da resposta."""
        entrada = json.dumps(
            {
                "template-id": "t",
                "info": {"name": "XSS", "severity": "high"},
                "matched-at": "https://a.com/x",
                "response": "HTTP/1.1 200 OK\r\n\r\n",
                "status-code": 301,
            }
        )
        assert ler_nuclei(entrada).achados[0].http_status == 301

    def test_severidade_original_e_preservada(self):
        """AC-ING-05 — a severidade informada pelo Nuclei chega intacta ao achado."""
        entrada = json.dumps(
            {
                "template-id": "t",
                "info": {"name": "XSS", "severity": "critical"},
                "matched-at": "https://a.com/x",
            }
        )
        assert ler_nuclei(entrada).achados[0].severidade == "critical"

    def test_linha_invalida_descartada_com_aviso(self):
        """AC-ING-07 — linha que não é JSON sai com aviso; as demais são processadas."""
        from tests.dados import NUCLEI_COM_LINHA_INVALIDA

        resultado = ler_nuclei(NUCLEI_COM_LINHA_INVALIDA)
        assert len(resultado.achados) == 2
        assert resultado.ignorados == 1

    def test_arquivo_vazio(self):
        """AC-ING-02 — arquivo sem linhas produz zero achados, sem erro."""
        assert ler_nuclei("").achados == []

    def test_linhas_em_branco_sao_ignoradas_sem_aviso(self):
        """AC-ING-E6 — linha em branco não conta como ignorada nem gera aviso."""
        resultado = ler_nuclei("\n\n\n")
        assert resultado.achados == []
        assert resultado.ignorados == 0


def _achado(origem: Ferramenta, tipo: str, endpoint: str, **extras: object) -> AchadoNormalizado:
    return AchadoNormalizado(
        origem=origem,
        tipo_vuln=tipo,
        endpoint=endpoint,
        severidade="high",
        mensagem="m",
        regra_id=f"{tipo}-{origem.value}",
        **extras,  # type: ignore[arg-type]
    )


class TestCorrelacionar:
    def test_mesmo_tipo_e_endpoint_agrupam(self):
        """AC-COR-01 — mesmo tipo e mesmo endpoint viram um grupo correlacionado."""
        grupos = correlacionar(
            [
                _achado(Ferramenta.SEMGREP, "xss", "/busca"),
                _achado(Ferramenta.NUCLEI, "xss", "/busca"),
            ]
        )
        assert len(grupos) == 1
        assert grupos[0].correlacionada

    def test_arquivo_correlaciona_com_rota(self):
        """AC-COR-05, AC-COR-08 — arquivo casa com rota, e o grupo exibe a rota."""
        grupos = correlacionar(
            [
                _achado(Ferramenta.SEMGREP, "xss", "src/views/busca.py"),
                _achado(Ferramenta.NUCLEI, "xss", "/busca"),
            ]
        )
        assert len(grupos) == 1
        assert grupos[0].endpoint == "/busca", "o grupo deve exibir a rota, não o arquivo"

    def test_tipos_diferentes_nao_agrupam(self):
        """AC-COR-02 — mesmo endpoint com tipos diferentes vira grupos separados."""
        grupos = correlacionar(
            [
                _achado(Ferramenta.SEMGREP, "xss", "/busca"),
                _achado(Ferramenta.NUCLEI, "sqli", "/busca"),
            ]
        )
        assert len(grupos) == 2

    def test_endpoints_incompativeis_nao_agrupam(self):
        """AC-COR-13 — mesmo tipo em endpoints sem relação vira grupos separados."""
        grupos = correlacionar(
            [
                _achado(Ferramenta.SEMGREP, "xss", "/busca"),
                _achado(Ferramenta.NUCLEI, "xss", "/perfil"),
            ]
        )
        assert len(grupos) == 2

    def test_so_semgrep_forma_grupo_nao_confirmado(self):
        """AC-COR-09 — achado só do Semgrep vira grupo sem confirmação do Nuclei."""
        grupos = correlacionar([_achado(Ferramenta.SEMGREP, "xss", "/busca")])
        assert len(grupos) == 1
        assert grupos[0].encontrada_semgrep
        assert not grupos[0].confirmada_nuclei
        assert not grupos[0].correlacionada

    def test_so_nuclei_forma_grupo_nao_encontrado_no_codigo(self):
        """AC-COR-10 — achado só do Nuclei vira grupo sem correspondência no Semgrep."""
        grupos = correlacionar([_achado(Ferramenta.NUCLEI, "xss", "/busca")])
        assert len(grupos) == 1
        assert grupos[0].confirmada_nuclei
        assert not grupos[0].encontrada_semgrep
        assert not grupos[0].correlacionada

    @pytest.mark.parametrize(
        "extras",
        [
            pytest.param({"evidencia": "payload"}, id="AC-COR-11-evidencia-extraida"),
            pytest.param({"http_status": 200}, id="AC-COR-11-status-http"),
        ],
    )
    def test_grupo_com_prova_concreta_tem_evidencia(self, extras):
        """Evidência extraída ou status HTTP significam que o Nuclei alcançou o alvo."""
        grupos = correlacionar([_achado(Ferramenta.NUCLEI, "xss", "/busca", **extras)])
        assert grupos[0].tem_evidencia

    def test_grupo_sem_prova_concreta_nao_tem_evidencia(self):
        """AC-COR-11 — achado puramente estático não conta como evidência."""
        grupos = correlacionar([_achado(Ferramenta.SEMGREP, "xss", "src/a/busca.py")])
        assert not grupos[0].tem_evidencia

    def test_cada_achado_em_exatamente_um_grupo(self):
        """AC-COR-14 — nenhum achado se perde e nenhum é contado duas vezes."""
        achados = [
            _achado(Ferramenta.SEMGREP, "xss", "/a"),
            _achado(Ferramenta.NUCLEI, "xss", "/a"),
            _achado(Ferramenta.SEMGREP, "sqli", "/b"),
        ]
        grupos = correlacionar(achados)
        total = sum(len(g.achados) for g in grupos)
        assert total == len(achados)

    def test_ordem_nao_altera_o_resultado(self):
        """AC-COR-07 — a correlação é confluente: a ordem da entrada não muda os grupos."""
        achados = [
            _achado(Ferramenta.SEMGREP, "xss", "src/views/busca.py"),
            _achado(Ferramenta.NUCLEI, "xss", "/busca"),
            _achado(Ferramenta.NUCLEI, "xss", "/perfil"),
        ]

        def assinatura(lista):
            return sorted((g.tipo_vuln, g.endpoint, len(g.achados)) for g in correlacionar(lista))

        assert assinatura(achados) == assinatura(list(reversed(achados)))

    def test_endpoint_canonico_prefere_a_rota_mais_curta(self):
        """AC-COR-08 — entre rotas candidatas vence a mais curta, com desempate alfabético."""
        grupos = correlacionar(
            [
                _achado(Ferramenta.NUCLEI, "xss", "/busca/avancada"),
                _achado(Ferramenta.SEMGREP, "xss", "/busca"),
            ]
        )
        assert len(grupos) == 1
        assert grupos[0].endpoint == "/busca"

    def test_lista_vazia(self):
        """AC-COR-E1 — lista de achados vazia produz lista de grupos vazia, sem erro."""
        assert correlacionar([]) == []


class TestMascaramento:
    @pytest.mark.parametrize(
        ("entrada", "marcador"),
        [
            pytest.param("Servidor em 192.168.0.10", "[IP_MASCARADO]", id="AC-IA-01"),
            pytest.param(
                "Authorization: Bearer abc123def456", "[TOKEN_MASCARADO]", id="AC-IA-02-bearer"
            ),
            pytest.param(
                "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.assinatura",
                "[TOKEN_MASCARADO]",
                id="AC-IA-02-jwt",
            ),
            pytest.param("api_key=AbCdEf0123456789XyZwQrSt", "[API_KEY_MASCARADO]", id="AC-IA-04"),
            pytest.param("password=SenhaSuperSecreta", "[SENHA_MASCARADA]", id="AC-IA-03-password"),
            pytest.param("senha=OutraSenha123", "[SENHA_MASCARADA]", id="AC-IA-03-senha"),
            pytest.param("contato admin@empresa.com.br", "[EMAIL_MASCARADO]", id="AC-IA-06"),
            pytest.param("host 2001:0db8:85a3::8a2e:0370:7334", "[IP_MASCARADO]", id="AC-IA-07"),
        ],
    )
    def test_substitui_dado_sensivel(self, entrada, marcador):
        """As categorias que a especificação §6 manda mascarar antes do envio."""
        assert marcador in mascarar(entrada)

    def test_valor_original_nao_sobrevive(self):
        """AC-IA-01, AC-IA-06 — o valor original não sobra em lugar nenhum do texto."""
        texto = "IP 192.168.0.10 e email admin@empresa.com"
        resultado = mascarar(texto)
        assert "192.168.0.10" not in resultado
        assert "admin@empresa.com" not in resultado

    def test_nomes_internos(self):
        """AC-IA-05 — cada nome interno configurado é substituído literalmente."""
        resultado = mascarar("servidor-prod-01 caiu", ["servidor-prod-01"])
        assert "servidor-prod-01" not in resultado
        assert "[NOME_MASCARADO]" in resultado

    def test_texto_limpo_passa_inalterado(self):
        """AC-IA-08 — texto sem dado sensível volta idêntico."""
        texto = "Nenhum dado sensivel neste texto."
        assert mascarar(texto) == texto

    def test_sem_nomes_internos_nao_quebra(self):
        """AC-IA-08 — sem lista de nomes internos o mascaramento segue funcionando."""
        assert mascarar("texto", None) == "texto"
