# Remediation Workflow Implementation

## O que foi feito
1. **Frontend**: Criados os painéis `PainelOwner`, `PainelComentarios` e `PainelEvidencias` em `DetalheVulnerabilidade.tsx`.
2. **Frontend API**: Atualizado `client.ts` com as novas funções para atribuição, comentários, evidências e envio de justificativa (`reason`) ao alterar status.
3. **Frontend Tipos e Mock**: Atualizado `BadgeStatus` para incluir os novos estados da State Machine e ajustado o mock de teste.
4. **Testes**: Criado o suíte de testes `test_remediation.py` cobrindo o ciclo de remediação, comentários, evidências e transição de estado.
5. **Roadmap**: Atualizado via Python para marcar `Remediation` como IMPLEMENTADO e `SLA` como AUSENTE.

## O que falta para ficar verde
- Alguns testes de integração legados (em `test_vulnerabilities.py`, `test_audit.py`, `test_applications.py`, etc) precisam ser ajustados pois a nova State Machine (`TRANSICOES_VALIDAS`) passou a rejeitar transições diretas de `NOVA` para `EM_CORRECAO` e `CORRIGIDA` sem passar por `EM_ANALISE`.
- O script de rastreabilidade (gate) apontou 21 ACs órfãos da Spec de Remediation (ex: AC-REM-01, AC-REM-02). É necessário criar um teste correspondente para cada um desses critérios de aceitação para o gate ficar verde.

