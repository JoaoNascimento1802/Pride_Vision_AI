# PRIDE Vision AI — como o projeto foi feito

> Este documento é para **quem não escreveu o código**: colegas de grupo, professor,
> qualquer pessoa que precise entender o que a plataforma faz e por que ela foi feita
> assim. Não tem pré-requisito.
>
> Para *instalar e rodar*, veja `COMO_USAR.md`. Para *publicar*, veja `DEPLOY.md`.
> Para as regras que o time seguiu, `AGENTS.md`.

---

## 1. O problema, em uma cena

Uma empresa roda duas ferramentas de segurança nas suas aplicações:

- O **Semgrep** lê o código-fonte e aponta trechos suspeitos. É rápido e barato, mas
  não sabe se aquele trecho está realmente exposto — ele só viu o texto do programa.
- O **Nuclei** ataca a aplicação de fora, como um invasor faria, e diz o que respondeu.
  É a prova de que a falha existe de verdade, mas não sabe em que linha do código está.

No fim do dia, a equipe recebe **duzentos alertas** e nenhuma ordem. Todos parecem
urgentes. E os dois relatórios usam nomes diferentes para a mesma coisa: o Semgrep chama
de `reflected-xss` em `src/views/busca.py`, o Nuclei chama de `Cross Site Scripting` em
`https://portal.exemplo.com/busca?q=…`. São o mesmo problema, e ninguém percebe.

A pergunta que ninguém consegue responder é simples:

> **Qual dessas eu conserto primeiro?**

O PRIDE Vision AI existe para responder isso. **Ele não é mais um scanner.** Não roda o
Semgrep, não roda o Nuclei, não encosta na aplicação da empresa. Ele recebe os relatórios
prontos, junta o que é a mesma coisa, ordena por risco real e acompanha a correção.

Isso tem nome no mercado: **ASPM**, *Application Security Posture Management*. É a
categoria de ferramenta que organiza a segurança das aplicações em vez de procurar falhas.

---

## 2. Por que "risco real" não é a severidade da ferramenta

Aqui está a ideia central do produto, e vale ler devagar.

O Semgrep marca um XSS como `ERROR`. Mas esse mesmo XSS pode estar:

- no **Portal do Cliente**, em produção, aberto na internet, importante para o negócio;
- ou no **Sandbox de Testes**, que só existe na rede interna e ninguém usa.

É o mesmo XSS. **O risco não é o mesmo.** A ferramenta não sabe disso, porque ela nunca
ouviu falar do seu negócio. O PRIDE sabe, porque o usuário cadastrou o contexto.

E tem mais: se o **Nuclei confirmou** que a falha responde de verdade em produção, isso
vale muito mais do que uma suspeita que só o Semgrep levantou. Confirmação por duas
ferramentas independentes é evidência; uma só é hipótese.

O PRIDE combina cinco coisas para decidir:

| Fator | De onde vem | Por que importa |
|---|---|---|
| Confirmação cruzada | As duas ferramentas apontaram o mesmo problema? | Evidência vale mais que suspeita |
| Ambiente | Cadastro da aplicação | Produção não é homologação |
| Exposição | Cadastro da aplicação | Na internet qualquer um alcança |
| Importância para o negócio | Cadastro da aplicação | Nem toda aplicação vale o mesmo |
| Severidade original | O relatório da ferramenta | Ajusta um degrau, nunca decide sozinha |

O resultado é um de quatro níveis — **Crítico, Alto, Médio, Baixo** — e, junto,
**uma frase explicando por quê**. A lista de vulnerabilidades sai ordenada por esse nível.
A resposta para "qual eu conserto primeiro?" é: a primeira da lista.

---

## 3. O caminho de um dado, do arquivo até a tela

```
   VOCÊ                        A PLATAFORMA                       O RESULTADO
   ────                        ────────────                       ───────────

 cadastra a           ┌──────────────────────────┐
 aplicação   ────────▶│ 1. INVENTÁRIO            │
 (ambiente,           │    guarda o contexto     │
  exposição,          └──────────────────────────┘
  importância)                     │
                                   ▼
 envia               ┌──────────────────────────┐
 semgrep.json ──────▶│ 2. INGESTÃO              │
 e nuclei.jsonl      │    lê e valida os        │
                     │    arquivos              │
                     └──────────────────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │ 3. NORMALIZAÇÃO          │   "reflected-xss"  ─┐
                     │    traduz os dois        │   "Cross Site       ├─▶  xss
                     │    dialetos para um só   │    Scripting"      ─┘
                     └──────────────────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │ 4. CORRELAÇÃO            │   src/views/busca.py ─┐
                     │    junta o que é a       │                       ├─▶ mesmo item
                     │    mesma coisa           │   /busca             ─┘
                     └──────────────────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │ 5. RISCO                 │   5 fatores  ─▶  Crítico
                     │    regra fixa, sem IA    │                  + justificativa
                     └──────────────────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │ 6. MASCARAMENTO          │   192.168.0.10
                     │    tira o que é sensível │        ▼
                     │    ANTES de sair daqui   │   [IP_MASCARADO]
                     └──────────────────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
 clica em            │ 7. IA                    │   explica, sugere,
 "gerar     ────────▶│    explica em português  │   escreve o ticket
  explicação"        │    (só texto, nunca ação)│
                     └──────────────────────────┘
                                   │
                                   ▼
 muda o              ┌──────────────────────────┐
 status     ────────▶│ 8. ACOMPANHAMENTO        │   Nova → Em correção
                     │    registra quem e quando│   → Corrigida
                     └──────────────────────────┘
```

---

## 4. As oito etapas, uma pergunta cada

### 1. Inventário — *o que a plataforma precisa saber sobre a aplicação?*

Seis campos: nome, responsável, ambiente (produção / homologação / teste), URL, exposição
(internet / interna) e importância para o negócio (alta / média / baixa).

A URL é **só identificação**. A plataforma nunca faz requisição para ela — isso a
transformaria num scanner, e a especificação proíbe.

### 2. Ingestão — *o que acontece quando um arquivo chega?*

Cada linha é lida e validada. Entrada quebrada **não derruba o resto**: ela é ignorada e
vira um aviso na resposta ("3 entradas do arquivo foram ignoradas"). Enviar um relatório
novo **substitui** o anterior daquela ferramenta, em vez de somar — a plataforma reflete
a varredura mais recente, não o histórico dela.

### 3. Normalização — *como comparar duas ferramentas que falam idiomas diferentes?*

Traduzindo as duas para um vocabulário só. `reflected-xss`, `dom-xss` e
`Cross Site Scripting` viram todas `xss`. A URL `https://host:8443/busca?q=teste#topo`
vira o caminho `/busca`. O arquivo `src/views/busca.py` também vira `/busca`.

É essa tradução que torna a próxima etapa possível.

### 4. Correlação — *como saber que dois achados são o mesmo problema?*

Duas condições: **mesmo tipo** e **endereços compatíveis**. Compatível significa uma de
três coisas — são idênticos, um é começo do outro numa fronteira de barra, ou terminam no
mesmo pedaço (com pelo menos 3 letras, para `/api` não casar com `/a`).

Nada de porcentagem de semelhança, nada de "provavelmente é o mesmo". A especificação
pediu regra **simples e explicável**, e é isso que está lá: dá para conferir no papel.

### 5. Risco — *quem decide, e como se audita essa decisão?*

Uma função matemática pura: mesma entrada, mesma saída, sempre. Não consulta banco, não
consulta rede, **não consulta IA**. Recebe o grupo correlacionado e o contexto da
aplicação, devolve o nível e a frase que o explica.

A matriz completa, sem letra miúda:

| Confirmação | Ambiente | Contexto | Risco |
|---|---|---|---|
| Semgrep **e** Nuclei, com evidência | Produção | Internet ou importância alta | **Crítico** |
| Semgrep **e** Nuclei, sem evidência | Produção | Internet ou importância alta | **Alto** |
| Semgrep **e** Nuclei | Produção | Interna e não-alta | **Alto** |
| Semgrep **e** Nuclei | Homologação | — | **Alto** |
| Semgrep **e** Nuclei | Teste | — | **Médio** |
| Só uma ferramenta | Produção | qualquer | **Alto** |
| Só uma ferramenta | Homologação | — | **Médio** |
| Só uma ferramenta | Teste | — | **Baixo** |

Depois disso, a severidade original ajusta **um único degrau**: tudo informativo desce um,
severidade crítica em produção sensível sobe um. E existe uma trava: essa subida **não
chega a Crítico sem evidência do Nuclei** — uma regra que se contorna por caminho lateral
não é uma regra.

Mudar o contexto da aplicação **reclassifica tudo na hora**. Trocar o Portal do Cliente de
Produção para Teste derruba os Críticos e reescreve as justificativas. É a demonstração
mais convincente do produto: o mesmo achado, risco diferente, motivo explicado.

### 6. Mascaramento — *o que sai daqui em direção a um serviço externo?*

Nada de sensível. Antes de qualquer texto ir para a OpenAI ou o Google, ele passa por uma
função que substitui:

```
192.168.0.10                    →  [IP_MASCARADO]
Bearer eyJhbGci…                →  [TOKEN_MASCARADO]
password=hunter2                →  [SENHA_MASCARADA]
api_key=sk-abc123…              →  [API_KEY_MASCARADO]
ana@empresa.com.br              →  [EMAIL_MASCARADO]
servidor-prod-01 (configurável) →  [NOME_MASCARADO]
```

Isto não é uma boa prática opcional do time: é o §6 da especificação, e existe um teste
que lê o texto entregue ao provedor e falha se encontrar qualquer um desses.

### 7. IA — *o que ela pode e o que ela não pode?*

**Pode**, e devolve seis blocos de texto: explicação, impacto, por que foi priorizado
assim, sugestão de correção, como validar a correção e uma descrição pronta para abrir um
ticket.

**Não pode** — e isto é estrutural, não uma promessa:

- não decide risco (o prompt informa a classificação **já decidida** e manda não questionar);
- não altera código, não faz commit, não abre pull request;
- não muda status de nada;
- não executa ataque.

A garantia não é a boa vontade do modelo. É que **o código da IA não tem como fazer nada
disso**: ele não importa o motor de risco, não importa nada que execute comando, e o
resultado dele só é gravado em seis campos de texto. Existem testes que leem os `import`
do módulo e falham se algum caminho aparecer.

### 8. Acompanhamento — *e depois que a vulnerabilidade aparece?*

Cinco status: **Nova → Em análise → Em correção → Corrigida**, mais **Falso positivo**.
Cada mudança grava quem fez, quando e um comentário opcional. E reenviar o relatório
**não apaga esse trabalho**: uma vulnerabilidade marcada "Em correção" continua "Em
correção" depois do próximo upload.

Isso é o que separa um comparador de arquivos de uma plataforma de ASPM de verdade.

---

## 5. Quem conversa com quem

```
  NAVEGADOR
     │
     │  React 19 + TypeScript + Tailwind
     │  5 telas: Login, Visão geral, Aplicações, Vulnerabilidades, Detalhe
     │
     │  Nenhuma tela chama a rede diretamente. Todas passam por
     │  api/client.ts — uma porta só, onde vive o tratamento de
     │  token e de sessão expirada.
     ▼
  ┌──────────────────────────────────────────────────────────┐
  │  API REST — FastAPI                                      │
  │  19 rotas. 17 exigem estar logado; 2 são públicas         │
  │  (a de saúde e a que lista as opções dos formulários).   │
  └──────────────────────────────────────────────────────────┘
     │
     │  As rotas não têm regra de negócio. Elas recebem,
     │  chamam um serviço e devolvem.
     ▼
  ┌──────────────────────────────────────────────────────────┐
  │  SERVIÇOS PUROS — não conhecem banco nem rede            │
  │                                                          │
  │   normalizer   traduz os dois dialetos                   │
  │   correlator   junta o que é a mesma coisa               │
  │   risk_engine  decide o nível e escreve a justificativa  │
  │   data_masker  esconde o que é sensível                  │
  │   ai_explainer monta o prompt e lê a resposta            │
  └──────────────────────────────────────────────────────────┘
     │
     │  Um único serviço faz a ponte com o banco: ingestion.
     ▼
  ┌──────────────────────────────────────────────────────────┐
  │  SQLAlchemy → SQLite                                     │
  │  5 tabelas: usuarios, aplicacoes, uploads, achados,      │
  │             vulnerabilidades (+ historico_status)        │
  └──────────────────────────────────────────────────────────┘
```

**Por que os serviços de regra não conhecem o banco.** Porque assim eles são testáveis
sem ligar nada. Testar "XSS confirmado em produção exposta dá Crítico" não precisa de
banco, de servidor, nem de arquivo: é chamar uma função com dois argumentos e conferir o
retorno. São **49 testes** só na matriz de risco, e rodam em menos de um segundo.

O outro motivo é auditoria. A regra "a IA não decide risco" só é verificável porque o
motor de risco é um arquivo que não importa nada de IA. Se ele conversasse com banco e
rede, ninguém conseguiria provar coisa alguma sobre ele.

---

## 6. As quatro decisões que definem o produto

Não são detalhes técnicos. São o que o produto **é**.

### O risco é decidido por regra, não por IA

Poderia ser mais fácil mandar tudo para um modelo e perguntar "isso é grave?". Seria pior:
a resposta mudaria de uma execução para outra, ninguém saberia explicar o porquê a um
auditor, e não daria para testar.

A regra fixa é o oposto: dá para escrever num papel, conferir à mão, e ela responde a
mesma coisa hoje e no ano que vem.

### O mascaramento acontece antes do envio, não depois

A ordem no código é literal: serializa → **mascara** → monta o prompt → envia. Não existe
caminho em que o texto original chegue ao provedor, porque não existe outro lugar de onde
o prompt possa sair.

### A IA devolve texto, nunca ação

Ela é uma assistente que explica, não um agente que age. Toda a saída dela vira texto
numa tela. Um modelo que pudesse alterar código ou mudar classificação seria um risco de
segurança dentro de uma ferramenta de segurança.

### A plataforma não varre nada

Ela recebe arquivos. Não instala o Semgrep, não dispara o Nuclei, e não manda uma única
requisição para a URL cadastrada da aplicação. Existe um teste que percorre os `import` do
código e falha se aparecer qualquer biblioteca de rede onde não deve.

---

## 7. Como o time garantiu que funciona

O projeto não foi escrito e testado depois. Foi o contrário, e em ordem fixa:

```
1. ESPECIFICAR   O pedido vira critério numerado, escrito em
                 "Dado / Quando / Então", gravado em SDD/.
                 Exemplo real:
                 AC-RISCO-01 — Dado Semgrep e Nuclei confirmando com
                 evidência, quando a aplicação está em produção exposta
                 à internet, então o risco é Crítico.
                        ↓
2. APROVAR       O usuário lê e aprova. Sem aprovação, nada avança.
                        ↓
3. TESTAR        O teste é escrito ANTES do código, citando o número do
                 critério. Ele nasce vermelho — tem que falhar, senão
                 não está testando nada.
                        ↓
4. IMPLEMENTAR   Escreve-se o código até o teste ficar verde.
                        ↓
5. CONFERIR      Um script roda tudo e só existe "pronto" com seis verdes.
```

O passo 5 é uma máquina, não uma opinião. `scripts/verificar.ps1` roda, em sequência:

| # | Etapa | O que reprova |
|---|---|---|
| 1 | `pytest` | qualquer teste falhando |
| 2 | `ruff` | código fora do padrão |
| 3 | `mypy --strict` | tipo errado em qualquer lugar |
| 4 | `vitest` | qualquer teste de tela falhando |
| 5 | `vite build` | erro de tipo no frontend |
| 6 | `rastreabilidade` | **critério sem teste, ou teste citando critério que não existe** |

A etapa 6 é a mais incomum e a mais valiosa. Ela lê todos os critérios da `SDD/`, lê todos
os testes, e cruza os dois. Um critério que ninguém testou **reprova a entrega**. Não dá
para dizer "está pronto" com um pedaço da especificação sem prova.

### Os números, hoje

| | |
|---|---|
| Critérios de aceitação | **212**, todos com pelo menos um teste |
| — vindos direto do PDF | 163 |
| — extensões (decisões do time, marcadas) | 49 |
| — proibições (o que o sistema **não** pode fazer) | 15 |
| Testes de backend | **354**, cobrindo 97% do código |
| Testes de tela | **41** |
| Rotas da API | 19 |
| Linhas de Python | ~7.700 |

---

## 8. O que ficou de fora, de propósito

A especificação diz que o MVP precisa ter "**somente**" onze itens. A palavra é parte do
requisito, então o time registrou cada ideia recusada com o motivo — para a resposta ser
"não, e por quê" em vez de silêncio:

| Ideia | Por que não |
|---|---|
| Rodar o Semgrep e o Nuclei pela plataforma | A especificação é explícita: os arquivos chegam à mão |
| Outros scanners (Trivy, ZAP, Dependabot) | O MVP nomeia duas ferramentas |
| Perfis e permissões por usuário | "Login simples" é o que está escrito |
| Abrir ticket no Jira ou no GitHub | O pedido é a **descrição** do ticket, não a abertura |
| Notificação por e-mail | Não consta no escopo |
| Gráficos de tendência ao longo do tempo | A plataforma reflete a varredura atual, não a série histórica |

### Limitações assumidas

Estas são escolhas conscientes, não esquecimentos:

1. **Não há sistema de migração de banco.** As tabelas são criadas na primeira execução,
   mas mudar uma coluna depois exige apagar o banco e repovoar. Em produção com dado real
   isso pediria a ferramenta Alembic.
2. **A correlação depende de o nome do arquivo lembrar a rota.** Se o Semgrep reportar
   `src/handlers/h1.py` para um código que atende `/busca`, os dois não se juntam. É
   consequência direta de a regra ser simples e explicável em vez de probabilística — e
   existe uma saída: declarar a rota no próprio relatório.
3. **Todo usuário logado vê todas as aplicações.** Separar por empresa seria outro projeto.
4. **O mascaramento usa expressões regulares.** Cobre as categorias que a especificação
   lista, mas um formato incomum de token pode escapar.
5. **Vulnerabilidade que some do relatório é removida.** A plataforma mostra a varredura
   mais recente; se algo foi corrigido e sumiu do scan, o registro sai junto.

---

## 9. A auditoria de setembro de 2026

O projeto foi conferido inteiro contra o PDF original, campo por campo. **Nenhum requisito
da especificação ficou de fora.** Tudo o que o documento pede — o inventário com os seis
campos, a centralização dos achados, os cinco fatores de risco, os quatro níveis, as cinco
categorias de mascaramento, as quatro telas, os cinco status e os onze itens do MVP — está
implementado e tem teste.

O que a auditoria encontrou não foi requisito faltando: foram **defeitos que se
escondiam**. Todos com o mesmo padrão — falhavam de um jeito que apontava para o lugar
errado, ou não falhavam onde alguém estivesse olhando.

| O que se achou | Como se escondia | O que se fez |
|---|---|---|
| **A conexão com o Gemini estava morta.** O pacote da Google saiu de suporte em novembro de 2025 e deixou de carregar na versão de Python do projeto | Nenhum teste exercitava o caminho do Gemini de verdade — só o do outro provedor tinha substituto. A bateria de testes ficava verde com a funcionalidade quebrada | Migrado para o pacote atual, e criados os testes que faltavam |
| **Uma biblioteca obrigatória nunca foi declarada.** A validação de e-mail exige um pacote extra no momento em que o programa carrega; sem ele, nada sobe | Funcionava nos computadores do time porque outro projeto instalava esse pacote por acidente. Numa instalação limpa — que é o que todo servidor faz — a aplicação inteira parava de subir | Declarado, e criado um teste que reprova se voltar a faltar |
| **Um comando do SQLite era enviado ao banco de produção.** Como não é a mesma linguagem, o banco recusava e cancelava tudo o que viesse depois | O erro estava dentro de um trecho que engolia falhas em silêncio. E os testes rodam em SQLite, onde o comando é válido | O comando passou a ser exclusivo do SQLite, e o silêncio foi removido |
| **A conexão com o banco era montada no instante em que o programa carregava.** Qualquer problema nela virava falha de carregamento | A aplicação morria antes de conseguir escrever uma linha de log. O servidor devolvia erro genérico em toda página, sem pista nenhuma | Passou a ser montada só quando alguém realmente usa o banco — assim a aplicação sempre sobe e consegue relatar o problema |
| **A tela de diagnóstico morria junto com o banco.** A única página cuja função é dizer o que está errado era a primeira a parar de responder | — | Agora ela responde mesmo com o banco fora, dizendo o motivo (com dados sensíveis ocultos, porque a página é pública) |
| Nove documentos da especificação com o status desmarcado, apesar de tudo pronto | — | Marcados, menos "validação real", que segue desmarcado por honestidade |
| Uma constante sobrando no motor de risco | — | Removida |

Cada um virou critério numerado com teste, para não voltar.

Também foi investigado e **descartado** um alarme falso: uma linha do código de
reclassificação parecia poder pular vulnerabilidades em silêncio, mas o cenário não é
alcançável, porque outra parte do sistema garante que a condição nunca ocorre.

> **A lição que vale para o grupo.** Os quatro defeitos sobreviveram a uma bateria de
> testes verde porque todos moravam no mesmo ponto cego: os testes rodam **na máquina do
> desenvolvedor, com um banco de mentira**. Nada disso é defeito de quem escreveu — é o
> limite natural de testar em ambiente de desenvolvimento. Foram encontrados de dois
> jeitos, e vale anotar os dois: **publicar de verdade**, e **reproduzir o ambiente do
> servidor numa instalação limpa**.

---

## 10. Onde está cada coisa

```
pride-vision-platform/
├── ENTENDA_O_PROJETO.md   ← este arquivo
├── COMO_USAR.md           ← instalar, rodar e percorrer a plataforma
├── DEPLOY.md              ← publicar de graça
├── AGENTS.md              ← as regras que o time seguiu
├── SDD/                   ← a especificação virada em 212 critérios numerados
│   ├── anexos/            ← o PDF original, intocado
│   └── RASTREABILIDADE.md ← gerado por máquina: critério ↔ teste
├── scripts/verificar.ps1  ← o script que diz se está pronto
├── backend/               ← Python, FastAPI, SQLAlchemy
└── frontend/              ← React, Vite, TypeScript, Tailwind
```

Se você só vai olhar **um** arquivo além deste, olhe `SDD/RASTREABILIDADE.md`: é a tabela
que liga cada linha da especificação ao teste que prova que ela foi cumprida.
