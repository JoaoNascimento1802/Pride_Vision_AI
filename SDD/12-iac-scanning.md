# 12. Infrastructure as Code (IaC) Scanning

O PRIDE Vision AI integra achados de infraestrutura como código (IaC) de ferramentas como Checkov, consolidando riscos de configuração na mesma plataforma que vulnerabilidades de código e dependências.

## 12.1. Ingestão de Relatórios (Checkov)

- **AC-IAC-01** — Parser extrai recursos. **Dado** um relatório JSON válido do Checkov, **Quando** for parseado por ler_checkov, **Então** deve extrair os recursos, arquivo, linha e framework e mapeá-los para o `AchadoNormalizado` com origem `checkov`.
- **AC-IAC-02** — Arquivo vazio levanta exceção. **Dado** uma string vazia, **Quando** for parseada por ler_checkov, **Então** a função levanta ValueError.
- **AC-IAC-03** — JSON inválido levanta exceção. **Dado** uma string JSON quebrada, **Quando** for parseada por ler_checkov, **Então** a função levanta ValueError.
- **AC-IAC-04** — Checkov report faltando campos. **Dado** um finding sem check_id ou check_name, **Quando** for parseado, **Então** o item é pulado e incrementa ignorados.
- **AC-IAC-05** — Múltiplos findings no JSON. **Dado** um array de relatórios gerado pelo Checkov, **Quando** parseado, **Então** o parser deve extrair os achados de todos os relatórios da lista.
