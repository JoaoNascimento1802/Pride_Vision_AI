# Observability (Observabilidade da Plataforma)

A plataforma necessita de telemetria nativa para monitoramento de saúde, performance e confiabilidade, expondo métricas de negócio e logs estruturados em JSON para análise.

## Critérios de Aceite

- **AC-OBS-01**
  Dado que uma requisição é feita para a plataforma
  Quando o backend processa o acesso
  Então deve inserir um `request_id` nos logs JSON estruturados

- **AC-OBS-02**
  Dado que um middleware de telemetria está ativo
  Quando uma rota é completada
  Então o sistema deve incrementar o Prometheus counter com rota e status code

- **AC-OBS-03**
  Dado que a aplicação possui telemetria
  Quando um usuário tenta acessar `/metrics`
  Então deve retornar dados Prometheus para ADMIN e HTTP 403 para os demais

- **AC-OBS-04**
  Dado o sistema de health check
  Quando a rota `/api/health` é chamada
  Então deve atestar o banco de dados e retornar `up` ou HTTP 503

- **AC-OBS-05**
  Dado o frontend da plataforma
  Quando a tela "System Health" é acessada por admin
  Então deve consumir `/health` e mostrar métricas e volume
