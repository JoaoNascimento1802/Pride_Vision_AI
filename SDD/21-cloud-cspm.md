# SDD: 21-cloud-cspm

## Contexto

Integração com ferramentas de CSPM para visão unificada "Code to Cloud" e detecção de Toxic Combinations.

## Critérios de Aceitação

- **AC-CSPM-01** - Ingestão e deduplicação CSPM. **Dado** um payload de CSPM recebido no webhook, **Quando** o sistema processá-lo, **Então** deve extrair conta, recurso e detalhes do achado, normalizando para a Ferramenta CLOUD_POSTURE e deduplicando por hit_count.
- **AC-CSPM-02** - Toxic Combination na Nuvem. **Dado** um alerta de CSPM Crítico de exposição para internet recebido, **Quando** houver vulnerabilidade estática do tipo RCE na mesma aplicação associada, **Então** o sistema deve elevar o risco da vulnerabilidade RCE para CRITICO e marcá-la como Toxic Combination com SLA recalculado.
