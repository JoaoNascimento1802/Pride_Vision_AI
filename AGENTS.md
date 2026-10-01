# AGENTS.md — PRIDE Vision AI (steering portável)

> Ponto de entrada **único e portável** para qualquer dev humano ou ferramenta de IA
> (Claude Code, Cursor, OpenCode…). Enxuto de propósito: aqui ficam as **regras
> inegociáveis** + um **índice navegável**. O detalhe vive nos docs apontados — leia o doc
> certo conforme a tarefa, não um manual gigante.
>
> PRIDE Vision AI = plataforma simplificada de ASPM. Recebe relatórios do Semgrep e do
> Nuclei, correlaciona os achados, prioriza por risco técnico somado ao contexto do
> negócio, usa IA para explicar e acompanha o ciclo de correção. Backend FastAPI +
> SQLAlchemy + SQLite; frontend React/Vite/TypeScript/Tailwind. Monólito por módulos.
>
> **A especificação é o contrato.** O PDF original está em `SDD/anexos/`. Ele foi
> decomposto em critérios de aceitação numerados dentro de `SDD/`. Nada entra no produto
> sem estar lá.

---

## Regras inegociáveis (valem para humano e IA)

1. **SDD antes de código — para QUALQUER mudança de comportamento, por menor que seja.**
   Harvey entrevista → AC numerado gravado em `SDD/` → **aprovado pelo usuário** → Robert
   escreve o teste do AC (nasce vermelho) → implementação até verde → validação real.
   Sem AC aprovado, não há teste; sem teste vermelho, não há código.
   *Exceções únicas:* documentação pura e conserto de teste quebrado sem mudança de
   comportamento do produto.

2. **Todo AC tem ≥1 teste; todo teste cita um AC.** O juiz é a máquina:
   ```bash
   python scripts/rastreabilidade.py
   ```
   AC órfão **bloqueia** a entrega. Teste citando AC inexistente também. Teste sem AC é
   sinal de spec incompleta — volte para a `SDD/`, não apague o teste.

3. **A IA nunca decide risco.** A especificação §5 é explícita: a classificação é feita
   pelo sistema com regras fixas, para ser explicável, testável e auditável.
   `app/services/risk_engine.py` **não importa nada** de `ai_explainer`/`ai_service`, e
   nenhum campo de risco é escrito a partir de resposta de modelo. Quebrar isto
   descaracteriza o produto.

4. **Nada vai para a IA sem passar por `mascarar()`.** Especificação §6: IPs, tokens,
   senhas, chaves de API, e-mails e nomes internos são substituídos por marcadores
   **antes** do envio. Qualquer caminho novo até um provedor de IA passa por
   `app/services/data_masker.py`. Não existe "só desta vez".

5. **A IA não age, só opina.** Não altera código, não commita, não aprova correção, não
   muda classificação, não executa ataque. Toda saída de modelo é texto exibido ao
   usuário — nunca um efeito colateral no banco ou no repositório.

6. **Nada de scanner embutido.** A plataforma **recebe** arquivos (`semgrep.json`,
   `nuclei.jsonl`). Não executa Semgrep, não executa Nuclei, não faz requisição para o
   alvo. Especificação §3: "O sistema não executará automaticamente o Semgrep ou o
   Nuclei".

7. **1 arquivo por alteração**, com o diff visível e "aplica" do usuário antes de seguir.
   Edição só via Edit/Write — **nunca `sed -i` nem redirecionamento `>`**.

8. **Rode a suíte antes e depois de cada arquivo alterado.** Teste que passava e começou a
   falhar: **reverter imediatamente e reportar**. Nunca ajustar o teste para o código
   passar.

9. **Escopo é o MVP da especificação §10.** Onze itens, nem um a mais. Ideia fora dessa
   lista vira AC novo em `SDD/`, discutido antes — não código de surpresa.

> Validação é real: subir a aplicação, percorrer o fluxo e conferir o resultado na tela ou
> no payload. O termo "smoke test" é proibido — diga o que foi executado e o que se viu.

---

## Regras de branch e PR — INATIVO (o projeto ainda não é um repositório git)

> Escritas agora para não precisarem ser inventadas depois. No dia em que rodar
> `git init`, esta seção passa a valer sem nenhuma outra mudança no harness.

- Nunca aja em `main`/`master`. Confira com `git branch --show-current`; se for a
  principal, **pare** e crie `git checkout -b [tipo]/[escopo]`
  (`feat|fix|debt|test|docs`).
- Toda mudança vai por PR, com revisão dual **em paralelo**: Robert Zane (QA) e Jessica
  Pearson (segurança). Ambos APROVADO antes do merge.
- Commit semântico em português: `tipo(escopo): descrição`.

**Enquanto não há git**, a rede de proteção é outra e não é opcional: um arquivo por vez,
`python -m pytest` depois de cada um, e o gate completo (`scripts/verificar.ps1`) antes de
dar qualquer tarefa por concluída.

---

## Comece por aqui (nova sessão)

1. Leia este arquivo e o `CLAUDE.md` (contrato operacional — o *como*).
2. Rode o briefing: `/briefing` — mostra o estado do gate e os ACs sem teste.
3. Só então escolha a tarefa.

## Índice navegável (para X, leia Y)

| Preciso de… | Doc |
|---|---|
| Contrato operacional, passos da sessão, proibições | `CLAUDE.md` |
| A especificação decomposta em critérios | `SDD/00-INDICE.md` |
| O PDF original, intocado | `SDD/anexos/PRIDE-Vision-AI.pdf` |
| Escrever uma spec nova | `SDD/templates/SPEC_TEMPLATE.md` + `/nova-spec` |
| Quais ACs têm teste e quais não têm | `SDD/RASTREABILIDADE.md` (gerado) |
| Convenções de teste do backend (AC ↔ teste) | `backend/tests/CLAUDE.md` |
| Convenções do frontend e dos testes de tela | `frontend/CLAUDE.md` |
| Instalar, rodar e percorrer a plataforma | `COMO_USAR.md` |
| Explicar o projeto a quem não escreveu o código | `ENTENDA_O_PROJETO.md` |
| Publicar a plataforma (Vercel + Neon, plano gratuito) | `DEPLOY.md` |
| Personas dos agents | `.claude/agents/` |
| Slash commands | `.claude/commands/` |

## Os agents

| Agent | Papel | Aciona por |
|---|---|---|
| **Harvey Specter** | Entrevista, escreve a SDD, **delega**. Nunca implementa. | `/nova-spec` |
| **Robert Zane** | QA. Deriva testes dos ACs antes da implementação; roda a suíte. | `/testes-ac`, `/revisar` |
| **Jessica Pearson** | Segurança. OWASP + as regras 3, 4, 5 e 6 acima. | `/revisar` |
| **Katrina Bennett** | Conformidade. Audita código × SDD × PDF. | `/conformidade` |
| **Louis Litt** | Implementação backend. | delegado por Harvey |
| **Mike Ross** | Implementação frontend. | delegado por Harvey |

---

## Proibições absolutas

| Proibido | Motivo |
|---|---|
| Implementar sem AC aprovado em `SDD/` | Quebra o spec-driven; vira código sem contrato |
| Escrever código antes do teste vermelho | Quebra o TDD; o teste vira carimbo |
| Importar `ai_explainer`/`ai_service` dentro de `risk_engine.py` | A IA passaria a decidir risco (regra 3) |
| Enviar texto a provedor de IA sem `mascarar()` | Vaza IP, token, senha, chave (regra 4) |
| Executar Semgrep, Nuclei ou qualquer varredura no alvo | Vira scanner; a spec proíbe (regra 6) |
| Mais de 1 arquivo por instrução | Perde rastreabilidade e a capacidade de reverter |
| `sed -i` ou redirecionamento `>` para editar | Toda edição via Edit/Write |
| Ajustar teste para o código passar | Esconde regressão |
| Apagar AC da `SDD/` para o gate ficar verde | Fraude no gate; o AC sai só com decisão do usuário |
| Commitar `.env`, `*.db` ou chave de API | Segredo em repositório |
| Dar tarefa por concluída sem rodar `scripts/verificar.ps1` | "Parece que funcionou" não é validação |
