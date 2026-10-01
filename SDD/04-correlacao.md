# SDD — Correlação dos achados

## Origem

PDF §3 (Correlação dos achados), §4.3 (Confirmação pelo outro scanner), §12 ("Comparar os
resultados. Definir o que é um match"), §13 Etapa 4.

## Contexto

Correlacionar é o que dá sentido ao produto. Quando as duas ferramentas apontam o mesmo
problema no mesmo lugar, sabe-se duas coisas ao mesmo tempo: a falha existe no código
**e** é alcançável de fora. É essa confirmação cruzada que entra na regra de risco.

O problema prático: o Semgrep reporta **caminho de arquivo**
(`src/views/busca.py`), o Nuclei reporta **caminho de URL** (`/busca`). Igualdade pura
nunca casaria os dois. O PDF pede correlação quando o endpoint for "igual ou compatível",
então "compatível" precisa de definição explícita — e explicável, porque a classificação
que sai daqui tem que ser auditável.

## Requisitos funcionais

- RF-1: Agrupar achados que tratam do mesmo problema, vindos de qualquer das duas
  ferramentas.
- RF-2: Um grupo exige **mesmo tipo canônico** de vulnerabilidade.
- RF-3: Um grupo exige endpoints **iguais ou compatíveis**.
- RF-4: Cada achado pertence a exatamente um grupo.
- RF-5: O resultado indica quais ferramentas contribuíram para o grupo.

## Considerações de segurança

- A correlação é função pura: sem banco, sem rede. Isso é o que permite auditá-la e
  reproduzi-la em teste.
- Nada aqui consulta IA. O que é ou não um match é decisão de regra, não de modelo.

## Definição de "compatível"

Dois endpoints são compatíveis quando, depois de canonizados (minúsculas, contrabarras
viram barras, query e fragmento removidos, barras repetidas colapsadas, barra final
removida, extensão de código removida do último segmento):

1. As formas canônicas são idênticas — `/busca` ~ `/busca/` ~ `/busca?q=1`
2. Um é prefixo do outro em fronteira de segmento — `/busca` ~ `/busca/avancada`
3. Compartilham o último segmento, com ao menos 3 caracteres —
   `src/views/busca.py` ~ `/busca`

O piso de 3 caracteres existe para que nomes genéricos curtos (`id`, `a`) não juntem
endpoints sem relação.

## Critérios de aceitação — testáveis

- **AC-COR-01** — Dado um achado do Semgrep e um do Nuclei com o mesmo tipo e o mesmo
  endpoint, quando correlacionados, então formam um único grupo marcado como confirmado
  pelas duas ferramentas.

- **AC-COR-02** — Dado dois achados com endpoints iguais mas **tipos diferentes**, quando
  correlacionados, então formam grupos separados.

- **AC-COR-03** — Dado dois achados do mesmo tipo cujos endpoints canônicos são idênticos
  a menos de barra final ou query, quando correlacionados, então formam um único grupo.

- **AC-COR-04** — Dado dois achados do mesmo tipo em que um endpoint é prefixo do outro em
  fronteira de segmento, quando correlacionados, então formam um único grupo.

- **AC-COR-05** — Dado um achado do Semgrep em `src/views/busca.py` e um do Nuclei em
  `/busca`, ambos do mesmo tipo, quando correlacionados, então formam um único grupo — é
  o caso que a plataforma existe para resolver.

- **AC-COR-06** — Dado dois achados do mesmo tipo cujo último segmento coincidente tem
  menos de 3 caracteres, quando correlacionados, então **não** são agrupados.

- **AC-COR-07** — Dado um conjunto de achados, quando a correlação roda com a entrada em
  ordens diferentes, então os grupos formados são os mesmos — a correlação é confluente.

- **AC-COR-08** — Dado um grupo formado, quando seu endpoint canônico é escolhido, então
  uma rota (começando com `/`) tem preferência sobre caminho de arquivo, e entre
  candidatos vence o mais curto com desempate alfabético.

- **AC-COR-09** — Dado um achado que só o Semgrep reportou, quando correlacionado, então
  forma um grupo próprio marcado como encontrado pelo Semgrep e não confirmado pelo
  Nuclei.

- **AC-COR-10** — Dado um achado que só o Nuclei reportou, quando correlacionado, então
  forma um grupo próprio marcado como confirmado pelo Nuclei e não encontrado pelo
  Semgrep.

- **AC-COR-11** `[extensão]` — Dado um grupo em que algum achado tem evidência extraída ou
  status HTTP, quando consultado, então o grupo indica que tem evidência concreta — é o
  que separa um achado teórico de um alcançado.

- **AC-COR-12** — Dado uma vulnerabilidade já gravada com endpoint de arquivo, quando o
  relatório do Nuclei chega e o grupo passa a se chamar pela rota, então a vulnerabilidade
  existente é reaproveitada e o endpoint é atualizado — não nasce um registro duplicado.

- **AC-COR-13** — Dado dois achados do mesmo tipo em endpoints sem nenhuma relação, quando
  correlacionados, então formam grupos separados: nenhuma das três regras de
  compatibilidade se aplica, e agrupar por tipo apenas juntaria problemas distintos.

- **AC-COR-14** — Dado um conjunto de achados, quando correlacionados, então a soma dos
  achados de todos os grupos é igual ao total de entrada: cada achado pertence a
  exatamente um grupo, nenhum se perde e nenhum é contado duas vezes.

## Casos de borda

- **AC-COR-E1** — Dado uma lista de achados vazia, quando correlacionada, então o
  resultado é uma lista vazia de grupos, sem erro.

- **AC-COR-E2** `[extensão]` — Dado dois grupos que casam com a mesma vulnerabilidade já
  gravada, quando a recorrelação roda, então cada registro é reivindicado por no máximo um
  grupo.

- **AC-COR-E3** — Dado um endpoint vazio ou apenas `/`, quando comparado com outro, então
  a compatibilidade não é declarada por coincidência de segmento inexistente.

## Restrições conscientes

- A correlação depende de o nome do arquivo lembrar a rota. Se o Semgrep reportar
  `src/handlers/h1.py` para código que atende `/busca`, os dois **não** correlacionam. A
  saída é preencher `extra.metadata.route` no relatório (ver `AC-ING-11`). É consequência
  direta da exigência do PDF por regras simples e explicáveis em vez de correspondência
  probabilística.
- Sem pontuação de similaridade, sem aprendizado de máquina, sem heurística difusa. Um
  match ou é explicável por uma das três regras acima, ou não é match.

## Validação real

- Fluxo: enviar um `semgrep.json` com achado em `src/views/busca.py` e um `nuclei.jsonl`
  com achado em `https://host/busca`, ambos XSS → abrir a vulnerabilidade.
- O que deve aparecer: **uma** vulnerabilidade, não duas, com as duas ferramentas listadas
  na origem.
- Critério: o detalhe mostra dois achados sob a mesma vulnerabilidade.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
