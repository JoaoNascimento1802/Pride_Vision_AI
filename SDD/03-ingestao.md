# SDD — Ingestão dos relatórios

## Origem

PDF §3 (upload manual), §4.2 (Centralização dos achados), §12 (parsers do Semgrep e do
Nuclei, padronização dos dados), §13 Etapa 3.

## Contexto

É a porta de entrada da plataforma. Dois formatos diferentes — `semgrep.json` (um objeto
JSON com a lista `results`) e `nuclei.jsonl` (um objeto JSON por linha) — precisam virar
o mesmo tipo interno para que correlação e risco não saibam de qual ferramenta veio o
achado.

Relatório real vem com lixo. Perder o arquivo inteiro por causa de uma entrada malformada
seria pior do que descartar a entrada e avisar.

## Requisitos funcionais

- RF-1: Receber `semgrep.json` por upload e transformar cada resultado em achado
  padronizado.
- RF-2: Receber `nuclei.jsonl` por upload e transformar cada linha em achado padronizado.
- RF-3: Padronizar tipo de vulnerabilidade e endpoint, para que os dois formatos fiquem
  comparáveis.
- RF-4: Preservar a severidade original informada pela ferramenta.
- RF-5: Registrar o que foi lido, o que foi ignorado e por quê.
- RF-6: Um novo relatório da mesma ferramenta **substitui** o anterior daquela aplicação.

## Considerações de segurança

- Upload exige autenticação.
- Há limite de tamanho por arquivo (`MAX_UPLOAD_BYTES`, 20 MB por padrão): um arquivo
  gigante não pode derrubar o processo.
- O conteúdo precisa ser UTF-8 válido.
- O conteúdo do relatório nunca é interpretado como código, comando ou caminho de
  arquivo local — é só texto a ser parseado como JSON.

## Critérios de aceitação — testáveis

- **AC-ING-01** — Dado um `semgrep.json` válido, quando enviado para uma aplicação, então
  cada item de `results` vira um achado com tipo, endpoint, severidade, mensagem, regra,
  arquivo e linha.

- **AC-ING-02** — Dado um `nuclei.jsonl` válido, quando enviado para uma aplicação, então
  cada linha vira um achado com tipo, endpoint, severidade, template, URL e — quando
  houver — evidência extraída e status HTTP.

- **AC-ING-03** — Dado um achado do Semgrep, quando o tipo é normalizado, então nomes
  sinônimos da mesma família (`cross-site scripting`, `reflected-xss`, `dom-xss`) chegam
  ao mesmo tipo canônico.

- **AC-ING-04** — Dado um achado do Nuclei com URL completa, quando o endpoint é
  normalizado, então esquema, domínio, porta e query são descartados e resta o caminho.

- **AC-ING-05** — Dado que a ferramenta informou uma severidade, quando o achado é
  gravado, então essa severidade original é preservada e exibível ao lado do risco
  calculado pelo PRIDE.

- **AC-ING-06** — Dado um `semgrep.json` com um resultado sem campo obrigatório, quando é
  enviado, então aquele resultado é ignorado com aviso e os demais são processados.

- **AC-ING-07** — Dado um `nuclei.jsonl` com uma linha que não é JSON válido, quando é
  enviado, então aquela linha é ignorada com aviso e as demais são processadas.

- **AC-ING-08** — Dado um upload concluído, quando a API responde, então informa quantos
  achados foram lidos, quantos ignorados, os avisos e quantas vulnerabilidades ficaram
  totais, novas e atualizadas.

- **AC-ING-09** — Dado que já existe um relatório do Semgrep para a aplicação, quando um
  novo relatório do Semgrep é enviado, então o anterior é substituído e seus achados não
  permanecem somados aos novos.

- **AC-ING-10** — Dado um relatório do Semgrep já enviado, quando o relatório do Nuclei
  chega depois, então a recorrelação considera **todos** os achados gravados da aplicação,
  não apenas os do upload atual.

- **AC-ING-11** `[extensão]` — Dado um achado do Semgrep cujo `extra.metadata.route` está
  preenchido, quando o endpoint é determinado, então a rota declarada é usada em vez do
  caminho do arquivo.

- **AC-ING-12** — Dado uma aplicação, quando seus uploads são listados, então aparece o
  relatório em vigor por ferramenta, com nome do arquivo e data.

- **AC-ING-13** — Dado vulnerabilidades gravadas, quando a listagem é consultada, então
  cada item traz os cinco campos que o PDF §4.2 exige da centralização: qual ferramenta
  encontrou, qual aplicação foi afetada, o tipo da vulnerabilidade, a severidade original
  e o status da análise.

- **AC-ING-14** `[extensão]` — Dado a listagem, quando filtrada por aplicação, risco, tipo
  ou "somente correlacionadas", então apenas os itens correspondentes são devolvidos.

## Casos de borda

- **AC-ING-E1** — Dado um arquivo vazio, quando enviado, então a API responde 422 com
  mensagem em português e nada é gravado.

- **AC-ING-E2** — Dado um arquivo que não é JSON válido, quando enviado como relatório do
  Semgrep, então a API responde 422 explicando o problema de sintaxe.

- **AC-ING-E3** — Dado um arquivo maior que o limite configurado, quando enviado, então a
  API responde 413 informando o limite.

- **AC-ING-E4** — Dado um arquivo que não está em UTF-8, quando enviado, então a API
  responde 422 pedindo UTF-8.

- **AC-ING-E5** — Dado um upload para uma aplicação inexistente, quando enviado, então a
  API responde 404.

- **AC-ING-E6** — Dado um `nuclei.jsonl` com linhas em branco, quando enviado, então as
  linhas em branco são ignoradas em silêncio, sem contar como ignoradas nem gerar aviso.

- **AC-ING-E7** `[extensão]` — Dado um tipo de vulnerabilidade fora das famílias
  conhecidas, quando o achado é normalizado, então o nome original em minúsculas é
  preservado e o achado continua sendo correlacionado e classificado.

## Contrato de API

| Método | Rota | Corpo | Resposta | Erros |
|---|---|---|---|---|
| POST | `/api/aplicacoes/{id}/uploads/semgrep` | multipart `arquivo` | 201 `ResultadoUploadResponse` | 401, 404, 413, 422 |
| POST | `/api/aplicacoes/{id}/uploads/nuclei` | multipart `arquivo` | 201 `ResultadoUploadResponse` | 401, 404, 413, 422 |
| GET | `/api/aplicacoes/{id}/uploads` | — | `UploadResumo[]` | 401, 404 |

## Restrições conscientes

- O vocabulário de tipos cobre cinco famílias: XSS, SQL Injection, SSRF, RCE/Command
  Injection e Path Traversal. Outros tipos passam com o nome original — são
  correlacionados e classificados, só não são unificados com sinônimos. Ampliar significa
  editar `MAPA_TIPOS` em `backend/app/services/normalizer.py`.
- Só dois formatos. Outros scanners exigiriam parser novo e AC novo.
- Vulnerabilidade que sumiu do relatório mais recente é **removida**, junto com o
  histórico dela. A plataforma reflete a varredura atual.

## Validação real

- Fluxo: enviar `semgrep.json` → conferir o resumo do upload → enviar `nuclei.jsonl` →
  conferir o resumo de novo.
- O que deve aparecer: no segundo upload, `vulnerabilidades_atualizadas` maior que zero —
  prova de que os achados do Semgrep foram reaproveitados na correlação.
- Critério: `achados_lidos` bate com o número de entradas do arquivo enviado.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
