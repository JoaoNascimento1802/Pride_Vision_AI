# SDD — Arquitetura, tecnologias e login

## Origem

PDF §8 (Tecnologias), §9 (Arquitetura simplificada), §10 (login simples).

## Contexto

O PDF fixa a stack e o formato da arquitetura. Isso não é detalhe de implementação livre —
é requisito, e trocar qualquer peça exige AC novo.

```
[React]
   ↓
[API FastAPI]
   ├── Aplicações
   ├── Uploads
   ├── Vulnerabilidades
   ├── Correlação
   ├── Risco
   ├── IA
   └── Status de correção
   ↓
[SQLite]
```

> "A arquitetura ainda será um monólito, ou seja, um único backend organizado por módulos.
> Não serão usados microserviços, Kubernetes ou infraestrutura complexa."

## Requisitos funcionais

- RF-1: Frontend em React com Vite, TypeScript, Tailwind CSS, React Router, Axios e
  Recharts.
- RF-2: Backend em Python com FastAPI, Pydantic, SQLAlchemy e SQLite, expondo API REST.
- RF-3: IA por OpenAI ou Gemini.
- RF-4: Monólito organizado por módulos — sem microserviços, sem Kubernetes.
- RF-5: Login simples.

## Considerações de segurança

- `SECRET_KEY` vem do ambiente. Ausente, uma chave aleatória é gerada e a aplicação avisa;
  fraca (menos de 32 bytes), avisa também. Quem descobre a chave forja token de qualquer
  usuário.
- Senha guardada com bcrypt, nunca em texto.
- CORS libera apenas as origens configuradas.
- Chaves de IA só do ambiente. `.env` não é versionado.

## Critérios de aceitação — testáveis

### Arquitetura

- **AC-ARQ-01** — Dado a aplicação iniciada, quando a rota de saúde é consultada, então
  responde 200 com o status, a versão e se a IA está configurada.
- **AC-ARQ-02** — Dado a aplicação iniciada, quando a rota de opções é consultada, então
  devolve o vocabulário controlado de ambientes, exposições, importâncias, riscos e status,
  cada um com slug e rótulo.
- **AC-ARQ-03** — Dado a API montada, quando as rotas são inspecionadas, então existem os
  sete módulos do §9: aplicações, uploads, vulnerabilidades, correlação e risco (via
  ingestão), IA e status de correção.
- **AC-ARQ-04** `[extensão]` — Dado os módulos de serviço puros (`normalizer`,
  `correlator`, `data_masker`, `risk_engine`), quando suas importações são inspecionadas,
  então nenhum importa `sqlalchemy`: a regra de negócio não conhece persistência.
- **AC-ARQ-05** — Dado a configuração padrão, quando o banco é resolvido, então é SQLite.
- **AC-ARQ-06** `[proibição]` — Dado o código do backend, quando inspecionado, então não há
  dependência de orquestrador, fila, cache distribuído ou segundo serviço — o monólito é
  um processo só.

### Configuração

- **AC-ARQ-07** — Dado um arquivo `.env`, quando a configuração é carregada, então os pares
  `CHAVE=VALOR` viram variáveis de ambiente sem sobrescrever as já definidas.
- **AC-ARQ-08** — Dado `SECRET_KEY` ausente, quando a configuração é lida, então uma chave
  aleatória é gerada e a aplicação sinaliza que ela não foi definida.
- **AC-ARQ-09** — Dado `SECRET_KEY` com menos de 32 bytes, quando a configuração é lida,
  então é sinalizada como fraca.
- **AC-ARQ-10** — Dado `AI_DEFAULT_PROVIDER` e a chave correspondente, quando a
  configuração é lida, então a IA é reportada como configurada; sem a chave, como não
  configurada.
- **AC-ARQ-11** `[extensão]` — Dado `MAX_UPLOAD_BYTES` definido no ambiente, quando a
  configuração é lida, então o limite de upload passa a ser esse valor.
- **AC-ARQ-12** `[extensão]` — Dado `PRIDE_INTERNAL_NAMES` com nomes separados por vírgula,
  quando a configuração é lida, então vira a lista de nomes internos usada no mascaramento.
- **AC-ARQ-13** `[extensão]` — Dado `CORS_ORIGINS` definido, quando a aplicação sobe, então
  apenas essas origens são liberadas.

- **AC-ARQ-14** `[extensão]` — Dado `OPENAI_MODELS` ou `GEMINI_MODELS` no ambiente, como
  lista separada por vírgula, quando a configuração é lida, então vira a lista de modelos
  candidatos daquele provedor, na ordem informada.

- **AC-ARQ-15** `[extensão]` — Dado nenhuma variável de modelo definida, quando a
  configuração é lida, então valem as listas padrão do projeto, e `OPENAI_MODEL` e
  `GEMINI_MODEL` ficam vazios.

- **AC-ARQ-16** `[extensão]` — Dado o provedor ativo e a configuração de modelos, quando o
  modelo previsto é consultado, então é o modelo explícito quando houver, e o primeiro
  candidato da lista quando não houver.

> **Por que normalizar o esquema da URL do banco.** `AC-ARQ-05` mantém SQLite como padrão,
> e é o que continua valendo em desenvolvimento. Mas hospedagem gratuita não tem disco
> persistente: publicar exige um Postgres gerenciado, e a string que eles entregam nunca
> declara o driver — vem como `postgres://…` (formato histórico da libpq) ou
> `postgresql://…`. Nenhum dos dois serve como está:
>
> - `postgres://` o SQLAlchemy 2.0 recusa de saída, com
>   `Can't load plugin: sqlalchemy.dialects:postgres`;
> - `postgresql://` ele aceita, **e então resolve para o psycopg2** — que este projeto não
>   usa. O erro vira `ModuleNotFoundError: No module named 'psycopg2'`, apontando para uma
>   dependência ausente em vez de para o esquema da URL.
>
> O segundo caso é o mais traiçoeiro, porque a URL parece correta. Normalizar os dois para
> o driver que o projeto realmente instala (`psycopg`, versão 3) é o que permite colar a
> string como o provedor entregou.

- **AC-ARQ-17** `[extensão]` — Dado `DATABASE_URL` sem driver declarado, em qualquer das
  duas formas que os provedores entregam (`postgres://…` ou `postgresql://…`), quando a
  configuração é lida, então o esquema é normalizado para `postgresql+psycopg://…`; dado
  um esquema que já declara o driver (`postgresql+psycopg://`, `postgresql+asyncpg://`) ou
  outro banco (`sqlite:///…`), então a string é preservada intacta.

> **Por que o PRAGMA precisa ser exclusivo do SQLite.** `AC-INV-09` (remoção em cascata)
> depende de `PRAGMA foreign_keys=ON`, porque o SQLite ignora chave estrangeira por
> padrão. Esse PRAGMA estava registrado no evento `connect` da classe `Engine`, o que o
> fazia disparar para **qualquer** banco. No Postgres ele é sintaxe inválida — e o erro,
> mesmo capturado e silenciado, **aborta a transação**: todo statement seguinte na mesma
> conexão falha com `InFailedSqlTransaction`. Na prática, toda conexão Postgres nascia
> inutilizável, e a suíte não percebia porque roda inteira em SQLite.

- **AC-ARQ-18** `[extensão]` — Dado um banco que não é SQLite, quando uma conexão é
  aberta, então o `PRAGMA foreign_keys=ON` não é executado e a conexão continua utilizável;
  dado SQLite, então o PRAGMA é executado e as chaves estrangeiras passam a valer, que é o
  que `AC-INV-09` exige.

> **Por que a saúde não pode morrer junto com o banco.** `criar_tabelas()` roda na
> inicialização. Quando ela levanta — banco inacessível, credencial errada, disco somente
> leitura na hospedagem —, a exceção derruba o processo inteiro, e a plataforma responde
> com o erro genérico do provedor em **todas** as rotas, inclusive na de saúde. O efeito é
> perverso: a única rota cuja função é dizer o que está errado é a primeira a parar de
> responder, e sobra um 500 opaco sem diagnóstico. A saúde precisa sobreviver para
> apontar o culpado.
>
> O texto do erro vai mascarado porque `AC-ARQ-01` deixa esta rota **sem autenticação**:
> mensagem de driver costuma carregar host e usuário do banco, e isso não pode vazar para
> quem só abriu a URL.

- **AC-ARQ-19** `[extensão]` — Dado que o banco está inacessível na inicialização, quando
  a aplicação sobe, então ela sobe mesmo assim e a rota de saúde responde 200 com
  `status: "degradado"` e o motivo no campo `banco`, passado por `mascarar()`; dado o banco
  acessível, então `banco` é `"ok"` e `status` segue `"ok"`.

> **Por que o engine não pode nascer no import.** `create_engine()` parece inofensivo e
> não é: ele resolve o dialeto e **importa o driver na hora**. Driver ausente do pacote ou
> URL malformada viram, então, erro de *import* — e `app/database.py` deixa de carregar,
> levando junto todo módulo que depende dele, que é o produto inteiro. Numa hospedagem
> serverless isso derruba a função antes de qualquer rota existir: até `GET /api/opcoes`,
> que só enumera constantes e nunca encosta no banco, passa a responder o erro genérico do
> provedor. `AC-ARQ-19` não alcança esse caso, porque o `lifespan` nem chega a rodar.

- **AC-ARQ-20** `[extensão]` — Dado `DATABASE_URL` com driver ausente ou esquema inválido,
  quando os módulos da aplicação são importados, então o import conclui e nenhuma conexão
  é tentada; a rota de saúde responde 200 relatando o problema e as rotas que não usam
  banco seguem funcionando. O engine é criado no primeiro uso, não na importação.

> **Por que a lista de dependências é um critério.** `EmailStr` do Pydantic exige o pacote
> `email-validator` **em tempo de importação**: sem ele, definir o schema levanta
> `ImportError`, e a falha não fica contida na validação de e-mail — derruba
> `schemas/auth.py`, depois `routers/auth.py`, depois `app/main.py`, ou seja, a aplicação
> inteira. O `email-validator` não estava declarado no `pyproject.toml` e o projeto
> funcionava assim mesmo, porque o interpretador de desenvolvimento é compartilhado com
> outros projetos que o instalam. Numa instalação limpa — que é o que toda hospedagem
> faz — nada subia. Dependência que só existe por acidente é dependência que falta.

- **AC-ARQ-21** `[extensão]` — Dado que os schemas usam `EmailStr`, quando as dependências
  declaradas são inspecionadas, então `pydantic` aparece com o extra `email`, de forma que
  uma instalação limpa a partir do `pyproject.toml` seja suficiente para importar a
  aplicação.

### Login simples

- **AC-LOGIN-01** — Dado um e-mail e uma senha novos, quando o registro é feito, então o
  usuário é criado e a senha é guardada como hash, nunca em texto.
- **AC-LOGIN-02** — Dado credenciais corretas, quando o login é feito, então a API devolve
  um token e os dados do usuário.
- **AC-LOGIN-03** — Dado credenciais incorretas, quando o login é tentado, então a API
  responde 401.
- **AC-LOGIN-04** — Dado um e-mail que não existe e uma senha errada de e-mail existente,
  quando os dois logins são tentados, então a mensagem de erro é **a mesma** — não se
  revela quais e-mails estão cadastrados.
- **AC-LOGIN-05** — Dado um token válido, quando a rota de identificação é chamada, então
  devolve o usuário do token.
- **AC-LOGIN-06** — Dado um token ausente, inválido ou expirado, quando uma rota protegida
  é chamada, então a API responde 401.
- **AC-LOGIN-07** `[extensão]` — Dado um e-mail já cadastrado, quando o registro é
  repetido, então a API responde 409.
- **AC-LOGIN-08** `[extensão]` — Dado um e-mail com maiúsculas ou espaços, quando o
  registro e o login são feitos, então funcionam: o e-mail é normalizado.

## Casos de borda

- **AC-ARQ-E1** — Dado um `.env` inexistente, quando a configuração é carregada, então nada
  quebra e valem os padrões.
- **AC-ARQ-E2** `[extensão]` — Dado um `.env` com linha em branco, comentário ou linha sem
  `=`, quando carregado, então essas linhas são ignoradas.
- **AC-LOGIN-E1** `[extensão]` — Dado uma senha acima do limite suportado pelo bcrypt,
  quando o registro é tentado, então a API responde 422 explicando, em vez de truncar em
  silêncio.
- **AC-LOGIN-E2** — Dado um e-mail em formato inválido, quando o registro é tentado, então
  a API responde 422.

- **AC-LOGIN-E3** `[extensão]` — Dado uma senha abaixo do comprimento mínimo, quando o
  registro é tentado, então a API responde 422.

## Restrições conscientes

- **Não há sistema de migrações.** As tabelas são criadas na inicialização, mas coluna nova
  não é acrescentada a tabela existente. Em desenvolvimento: apagar
  `backend/pride_vision.db` e rodar `popular_demo.py`. Publicar com dado real exigiria
  Alembic — está fora do MVP.
- **Login sem papéis nem permissões.** Todo usuário autenticado enxerga todas as
  aplicações. É a leitura literal de "login simples" no §10; isolamento por empresa seria
  outro projeto.
- **Sem refresh token.** O token expira em 480 minutos por padrão e o usuário faz login de
  novo.
- **Sem rate limiting** no login. Fora do escopo do MVP.

## Validação real

- Fluxo: subir backend e frontend → `GET /api/saude` → registrar usuário → login → chamar
  uma rota protegida com e sem token.
- O que deve aparecer: 200 na saúde com a versão; 401 sem token; 200 com token.
- Critério: nenhum aviso de `SECRET_KEY` no boot quando o `.env` está preenchido.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
