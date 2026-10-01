# SDD: 20-runtime-ebpf

## Contexto

Esta especificação define a integração com agentes de Runtime Security (ex: Falco, Tetragon).
A funcionalidade eleva o PRIDE de uma plataforma puramente estática para uma que reage ativamente a eventos do cluster, correlacionando o que foi descoberto na imagem com o que de fato está rodando e sendo acessado.

## Critérios de Aceitação

- **AC-RT-01** - Ingestão e deduplicação de eventos. **Dado** um payload de evento de runtime recebido no webhook, **Quando** o sistema processá-lo, **Então** deve extrair `container_id`, `proc.name`, `evt.type`, identificar a aplicação via container, registrar a telemetria, e agregar temporalmente eventos repetidos usando `hit_count`.
- **AC-RT-02** - Correlação de ameaças em execução (Reachability). **Dado** um evento contendo informações de execução (`proc.name`), **Quando** houver uma vulnerabilidade latente na mesma aplicação cujo identificador estático coincida com o processo/evento reportado, **Então** o risco da vulnerabilidade deve ser alterado para CRÍTICO e sua SLA recalculada automaticamente.
- **AC-RT-03** - Selo visual de ameaça (Frontend). **Dado** uma vulnerabilidade que tenha achados correlacionados à ferramenta RUNTIME, **Quando** o usuário acessar a página de detalhamento, **Então** um bloco visual de "Ameaça em Execução" (REACHABLE) e os detalhes de telemetria em tempo real devem ser exibidos de forma destacada.
