# 14. Jira Ticketing OAuth 2.0 (3LO)

O PRIDE Vision AI permite a criacao e atualizacao de tickets de remediacao no Jira Cloud de forma rastreavel e autenticada via OAuth 2.0. Isso garante a seguranca sem a necessidade de expor ou exigir API Tokens manuais.

## 14.1. Autorizacao (OAuth 2.0)

- **AC-JIRA-01** — Iniciar fluxo de autorizacao. **Dado** um usuario autenticado, **Quando** chamar `GET /api/integrations/jira/authorize`, **Entao** recebe uma URL contendo os parametros corretos (client_id, redirect_uri, scope, state JWT criptograficamente assinado).
- **AC-JIRA-02** — State invalido bloqueia callback. **Dado** um callback OAuth, **Quando** o state for ausente, expirado ou forjado, **Entao** a API rejeita com HTTP 400.
- **AC-JIRA-03** — Token exchange bem sucedido salva credenciais. **Dado** um authorization code valido, **Quando** chamar `GET /api/integrations/jira/callback`, **Entao** o PRIDE troca o code pelo token na Atlassian, consulta as `accessible-resources`, salva as credenciais e redireciona o usuario para a UI.

## 14.2. Segurança e Armazenamento

- **AC-JIRA-04** — Criptografia de Tokens. **Dado** que os tokens (access e refresh) serao armazenados, **Quando** forem gravados no banco de dados, **Entao** devem usar criptografia simetrica (AES/Fernet) gerenciada no servidor.
- **AC-JIRA-05** — Renovaçao Automatica (Refresh). **Dado** um access_token expirado, **Quando** uma operação do Jira for tentada, **Entao** o sistema deve usar o refresh token, obter um novo token, gravar no banco e tentar novamente.

## 14.3. Criaçao e Sincronizacao de Issues

- **AC-JIRA-06** — Criação real de Issue. **Dado** uma Vulnerabilidade com provider Jira, **Quando** criar o ticket, **Entao** faz uma requisição HTTP real à API do Jira Cloud com payload ADF incluindo dados vitais sem incluir credenciais e persiste no banco.
- **AC-JIRA-07** — Sync de Status. **Dado** um ticket Jira ja criado, **Quando** sincronizado, **Entao** deve refletir o titulo e o status mapeado localmente, atualizando o Ticket.
- **AC-JIRA-08** — Falha de comunicação e permissão. **Dado** um ticket e token invalido não-renovavel ou erro 403, **Quando** chamar a API, **Entao** deve tratar o erro de forma tolerante sem derrubar o PRIDE.
- **AC-JIRA-09** — Conexão Múltipla. **Dado** que o sistema suporta integração 3LO, **Quando** múltiplos usuários se conectam ao Jira, **Entao** a conexão é realizada via Integration associada ao usuário no sistema, permitindo operação baseada na conta Jira autorizada individualmente.
