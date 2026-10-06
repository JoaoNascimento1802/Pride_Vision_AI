# Publicar o PRIDE Vision AI de graça

Guia reproduzível para colocar a plataforma no ar sem gastar nada e sem cartão de crédito.
Leva cerca de 30 minutos na primeira vez.

> Para entender o projeto, veja `ENTENDA_O_PROJETO.md`. Para rodar na sua máquina,
> `COMO_USAR.md`.

---

## O que você vai ter no final

**Um projeto só na Vercel, com dois serviços no mesmo domínio.**

```
  https://pride-vision-platform.vercel.app
                    │
      ┌─────────────┴─────────────┐
      │                           │
  /api/(.*)                    /(.*)
      │                           │
      ▼                           ▼
 ┌──────────┐              ┌────────────┐
 │ backend/ │              │ frontend/  │
 │ FastAPI  │              │ Vite build │
 └──────────┘              └────────────┘
      │
      ▼
  Neon · Postgres gratuito, 0,5 GB, permanente
```

Isso usa **Vercel Services**: vários serviços dentro de um projeto, construídos
separadamente e servidos por um domínio comum. A configuração está em `vercel.json`, na
raiz do repositório — você não precisa escrever nada.

### As duas consequências que simplificam tudo

**1. Não existe CORS.** Frontend e API estão na mesma origem. A variável `CORS_ORIGINS`
fica irrelevante em produção (o middleware só age em requisição de outra origem).

**2. Não existe `VITE_API_URL`.** O `src/api/client.ts` usa `baseURL` vazio e chama
caminhos relativos (`/api/…`). Em desenvolvimento o proxy do Vite resolve; em produção o
roteamento da Vercel resolve. **Não defina `VITE_API_URL`** — definir quebraria isso,
transformando as chamadas em absolutas e reintroduzindo CORS.

> **Por que o prefixo `/api` não atrapalha.** A documentação da Vercel é explícita: o
> serviço recebe o caminho original. `GET /api/saude` chega ao FastAPI como `/api/saude`,
> não como `/saude`. Como as rotas do projeto já nascem com o prefixo `/api`, elas casam
> direto — sem transformação de caminho, sem `root_path`.

### Por que este arranjo, e não outro

| Alternativa | Por que não |
|---|---|
| SQLite em arquivo, como no desenvolvimento | Nenhuma hospedagem gratuita tem disco persistente. O banco seria apagado a cada reinício ou novo deploy |
| Dois projetos separados na Vercel | Funciona, mas exige CORS, `VITE_API_URL` e dois domínios para manter em sincronia. Fica como plano B abaixo |
| Fly.io | O plano gratuito virou um teste de 2 horas |
| Koyeb | Fechou o tier gratuito depois da aquisição pela Mistral |
| Postgres gratuito da Render | **Expira 30 dias** depois de criado |

O Neon foi escolhido porque o plano gratuito é **permanente** (não é teste), não pede
cartão, e o banco não é apagado por inatividade — no máximo é suspenso se você estourar a
cota do mês, e volta sozinho.

### O que já está pronto no repositório

Você não precisa mexer em código:

| Arquivo | Para quê |
|---|---|
| `vercel.json` (raiz) | Declara os dois serviços, o roteamento e o que fica fora do pacote |
| `backend/.python-version` | Fixa o Python 3.12 |
| `backend/pyproject.toml` | Declara o entrypoint e o driver do Postgres |
| `.gitignore` | Já bloqueia `.env`, `*.db` e `node_modules` |

---

## Antes de começar

| Conta | Onde | Cartão? |
|---|---|---|
| GitHub | github.com | não |
| Vercel | vercel.com — entre com o GitHub | não |
| Neon | neon.com | não |

E, opcionalmente, uma chave de IA:

| Provedor | Onde | Custo |
|---|---|---|
| **Google Gemini** (recomendado) | https://aistudio.google.com/apikey | tem plano gratuito |
| OpenAI | https://platform.openai.com/api-keys | pago, sem plano gratuito |

> **Sem chave de IA a plataforma funciona inteira.** Inventário, upload, correlação,
> risco, status e dashboard seguem normais; só o botão "Gerar explicação" responde que a
> IA não está configurada. É comportamento especificado (`AC-IA-20`), não uma falha.

---

## Passo 1 — Criar o banco no Neon

1. Entre em https://neon.com e crie um projeto (região mais próxima; o nome não importa).
2. Na tela de conexão, copie a **connection string**. Prefira a opção **Pooled
   connection** — o endereço dela tem `-pooler` no meio.

Vai ser algo como:

```
postgres://usuario:senha@ep-algo-123-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require
```

> **Cole exatamente como veio**, nas duas formas que o Neon oferece (`postgres://…` ou
> `postgresql://…`). O sistema aponta as duas para o driver que o projeto instala,
> `postgresql+psycopg://` (`AC-ARQ-17`). Você não precisa editar nada — e não adianta
> "consertar" `postgres://` para `postgresql://` à mão: sem o driver declarado, o
> SQLAlchemy escolheria o psycopg2, que não é dependência deste projeto.
>
> **Por que a versão *pooled*:** a API sobe do zero depois de um período parada e abre
> conexão nova a cada vez. Sem o pool, isso consome os slots de conexão do Neon rápido.

Guarde a string. Ela é uma senha — não coloque em nenhum arquivo do repositório.

---

## Passo 2 — Gerar a chave de sessão

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Guarde o resultado. Sem essa chave fixa, uma nova é gerada a cada partida do processo e
todo mundo é deslogado sem aviso.

---

## Passo 3 — Importar na Vercel

Em vercel.com: **Add New → Project** → importe `pride-vision-platform`.

Na tela **New Project**, confira:

| Campo | Valor |
|---|---|
| Vercel Team | `lauiskk's projects` (Hobby) |
| Project Name | `pride-vision-platform` |
| **Root Directory** | `./` — a raiz, **não** `frontend` nem `backend` |
| Application Preset | deixe em **Other**, se puder escolher |

> **Se o campo "Application Preset" estiver marcado como Angular** (ou qualquer outro
> framework), ignore ou troque para "Other". Essa detecção é um palpite feito antes de a
> Vercel ler o `vercel.json`, e o `vercel.json` da raiz tem precedência — ele já declara
> `vite` para o frontend e `fastapi` para o backend.

A tela deve listar os dois serviços detectados:

```
pride-vision-platform
├── frontend   /       Vite
└── backend    /api    FastAPI
```

Se listar exatamente isso, o `vercel.json` foi lido e o roteamento está certo.

### As variáveis de ambiente

Ainda na tela de importação, abra **Environment Variables** e adicione:

| Nome | Valor | Obrigatório |
|---|---|---|
| `DATABASE_URL` | a string *pooled* do Neon | sim |
| `SECRET_KEY` | a chave gerada no passo 2 | sim |
| `MAX_UPLOAD_BYTES` | `4000000` | sim |
| `AI_DEFAULT_PROVIDER` | `gemini` | se for usar IA |
| `GEMINI_API_KEY` | sua chave do Google AI Studio | se for usar IA |

**Não defina `VITE_API_URL`** e **não defina `CORS_ORIGINS`** — veja a explicação lá em
cima.

> **Por que `MAX_UPLOAD_BYTES=4000000` e não os 20 MB do padrão.** Funções da Vercel
> recusam qualquer requisição com corpo acima de **4,5 MB**, antes de a aplicação ver o
> arquivo — e o erro que aparece é um 413 sem explicação. Com o limite do sistema abaixo
> do limite da plataforma, quem enviar um relatório grande recebe a mensagem em português
> dizendo qual é o teto.

Clique em **Deploy**.

---

## Passo 4 — Conferir que subiu

Quando o build terminar, abra `https://<seu-projeto>.vercel.app/api/saude`:

```json
{"status":"ok","versao":"0.1.0","ia_configurada":true,
 "provedor_ia":"gemini","modelo_ia":"gemini-flash-latest"}
```

Se isso responder, os dois serviços estão de pé e o roteamento está certo — foi o
frontend que serviu o domínio e o backend que atendeu `/api`.

---

## Passo 5 — Povoar a demonstração (opcional)

Para a plataforma já abrir com dados em vez de telas vazias, aponte o backend **local**
para o banco do Neon e rode o script de demonstração. Os dados vão para o mesmo banco que
a API publicada usa.

Crie `backend/.env` (não vai para o repositório) com:

```
DATABASE_URL=postgres://…a mesma string do Neon…
SECRET_KEY=…a mesma chave…
```

Depois, em dois terminais:

```bash
cd backend && python -m uvicorn app.main:app --port 8000
```

```bash
cd backend && python popular_demo.py
```

O script cria 5 aplicações em contextos diferentes, envia os relatórios de exemplo e já
deixa duas vulnerabilidades com status alterado. Depois disso, entre pela URL publicada
com **`ana@exemplo.com`** / **`senha-de-demonstracao`**.

Terminado o povoamento, apague o `backend/.env` — senão o desenvolvimento local passa a
mexer no banco de produção sem você perceber.

---

## Validação — o que conferir, na ordem

Não basta o deploy dizer "Ready". Percorra o fluxo:

1. `GET /api/saude` responde `"status":"ok"` e mostra qual modelo de IA está ativo.
2. A tela de login abre e você consegue criar uma conta.
3. Cadastrar uma aplicação em **Produção / Internet / Importância alta**.
4. Enviar os dois relatórios (Semgrep e Nuclei) com o mesmo XSS.
5. Na lista, a vulnerabilidade aparece **correlacionada**, com risco **Crítico** e as
   duas ferramentas na coluna Origem.
6. No detalhe, **Gerar explicação** preenche os seis blocos da IA.
7. Editar a aplicação para ambiente **Teste** e reabrir o detalhe: o risco cai para
   **Médio** e a justificativa é reescrita citando o novo ambiente.
8. Mudar o status para **Em correção**: o histórico registra autor e data, e o dashboard
   reconta.

Se os oito passarem, está publicado de verdade.

---

## Quando der errado

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Todas as rotas da API dão 404 | `VITE_API_URL` foi definida, ou o `vercel.json` da raiz não subiu | Apague a variável e faça redeploy; confira que `vercel.json` está no commit |
| Tela diz "Não foi possível falar com o servidor" | O serviço do backend não subiu | Veja os build logs do serviço `backend` no painel |
| `Can't load plugin: sqlalchemy.dialects:postgres` | Versão do código anterior à normalização da URL | Confira que `backend/app/config.py` tem `_normalizar_url_do_banco` |
| `502` ao gerar a explicação | Chave de IA inválida, sem cota, ou modelo aposentado | Veja `modelo_ia` em `/api/saude`; a mensagem de erro do Gemini lista os modelos que a sua chave aceita — copie um para `GEMINI_MODEL` |
| `503` ao gerar a explicação | Não há chave para o provedor selecionado | Confira `AI_DEFAULT_PROVIDER` e a chave correspondente |
| `413` ao enviar relatório | Arquivo acima de 4,5 MB | Limite da plataforma, não do sistema. Use um relatório menor ou mude o backend para a Render |
| Recarregar em `/vulnerabilidades/7` dá 404 | O rewrite de SPA do serviço `frontend` não foi aplicado | Confira o bloco `rewrites` dentro de `services.frontend` no `vercel.json` |
| Primeira requisição do dia demora | A função subiu do zero e recriou a conexão | Normal. As seguintes são rápidas |
| Login some sozinho | `SECRET_KEY` não definida — uma nova é gerada a cada partida e invalida os tokens | Defina `SECRET_KEY` nas variáveis |

---

## Os limites do plano gratuito

| | Vercel Hobby | Neon Free |
|---|---|---|
| Custo | $0 | $0 |
| Cartão | não pede | não pede |
| Duração máxima da requisição | 300 s | — |
| Memória | 2 GB | até 8 GB de RAM no autoscale |
| **Corpo da requisição** | **4,5 MB** | — |
| Banda | 100 GB/mês | — |
| Armazenamento | — | 0,5 GB por projeto |
| Computação | — | 100 CU-horas/mês |
| Validade | permanente | permanente |

> **Uso pessoal e não comercial.** O plano Hobby da Vercel é restrito, pelos termos de
> uso, a projeto pessoal ou não comercial. Trabalho de faculdade e portfólio se
> enquadram; cobrar por isso, não.
>
> Se estourar a cota do Neon, o banco é **suspenso até o mês virar**, não apagado. Os
> dados continuam lá.

---

## Plano B — dois projetos separados

Se o recurso **Services** não estiver liberado para a sua conta, dá para publicar do jeito
tradicional: dois projetos da Vercel apontando para o mesmo repositório, cada um com um
*Root Directory* diferente. Aí o CORS volta a existir e é preciso:

1. Projeto `pride-api`, Root Directory `backend`, com as variáveis do passo 3 **mais**
   `CORS_ORIGINS` = a URL do frontend.
2. Projeto `pride-web`, Root Directory `frontend`, framework Vite, com
   `VITE_API_URL` = a URL do backend (sem barra no final).
3. Recriar `frontend/vercel.json` com o rewrite de SPA:
   `{"rewrites":[{"source":"/(.*)","destination":"/index.html"}]}`.
4. `VITE_API_URL` é lida em tempo de **build** — mudá-la exige um novo deploy.

## Plano C — backend na Render

Se a função Python da Vercel der problema, o backend roda igual na Render, com o **mesmo
banco Neon**:

1. render.com → **New → Web Service** → conecte o repositório.
2. Root Directory `backend`, Runtime **Python 3**.
3. Build Command: `pip install -e .`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Mesmas variáveis, com uma diferença: na Render **não há limite de 4,5 MB**, então
   `MAX_UPLOAD_BYTES` pode voltar aos 20 MB do padrão.
6. O frontend continua na Vercel, agora precisando de `VITE_API_URL` e `CORS_ORIGINS`.

O que muda para pior: o serviço gratuito **dorme após 15 minutos parado** e leva cerca de
um minuto para acordar. Numa apresentação ao vivo, abra a aplicação alguns minutos antes.

**Não use o Postgres gratuito da própria Render** — ele expira 30 dias depois de criado.
Continue com o Neon.
