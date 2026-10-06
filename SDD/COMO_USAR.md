# PRIDE Vision AI — Plataforma

Plataforma simplificada de ASPM (Application Security Posture Management).
Recebe os resultados do **Semgrep** (análise estática de código) e do **Nuclei**
(varredura dinâmica da aplicação), correlaciona os achados, prioriza pelo risco
técnico somado ao contexto do negócio, usa IA para explicar cada problema e
acompanha o ciclo de correção.

Este documento é um passo a passo completo: o que fazer, na ordem, e **por que**
cada coisa foi feita desse jeito.

---

## Índice

1. [O problema que a plataforma resolve](#1-o-problema-que-a-plataforma-resolve)
2. [Requisitos](#2-requisitos)
3. [Instalação](#3-instalação)
4. [Primeira execução](#4-primeira-execução)
5. [Percorrendo a plataforma](#5-percorrendo-a-plataforma)
6. [Como funciona por dentro](#6-como-funciona-por-dentro)
7. [Rodando com IA de verdade](#7-rodando-com-ia-de-verdade)
8. [Decisões de projeto e o porquê](#8-decisões-de-projeto-e-o-porquê)
9. [Rodando os testes](#9-rodando-os-testes)
10. [Conferência com a especificação](#10-conferência-com-a-especificação)
11. [Limitações conhecidas](#11-limitações-conhecidas)
12. [Estrutura do projeto](#12-estrutura-do-projeto)

---

## 1. O problema que a plataforma resolve

Ferramentas de segurança geram muitos alertas, e nem todos importam igualmente.

- O **Semgrep** lê o código e aponta trechos suspeitos. Acha muita coisa que
  talvez nunca seja explorável na prática.
- O **Nuclei** ataca a aplicação rodando e confirma o que responde. Prova o que
  é alcançável, mas não diz onde consertar.

Quando as **duas** apontam o mesmo problema no mesmo lugar, você sabe duas
coisas ao mesmo tempo: a falha existe no código *e* é alcançável de fora.

Mas isso ainda não basta. A mesma falha não vale o mesmo em toda parte: um XSS
num portal público em produção é urgente; o mesmo XSS num sandbox interno de
testes pode esperar. É essa diferença — o **contexto de negócio** — que separa
uma plataforma de ASPM de um simples comparador de arquivos.

O PRIDE responde a uma pergunta: **qual vulnerabilidade precisa ser corrigida
primeiro?**

---

## 2. Requisitos

| Item | Versão | Para quê |
|---|---|---|
| **Python** | 3.11 ou superior | Backend |
| **Node.js** | 20 ou superior | Frontend |
| Chave de API da OpenAI ou do Gemini | — | Opcional; só para as explicações por IA |

O restante da plataforma funciona sem chave nenhuma — apenas as explicações
geradas por IA ficam indisponíveis, com uma mensagem clara na tela.

---

## 3. Instalação

O projeto tem duas partes independentes, cada uma com suas dependências.

### Passo 1 — Backend

```powershell
cd c:\Users\Cliente\personaProject\pride-vision-platform\backend
python -m pip install -e ".[dev]"
```

**Por que `-e`:** instala em modo editável, apontando para a pasta em vez de
copiar os arquivos. Você edita o código e a mudança vale na hora.

**Por que `[dev]`:** traz `pytest`, `ruff` e `mypy`. Sem isso o servidor sobe,
mas você não consegue rodar os testes.

### Passo 2 — Frontend

```powershell
cd c:\Users\Cliente\personaProject\pride-vision-platform\frontend
npm install
```

---

## 4. Primeira execução

São dois processos, cada um num terminal.

### Terminal 1 — API

```powershell
cd c:\Users\Cliente\personaProject\pride-vision-platform\backend
python -m uvicorn app.main:app --reload --port 8000
```

Confira em **http://localhost:8000/docs** — a documentação interativa da API,
gerada automaticamente. Dá para percorrer o sistema inteiro por ali, sem
interface, o que é útil para demonstrar o backend isoladamente.

### Terminal 2 — Interface

```powershell
cd c:\Users\Cliente\personaProject\pride-vision-platform\frontend
npm run dev
```

Abre em **http://localhost:5173**.

**Por que duas portas:** o Vite serve a interface e repassa tudo que começa com
`/api` para o backend na 8000. Assim o código do frontend usa caminhos
relativos, e o mesmo código funciona depois de publicado, quando os dois ficam
atrás do mesmo domínio.

### Passo 3 — Popular a demonstração

Com a API rodando, num terceiro terminal:

```powershell
cd c:\Users\Cliente\personaProject\pride-vision-platform\backend
python popular_demo.py
```

Isso cria o usuário `admin@pride.com` (senha `admin`), cadastra
cinco aplicações em contextos diferentes e envia os **mesmos** relatórios para
todas.

**Por que os mesmos relatórios:** é justamente o ponto da demonstração. O mesmo
achado recebe prioridades diferentes conforme o ambiente, a exposição e a
importância da aplicação. Sem esse contraste, a plataforma pareceria só um
leitor de arquivos.

---

## 5. Percorrendo a plataforma

### Visão geral

Cinco indicadores no topo, dois gráficos e o ranking de aplicações por risco
acumulado.

**Por que o ranking pesa crítico muito acima de médio:** um crítico não é
compensado por vários médios. A pontuação usa pesos distantes (100/20/5/1) para
que uma aplicação com uma falha crítica apareça acima de outra com dez achados
irrelevantes.

### Aplicações

O inventário. Cada cartão traz o contexto de negócio, os contadores, quais
relatórios estão em vigor, e os botões de enviar relatório, editar e remover.

**O botão Editar é a demonstração mais forte da plataforma.** Mude uma aplicação
de produção/internet/alta para teste/interna/baixa e salve: as vulnerabilidades
são reclassificadas na hora e as críticas somem. Volte e elas reaparecem. É a
prova visível de que o contexto de negócio entra na conta.

### Vulnerabilidades

A lista central, ordenada da mais grave para a menos grave. Dentro de cada
nível, as confirmadas pelas duas ferramentas aparecem primeiro.

**Por que os filtros vão para a URL:** uma busca vira link compartilhável e
sobrevive ao recarregar a página.

### Detalhes

Reúne o que cada ferramenta reportou, por que aquele risco foi atribuído, a
explicação da IA e todo o histórico de tratamento — com o botão para mudar o
status.

---

## 6. Como funciona por dentro

```
Cadastro da aplicação
        ↓
Upload do relatório do Semgrep
        ↓
Upload do relatório do Nuclei
        ↓
   normalizer      → unifica tipos e extrai endpoints
        ↓
   correlator      → agrupa por tipo + endpoint compatível
        ↓
   risk_engine     → crítico / alto / médio / baixo (sem IA)
        ↓
   data_masker     → mascara dados sensíveis
        ↓
   ai_explainer    → explica e sugere (não decide)
        ↓
   acompanhamento  → status e histórico
```

### Etapa 1 — Inventário

Cada aplicação registra nome, responsável, URL, e os três fatores de contexto:
**ambiente** (produção, homologação, teste), **exposição** (internet, interna) e
**importância para o negócio** (alta, média, baixa).

**Por que esses três:** são exatamente os fatores que a especificação usa para
diferenciar a prioridade. Sem eles, a plataforma só saberia dizer "as duas
ferramentas acharam isto", que é o que a POC já fazia.

### Etapa 2 — Ingestão

Os arquivos são enviados manualmente; o sistema não executa as ferramentas.

**Por que o relatório anterior é substituído:** uma nova varredura representa o
estado atual. Acumular achados antigos mostraria problemas que já não existem.

**Por que arquivos malformados não derrubam o upload:** um resultado do Semgrep
sem campo obrigatório é descartado com aviso, e uma linha inválida no JSONL do
Nuclei também. O retorno diz quantos entraram e quantos foram ignorados —
relatórios reais vêm com lixo, e perder o arquivo inteiro por causa de uma
entrada ruim seria pior.

### Etapa 3 — Normalização

**Tipos de vulnerabilidade.** `cross-site scripting`, `reflected-xss` e `xss`
viram todos `xss`.

**Por que a comparação ignora separadores:** o Semgrep nomeia regras com pontos
e hífens (`...audit.command-injection`), o Nuclei usa espaços (`Remote Code
Execution`). Sem tratar isso, o mesmo command injection achado pelas duas
ferramentas viraria dois grupos separados — e dois "médio" em vez de um
"crítico".

**URLs.** `https://exemplo.com/busca?q=teste` vira `/busca`. Esquema, domínio,
porta e query são descartados, porque o mesmo endpoint aparece com domínios
diferentes entre ambientes e a query muda a cada requisição.

### Etapa 4 — Correlação

Dois achados são relacionados quando **o tipo é igual** e **o endpoint é igual
ou compatível**.

O problema prático: o Semgrep reporta caminho de arquivo (`src/views/busca.py`),
o Nuclei reporta caminho de URL (`/busca`). Igualdade pura nunca casaria. Por
isso há três regras de compatibilidade:

1. **Formas canônicas iguais** — ignorando caixa, barra final, query,
   contrabarras e extensão de arquivo. `/busca/` ~ `/busca?q=1` ~ `busca`
2. **Prefixo em fronteira de segmento** — `/busca` ~ `/busca/avancada`
3. **Mesmo último segmento, com ao menos 3 caracteres** —
   `src/views/busca.py` ~ `/busca`

**Por que o mínimo de 3 caracteres:** sem ele, segmentos genéricos curtos como
`id` ou `v1` agrupariam endpoints sem relação, inflando os falsos críticos.

**Por que regras assim, e não algo mais esperto:** quando um achado sai como
crítico, dá para apontar exatamente qual regra casou. Correspondência
probabilística seria impossível de explicar numa auditoria.

**Por que a ordem dos uploads não importa:** o agrupamento usa componentes
conexas de um grafo e as regras são simétricas. Enviar o Nuclei antes ou depois
do Semgrep dá o mesmo resultado.

Se um resultado do Semgrep trouxer `extra.metadata.route`, esse valor é usado
direto como endpoint e tem precedência.

### Etapa 5 — Classificação de risco

Quatro níveis, decididos por regras — **nunca pela IA**.

A base é a matriz de confirmação × ambiente × contexto de negócio:

| Confirmação | Ambiente | Exposta ou de alta importância | Resultado |
|---|---|---|---|
| Ambas ferramentas | Produção | Sim | **Crítico** |
| Ambas ferramentas | Produção | Não | **Alto** |
| Ambas ferramentas | Homologação | — | **Alto** |
| Ambas ferramentas | Teste | — | **Médio** |
| Uma ferramenta | Produção | Sim | **Alto** |
| Uma ferramenta | Produção | Não | **Médio** |
| Uma ferramenta | Homologação | — | **Médio** |
| Uma ferramenta | Teste | — | **Baixo** |

**Por que uma matriz completa:** a especificação enumera quatro situações mas
não cobre todas as combinações — não diz, por exemplo, o que fazer quando as
duas ferramentas confirmam algo em homologação. As lacunas foram preenchidas
mantendo a lógica dela: confirmação dupla sempre pesa mais que simples, e
produção sempre pesa mais que homologação, que pesa mais que teste.

Sobre esse resultado incide **um** ajuste pela severidade que a ferramenta
reportou:

- **Desce um nível** quando todas as severidades são informativas ou baixas.
- **Sobe um nível** quando alguma é crítica **e** a aplicação está em produção
  **e** é exposta ou de alta importância.

**Por que a severidade entra:** a especificação lista cinco fatores para a
priorização, e a severidade reportada é o primeiro deles. Sem esse ajuste, um
RCE crítico e um XSS médio terminariam empatados só por compartilharem o
ambiente.

**Por que só um degrau:** o peso principal continua sendo a confirmação cruzada
e o contexto, como a especificação define. A severidade refina, não domina.

Cada resultado carrega uma **justificativa em texto** citando os fatores que
pesaram — inclusive quando a severidade alterou o nível. Sem isso o usuário
veria um risco diferente do que a matriz sugere, sem explicação.

### Etapa 6 — Mascaramento

Antes de qualquer envio à IA, o sistema substitui:

| Dado sensível | Substituído por |
|---|---|
| Endereços IP (IPv4 e IPv6) | `[IP_MASCARADO]` |
| Tokens (Bearer, JWT) | `[TOKEN_MASCARADO]` |
| Chaves de API | `[API_KEY_MASCARADO]` |
| Senhas | `[SENHA_MASCARADA]` |
| E-mails | `[EMAIL_MASCARADO]` |
| Nomes de sistemas internos | `[NOME_MASCARADO]` |

**Por que mascarar:** mensagens de ferramentas de segurança frequentemente
carregam trechos de código com credenciais, IPs internos e e-mails. Mandar isso
para um provedor externo vazaria informação da sua infraestrutura.

**Por que os nomes internos são configuráveis:** IPs e e-mails seguem padrões
reconhecíveis por expressão regular, mas `servidor-prod-01` não tem como ser
adivinhado. A variável `PRIDE_INTERNAL_NAMES` recebe a lista.

### Etapa 7 — Explicação pela IA

A IA recebe os dados **já correlacionados e já classificados** e devolve seis
seções: explicação, impacto, por que foi priorizado assim, sugestão de correção,
como validar, e uma descrição pronta para abrir um ticket.

**Por que a IA entra só no fim:** a especificação exige que a classificação seja
feita por regras fixas, "mais fácil de explicar, testar e auditar". A IA explica
o resultado; não participa da decisão.

**Por que ela não consegue fazer mais nada:** o programa envia uma string e lê
uma string de volta. Não há caminho pelo qual a IA altere código, faça commit,
aprove uma correção ou execute um ataque — as ações que a especificação proíbe.
O módulo de risco sequer importa o módulo de IA, e há teste verificando isso.

**Por que sob demanda, e não durante o upload:** um relatório grande faria
dezenas de chamadas e deixaria o envio lento, e nem toda vulnerabilidade precisa
de explicação — o usuário pede quando vai tratar.

**Por que uma falha da IA não derruba nada:** risco, justificativa e
acompanhamento seguem válidos. Só o bloco da IA fica indisponível.

### Etapa 8 — Acompanhamento

Cinco status: **Nova**, **Em análise**, **Em correção**, **Corrigida** e **Falso
positivo**. Cada mudança grava quem fez, quando e o comentário.

**Por que o histórico importa:** sem ele não dá para responder quando algo foi
corrigido nem por quem. Acompanhar o ciclo de tratamento é um dos quatro pilares
de ASPM da especificação.

**Por que reenviar um relatório não apaga o status:** o acompanhamento é
trabalho do usuário. Uma nova varredura atualiza os dados técnicos e o risco,
mas nunca o status. A vulnerabilidade é reencontrada mesmo que o endpoint mude
de nome — quando só o Semgrep havia reportado, ela ficou registrada como
`src/views/busca.py`; ao chegar o Nuclei, passa a se chamar `/busca`, e são o
mesmo item.

---

## 7. Rodando com IA de verdade

### Passo 1 — Conseguir uma chave

Você precisa de **uma** das duas. O Gemini tem plano gratuito; a API da OpenAI é
paga, mesmo que você já assine o ChatGPT — são cobranças separadas.

#### Gemini (Google) — tem plano gratuito

1. Acesse **https://aistudio.google.com/apikey**
2. Entre com uma conta Google
3. Clique em **Get API key** / **Criar chave de API**
4. Escolha um projeto do Google Cloud, ou deixe criar um novo
5. Copie a chave — começa com `AIza...`

#### OpenAI — paga

1. Acesse **https://platform.openai.com/api-keys**
2. Em **Billing**, adicione crédito (o mínimo costuma ser US$ 5).
   **Sem crédito a chave é criada mas retorna erro de quota.**
3. **Create new secret key** e copie — começa com `sk-...`, e só aparece uma vez

### Passo 2 — Configurar

Crie um arquivo `.env` dentro de `backend/`, usando o `.env.example` como
modelo:

```
SECRET_KEY=gere-uma-chave-forte-aqui
AI_DEFAULT_PROVIDER=gemini
GEMINI_API_KEY=AIza-sua-chave-aqui
```

Gere a `SECRET_KEY` com:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Por que a SECRET_KEY importa:** ela assina os tokens de login. Sem ela o
sistema gera uma aleatória a cada reinício e todo mundo é deslogado; com uma
chave curta, quem a descobrir consegue forjar o token de qualquer usuário. O
sistema avisa nos dois casos ao subir.

O `.env` está no `.gitignore` — chave em código-fonte vaza no primeiro push.

### Passo 3 — Usar

Na tela de detalhes de qualquer vulnerabilidade, clique em **Gerar explicação**.

### Passo 4 — Escolher o modelo (opcional, mas importante saber que existe)

**Nenhum nome de modelo está fixado no código.** Provedores aposentam modelos com
o tempo — este projeto já foi mordido duas vezes, e o sintoma é sempre "modelo
inválido" com uma chave perfeitamente válida. Por isso o modelo é configuração,
em dois níveis:

```
# A lista de candidatos, em ordem. O primeiro que a sua chave aceitar é o usado;
# se ele não existir mais, o próximo é tentado automaticamente.
GEMINI_MODELS=gemini-flash-latest,gemini-2.5-flash,gemini-2.5-flash-lite

# Ou um modelo só. Tem precedência sobre a lista e desliga a troca automática:
# se falhar, o erro aparece em vez de o sistema usar outro sem avisar.
GEMINI_MODEL=gemini-2.5-flash
```

O mesmo vale para a OpenAI, com `OPENAI_MODELS` e `OPENAI_MODEL`. Sem nenhuma das
duas variáveis, valem as listas padrão do projeto.

Para saber qual modelo está ativo agora:

```powershell
curl http://127.0.0.1:8000/api/saude
```

O campo `modelo_ia` responde. É a primeira coisa a olhar quando a IA para de
funcionar sem ninguém ter mexido em nada.

### Se der erro

| Mensagem | O que significa |
|---|---|
| `OPENAI_API_KEY não configurada` (503) | Variável ausente. Confirme que o `.env` está em `backend/` e reinicie o servidor. |
| `insufficient_quota` / `429` | Conta da OpenAI sem crédito. A chave sozinha não basta. |
| `invalid_api_key` / `401` | Chave errada, incompleta ou revogada. |
| `API_KEY_INVALID` no Gemini | Projeto errado, ou API Generative Language não habilitada. |
| `modelo inválido` / `does not exist` / `404` | O modelo foi aposentado. Ajuste `GEMINI_MODELS`/`OPENAI_MODELS` no `.env` — no Gemini, a própria mensagem lista os modelos que a sua chave aceita. |
| Erro 502 na tela | A chamada chegou ao provedor e falhou. A causa aparece no terminal do backend. |

---

## 8. Decisões de projeto e o porquê

### Monólito organizado por módulos

Sem microserviços, sem Kubernetes — como a especificação pede. Um backend só,
dividido em camadas.

### Regras de negócio separadas da persistência

`normalizer`, `correlator`, `data_masker` e `risk_engine` são **funções puras**:
não tocam banco nem rede. Só `ingestion` junta as duas coisas.

**Por quê:** é o que permite auditar a classificação de risco e reproduzi-la em
teste sem subir nada. A especificação exige que o resultado seja "fácil de
explicar, testar e auditar" — e uma regra enterrada numa consulta SQL não é.

### Enums com slug e rótulo

O banco guarda `producao`; a tela mostra `Produção`. A rota `/api/opcoes`
entrega os dois.

**Por quê:** o slug é estável em banco e URL, sem problema de acento. E a
interface não mantém uma tabela de tradução própria, que sairia de sincronia com
o backend na primeira mudança.

### Chaves estrangeiras ligadas explicitamente no SQLite

O SQLite ignora chaves estrangeiras por padrão. Sem `PRAGMA foreign_keys=ON`,
todos os `ondelete="CASCADE"` seriam inertes: apagar uma aplicação deixaria
achados órfãos e o dashboard contaria vulnerabilidades de aplicações que já não
existem. Foi um bug real, encontrado em teste.

### Login com mensagem de erro idêntica

E-mail inexistente e senha errada devolvem exatamente a mesma mensagem.
Distinguir os dois permitiria descobrir quais e-mails estão cadastrados.

### Senha limitada a 72 bytes

É o limite do bcrypt, que trunca silenciosamente acima disso — duas senhas
longas diferentes colidiriam. Em vez de aceitar e truncar, o sistema recusa com
mensagem clara.

### Estado de carregamento só na primeira busca

Numa recarga, a tela continua desenhada. Trocá-la por um indicador de página
inteira desmontaria os componentes filhos e apagaria o estado local deles — o
resultado de um upload recém-feito, um formulário aberto, um aviso. Também foi
um bug real, descoberto ao testar o fluxo no navegador.

### Cores de risco como elemento visual central

O nível de risco tem cor própria e peso; status e origem ficam neutros. A
pergunta que a plataforma responde é "o que corrigir primeiro", e a resposta
precisa ser legível num relance.

---

## 9. Rodando os testes

O projeto é **spec-driven**: a especificação do PDF foi decomposta em critérios
de aceitação numerados dentro de `SDD/`, e cada critério tem ao menos um teste
que o prova. Não é opcional — um AC sem teste reprova o gate.

Um comando roda tudo:

```powershell
.\scripts\verificar.ps1
```

Ele executa, em sequência e sem parar no primeiro erro:

| Etapa | Comando | Esperado |
|---|---|---|
| Suíte do backend | `python -m pytest -q` | 344 casos, cobertura de 97% |
| Lint | `python -m ruff check app/ tests/` | limpo |
| Tipos | `python -m mypy --strict app/` | limpo |
| Testes do frontend | `npm run test` | 41 casos |
| Build | `npm run build` | sem erro de tipo |
| Rastreabilidade | `python scripts/rastreabilidade.py` | 208/208 ACs com teste |

Em ambiente POSIX, `./scripts/verificar.sh` faz o mesmo.

Para rodar uma parte isolada:

```powershell
cd backend
python -m pytest
```

```powershell
cd frontend
npm run test
```

**Por que `mypy --strict`:** o sistema lida com campos que podem faltar nos
relatórios. A checagem estrita força tratar cada `None` explicitamente, em vez
de descobrir o problema em produção.

**Por que testar o frontend:** as quatro telas do §7 do PDF listam campos
obrigatórios. Sem teste, "a tela mostra a severidade original" é promessa; com
teste, é contrato.

---

## 10. Conferência com a especificação

A conferência não é mais uma tabela em prosa: é gerada por máquina a partir dos
critérios e dos testes que os provam.

```powershell
python scripts/rastreabilidade.py --emitir
```

O resultado fica em **`SDD/RASTREABILIDADE.md`**, com uma linha por critério: o
ID, se veio do PDF ou é extensão de projeto, o texto do critério e o arquivo e a
linha de cada teste que o cobre.

| Seção do PDF | Onde está especificada | Critérios |
|---|---|---|
| 1–3 — Ideia, problema e fluxo | `SDD/01-visao-geral.md` | `AC-FLUXO-*` |
| 4.1 — Inventário de aplicações | `SDD/02-inventario.md` | `AC-INV-*` |
| 4.2 — Centralização dos achados | `SDD/03-ingestao.md` | `AC-ING-*` |
| 4.3 / 5 — Priorização e regra de risco | `SDD/05-risco.md` | `AC-RISCO-*` |
| 4.4 — Acompanhamento da correção | `SDD/07-acompanhamento.md` | `AC-STATUS-*` |
| 3 / 12 — Correlação e o que é um match | `SDD/04-correlacao.md` | `AC-COR-*` |
| 6 — Como funcionará a IA | `SDD/06-ia.md` | `AC-IA-*` |
| 7 — Interface e telas | `SDD/08-interface.md` | `AC-UI-*` |
| 8–9 — Tecnologias e arquitetura | `SDD/09-arquitetura.md` | `AC-ARQ-*`, `AC-LOGIN-*` |
| 10 — Escopo do MVP | `SDD/10-mvp.md` | checklist dos onze itens |

Situação atual: **208 critérios, todos com teste.** Os marcados `[extensão]` são
os que preenchem lacunas da especificação, para não se confundirem com o que foi
pedido; os `[proibição]` descrevem o que o sistema **não** pode fazer, como a IA
decidir risco ou a plataforma executar uma varredura.

> **Divergências com o PDF §5: resolvidas.** Os três pontos que estavam abertos
> foram fechados relendo cada bloco do §5 como conjunção de condições, que é
> como ele está escrito. O registro da decisão e o que mudou na prática estão em
> `SDD/05-risco.md`, seção "Divergências com o PDF — resolvidas".

O PDF original está versionado em `SDD/anexos/PRIDE-Vision-AI.pdf`.

---

## 11. Limitações conhecidas

Em ordem de importância:

1. **Não há sistema de migrações de banco.** As tabelas são criadas na
   inicialização, mas uma coluna nova não é acrescentada a uma tabela que já
   existe. Em desenvolvimento basta apagar `backend/pride_vision.db` e rodar
   `popular_demo.py` de novo. Depois de publicado com dados reais, será preciso
   adotar Alembic ou aplicar `ALTER TABLE` manualmente.

2. **A correlação depende de o nome do arquivo lembrar a rota.** Se o Semgrep
   reportar `src/handlers/h1.py` para um código que atende `/busca`, os dois não
   correlacionam. A saída é preencher `extra.metadata.route` no relatório. É
   consequência direta de a especificação exigir regras simples e explicáveis em
   vez de correspondência probabilística.

3. **Login sem papéis nem permissões.** Todo usuário autenticado enxerga todas as
   aplicações. É a leitura literal de "login simples" no escopo do MVP;
   isolamento por empresa seria outro projeto.

4. **O vocabulário de tipos cobre cinco famílias:** XSS, SQL Injection, SSRF,
   RCE/Command Injection e Path Traversal. Outros tipos são preservados com o
   nome original e continuam sendo correlacionados e classificados — apenas não
   são unificados com sinônimos. Para ampliar, edite `MAPA_TIPOS` em
   `backend/app/services/normalizer.py`.

5. **O mascaramento é baseado em expressões regulares.** Cobre as categorias que
   a especificação lista, mas formatos incomuns de token podem escapar. Os dados
   de demonstração são todos fictícios.

6. **Vulnerabilidades que somem do relatório são removidas.** A plataforma
   reflete a varredura mais recente. Se algo foi corrigido e desapareceu do
   scan, o registro — e o histórico dele — sai junto.

---

## 12. Estrutura do projeto

```
pride-vision-platform/
├── COMO_USAR.md                    ← este arquivo
├── ENTENDA_O_PROJETO.md            ← o projeto explicado a quem não o escreveu
├── DEPLOY.md                       ← publicar de graça (Vercel + Neon)
├── AGENTS.md                       ← regras inegociáveis (fonte única)
├── CLAUDE.md                       ← contrato operacional do dia a dia
├── .gitignore
├── SDD/                            ← a especificação, decomposta em critérios
│   ├── 00-INDICE.md                ← para X, leia Y
│   ├── 01-visao-geral.md … 10-mvp.md
│   ├── RASTREABILIDADE.md          ← gerado: AC ↔ teste
│   ├── templates/SPEC_TEMPLATE.md
│   └── anexos/                     ← o PDF original e o texto extraído
├── scripts/
│   ├── verificar.ps1 / .sh         ← o gate: roda tudo e resume
│   ├── rastreabilidade.py          ← reprova AC sem teste
│   └── hook_pos_edicao.py          ← verificação a cada arquivo salvo
├── .claude/
│   ├── agents/                     ← Harvey, Robert, Jessica, Katrina, Louis, Mike
│   ├── commands/                   ← /nova-spec, /testes-ac, /verificar, …
│   ├── settings.json               ← hook PostToolUse
│   └── launch.json                 ← backend e frontend para o preview
├── backend/
│   ├── .env.example                ← modelo de configuração
│   ├── pyproject.toml
│   ├── popular_demo.py             ← cria o cenário de demonstração
│   ├── app/
│   │   ├── main.py                 ← FastAPI, CORS, rotas de infraestrutura
│   │   ├── config.py               ← configuração lida do ambiente
│   │   ├── database.py             ← engine e sessão SQLAlchemy
│   │   ├── auth/                   ← hash de senha, JWT, dependência de sessão
│   │   ├── models/                 ← tabelas e vocabulário do domínio
│   │   ├── schemas/                ← contratos de entrada e saída da API
│   │   ├── routers/                ← camada HTTP
│   │   └── services/
│   │       ├── dominio.py          ← tipos puros, sem banco
│   │       ├── normalizer.py       ← leitura e normalização
│   │       ├── correlator.py       ← correlação
│   │       ├── risk_engine.py      ← classificação de risco
│   │       ├── data_masker.py      ← mascaramento
│   │       ├── ai_explainer.py     ← prompt e interpretação
│   │       ├── ai_service.py       ← IA ligada ao banco
│   │       └── ingestion.py        ← orquestra tudo com persistência
│   └── tests/                      ← 344 casos, cada um citando o AC que prova
│       ├── CLAUDE.md               ← convenções de teste do backend
│       ├── conftest.py             ← banco em memória por teste
│       ├── dados.py                ← relatórios de exemplo
│       └── analise_estatica.py     ← prova as proibições lendo os imports
└── frontend/
    ├── CLAUDE.md                   ← padrão do React e dos testes de tela
    ├── vite.config.ts              ← Tailwind, proxy para a API e Vitest
    └── src/
        ├── api/                    ← cliente HTTP e tipos
        ├── auth/                   ← contexto de sessão
        ├── components/             ← layout, etiquetas, estados de tela
        ├── hooks/                  ← busca de dados
        ├── testes/                 ← fixtures e helpers dos testes de tela
        ├── setupTests.ts
        └── pages/                  ← Login, Dashboard, Aplicações,
                                       Vulnerabilidades, Detalhes
                                       (+ __tests__/ com 41 casos)
```

### As rotas da API

| Método | Rota | Para quê |
|---|---|---|
| POST | `/api/auth/registrar` | Cadastro |
| POST | `/api/auth/login` | Autenticação |
| GET | `/api/auth/eu` | Validar a sessão |
| GET/POST | `/api/aplicacoes` | Listar e cadastrar |
| GET/PATCH/DELETE | `/api/aplicacoes/{id}` | Obter, editar e remover |
| GET | `/api/aplicacoes/{id}/resumo` | Contagens da aplicação |
| GET | `/api/aplicacoes/{id}/uploads` | Relatórios em vigor |
| POST | `/api/aplicacoes/{id}/uploads/semgrep` | Enviar relatório do Semgrep |
| POST | `/api/aplicacoes/{id}/uploads/nuclei` | Enviar relatório do Nuclei |
| GET | `/api/vulnerabilidades` | Listar, com filtros |
| GET | `/api/vulnerabilidades/{id}` | Detalhes |
| PATCH | `/api/vulnerabilidades/{id}/status` | Mudar o status |
| POST | `/api/vulnerabilidades/{id}/analise` | Gerar a explicação da IA |
| GET | `/api/dashboard` | Números da tela inicial |
| GET | `/api/saude` | Verificação de saúde |
| GET | `/api/opcoes` | Vocabulário controlado |
