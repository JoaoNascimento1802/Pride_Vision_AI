# PRIDE Vision AI — contrato operacional

> **Steering portável — fonte única das regras inegociáveis: `AGENTS.md`.**
> Este `CLAUDE.md` **não redefine** aquelas regras: é o *como* executá-las no dia a dia.
> Em qualquer divergência, **prevalece o `AGENTS.md`**. Nova sessão? Comece por
> `AGENTS.md` e rode `/briefing`.

## Comunicação

- Tratar o usuário como especialista sênior. Sem explicação óbvia, sem tutorial básico.
- Ir direto ao ponto. Precisa de algo, pergunte objetivamente.
- Não alucinar. Não sabe, diga que não sabe.
- Português em tudo: código, comentário, docstring, commit, AC e conversa.

---

## O ciclo: planejar → SDD → TDD

```
Pedido do usuário
      ↓
1. PLANEJAR   Harvey entrevista. Perguntas objetivas, uma rodada por vez.
      ↓       O que entrega? O que NÃO pode acontecer? Casos de borda?
      ↓
2. SDD        AC numerado gravado em SDD/<módulo>.md, formato Dado/Quando/Então.
      ↓       Apresentar ao usuário e AGUARDAR aprovação explícita.
      ↓
3. TDD        Robert escreve o teste citando o AC. Roda. Confirma VERMELHO.
      ↓       Louis (backend) ou Mike (frontend) implementa até VERDE.
      ↓
4. GATE       scripts/verificar.ps1 — suíte, lint, tipos, frontend, rastreabilidade.
      ↓
5. VALIDAR    Subir a plataforma e percorrer o fluxo. Dizer o que se viu.
```

Nenhum passo é pulável. Fix pequeno usa formato reduzido — **um** AC — nunca ausência
de AC.

---

## Passo 1 — Antes de tocar em qualquer coisa

```bash
cd backend && python -m pytest -q
```

Guarde o número. É o baseline. Se já estiver vermelho, **pare e reporte** — não empilhe
mudança sobre suíte quebrada.

## Passo 2 — Ler a SDD do módulo que vai mexer

`SDD/00-INDICE.md` diz qual arquivo cobre o quê. Ler o AC antes de ler o código evita
implementar o que ninguém pediu.

## Passo 3 — Escopo limitado

**Um arquivo por vez. Sem exceções.** Depois de cada arquivo Python alterado:

```bash
cd backend && python -m py_compile app/caminho/arquivo.py
```

## Passo 4 — Rodar a suíte depois de cada arquivo

```bash
cd backend && python -m pytest -q
```

Teste que passava e começou a falhar: **reverter imediatamente e reportar.** Não tentar
consertar o teste para o código passar.

## Passo 5 — Gate completo antes de dar por concluído

```powershell
.\scripts\verificar.ps1
```

Roda, em sequência e sem abortar no primeiro erro: `pytest` → `ruff` → `mypy --strict` →
`vitest` → `vite build` → `rastreabilidade`. Só existe "concluído" com os seis verdes.

## Passo 6 — Reportar

- O que mudou (arquivo + linha)
- Qual AC isso atende
- Quais testes rodaram e o resultado, com números
- O que foi validado na aplicação rodando

---

## Matriz: alterei X → rode Y

| Alterei | Rode |
|---|---|
| `backend/app/services/*.py` | `pytest`, `ruff check app/ tests/`, `mypy --strict app/` |
| `backend/app/routers/*.py` | idem + validação real do endpoint com a aplicação de pé |
| `backend/app/models/*.py` | idem + apagar `backend/pride_vision.db` e rodar `popular_demo.py` (não há migrações) |
| `frontend/src/**` | `npm run test`, `npm run lint`, `npm run build` |
| `SDD/**` | `python scripts/rastreabilidade.py` |
| Qualquer coisa | `.\scripts\verificar.ps1` antes de encerrar |

> **Não há sistema de migrações.** `criar_tabelas()` cria o que não existe, mas não
> acrescenta coluna a tabela existente. Mudou model? Apague `backend/pride_vision.db` e
> repovoe. Em produção com dado real isso exigiria Alembic — está registrado como
> restrição consciente em `SDD/09-arquitetura.md`.

---

## As quatro regras de produto que não se negociam

Detalhamento operacional das regras 3 a 6 do `AGENTS.md`. Não criam regra paralela.

**Risco é do sistema, não da IA.** `risk_engine.classificar()` é função pura: mesma
entrada, mesma saída, sem rede e sem banco. Precisa de um fator novo na classificação?
Vira AC em `SDD/05-risco.md` e entra como parâmetro de `ContextoAplicacao` — nunca como
chamada a modelo.

**Masking antes do envio.** Todo texto que sai em direção a OpenAI ou Gemini passa por
`mascarar()`. Adicionou campo novo no prompt? O campo passa pelo masking também. O teste
que prova isso vive em `backend/tests/test_ai.py`.

**A IA devolve texto, não ação.** `ai_explainer` retorna explicação, impacto, remediação,
justificativa da priorização e descrição de ticket. Nada disso escreve no banco por conta
própria.

**Sem varredura.** Nenhum código do produto faz requisição para a URL da aplicação
cadastrada. A URL é dado de inventário e contexto — não alvo.

---

## Segurança do dia a dia

| Item | Regra |
|---|---|
| `SECRET_KEY` | Vem do ambiente. Chave fraca ou ausente gera aviso no boot — não ignore |
| Chave de IA | Só do ambiente (`.env`, nunca versionado). `.env.example` é o modelo |
| Upload | Limite de tamanho e UTF-8 validados em `routers/uploads.py`. Não afrouxar |
| Autenticação | Toda rota de dado exige `usuario_atual`. Rota nova sem isso é bug |
| Senha | `bcrypt` em `auth/security.py`. Nunca comparar hash na mão |
| Log | Nada de token, senha ou payload bruto de upload em log |

---

## Onde encontrar o resto

Índice completo: **`AGENTS.md`**. Especificação decomposta: `SDD/00-INDICE.md`.
Como instalar e percorrer a plataforma: `COMO_USAR.md`.
