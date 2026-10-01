# SDD/23-multi-tenancy-sso.md — Isolamento Multi-Tenant e SSO Corporativo

## Objetivo
Transformar o PRIDE Vision AI em uma plataforma B2B SaaS, isolando os dados por Tenant (cliente/organização) e permitindo autenticação corporativa via SSO (Single Sign-On).

## Critérios de Aceitação

- **AC-MT-01**
  **Dado** que um usuário faz login via SSO Corporativo
  **Quando** o domínio do e-mail bater com o `domain` de um Tenant cadastrado
  **Então** o backend deve provisionar o usuário (JIT) e associá-lo ao Tenant, retornando um JWT válido.

- **AC-MT-02**
  **Dado** que o banco de dados armazena aplicações, integrações e vulnerabilidades de múltiplos Tenants
  **Quando** um usuário autenticado no Tenant A acessar `/api/v1/applications`
  **Então** o sistema deve aplicar Row-Level Security via SQLAlchemy e retornar EXCLUSIVAMENTE os dados do Tenant A.

- **AC-MT-03**
  **Dado** um usuário com múltiplas associações na tabela `TenantUser`
  **Quando** ele acessar a interface web
  **Então** o frontend deve exibir um modal/seletor de Workspace (Tenant) no cabeçalho e armazenar a seleção no header `X-Tenant-ID`.

- **AC-MT-04**
  **Dado** uma base de dados legada sem `tenant_id`
  **Quando** o sistema for atualizado
  **Então** uma migration Alembic deve criar um "Default Organization" e migrar todos os usuários e dados para ele, sem corromper as informações originais.
