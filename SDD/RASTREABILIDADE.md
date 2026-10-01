# Rastreabilidade — AC ↔ teste

> **Arquivo gerado.** Não edite à mão: rode `python scripts/rastreabilidade.py --emitir`.
> Cada critério da `SDD/` aparece aqui com os testes que o provam. AC sem teste
> reprova o gate.

## Resumo

| Métrica | Valor |
|---|---|
| Critérios declarados | 316 |
| Com ao menos um teste | 316 |
| Sem teste | 0 |
| Vindos do PDF | 267 |
| Extensões (decisão de projeto) | 49 |
| Proibições (o que o sistema não pode fazer) | 15 |

## 01-visao-geral.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-FLUXO-01` | PDF | Dado uma aplicação cadastrada, quando o relatório do Semgrep é enviado e em seguida o do Nuclei, então a lista de vulnerabilidades traz o problema comum às d… | `backend/tests/test_ingestion.py:134` |
| `AC-FLUXO-02` | PDF | Dado vulnerabilidades de riscos diferentes na mesma base, quando a lista é consultada, então elas vêm ordenadas de Crítico para Baixo. | `backend/tests/test_vulnerabilities.py:42` |
| `AC-FLUXO-03` | proibição | Dado os módulos de ingestão, correlação e risco, quando suas dependências são inspecionadas, então nenhum importa cliente HTTP (requests, httpx, urllib.reque… | `backend/tests/test_infra.py:282`<br>`backend/tests/test_infra.py:283`<br>`backend/tests/test_infra.py:284`<br>`backend/tests/test_infra.py:285` |
| `AC-FLUXO-04` | proibição | Dado o conjunto de rotas publicadas pela API, quando inspecionado, então não existe rota que dispare varredura, execução de ferramenta ou chamada ao alvo — a… | `backend/tests/test_infra.py:297`<br>`backend/tests/test_infra.py:310` |
| `AC-FLUXO-05` | extensão | Dado uma base sem nenhum relatório enviado, quando a lista de vulnerabilidades é consultada, então a resposta é uma lista vazia com HTTP 200, não um erro. | `backend/tests/test_vulnerabilities.py:111` |
| `AC-FLUXO-06` | PDF | Dado que o mesmo problema foi apontado pelas duas ferramentas, quando a vulnerabilidade é consultada, então ela indica que foi encontrada pelo Semgrep e conf… | `backend/tests/test_ingestion.py:116`<br>`backend/tests/test_vulnerabilities.py:62`<br>`backend/tests/test_vulnerabilities.py:123` |
| `AC-FLUXO-07` | proibição | Dado uma requisição sem token, quando qualquer rota que devolve dado de vulnerabilidade é chamada (listagem, detalhe, dashboard), então a API responde 401 e … | `backend/tests/test_vulnerabilities.py:117`<br>`backend/tests/test_vulnerabilities.py:419` |
| `AC-FLUXO-E1` | PDF | Dado que só o relatório do Semgrep foi enviado, quando a lista é consultada, então as vulnerabilidades aparecem marcadas como não confirmadas dinamicamente, … | `backend/tests/test_ingestion.py:160` |
| `AC-FLUXO-E2` | PDF | Dado que o relatório do Nuclei chega depois do Semgrep, quando a ingestão termina, então a correlação considera os achados antigos já gravados e não só os do… | `backend/tests/test_ingestion.py:147` |
| `AC-FLUXO-E3` | PDF | Dado um identificador de vulnerabilidade inexistente, quando o detalhe é consultado, então a API responde 404 com mensagem em português. | `backend/tests/test_vulnerabilities.py:163` |

## 02-inventario.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-INV-01` | PDF | Dado um usuário autenticado, quando cadastra uma aplicação com nome, responsável, ambiente, exposição, importância e URL, então a API responde 201 e devolve … | `backend/tests/test_applications.py:25`<br>`backend/tests/test_applications.py:86`<br>`backend/tests/test_applications.py:178`<br>`backend/tests/test_applications.py:190` |
| `AC-INV-02` | PDF | Dado o vocabulário de ambiente, quando uma aplicação é cadastrada com producao, homologacao ou teste, então o cadastro é aceito. | `backend/tests/test_applications.py:45`<br>`backend/tests/test_applications.py:46`<br>`backend/tests/test_applications.py:47` |
| `AC-INV-03` | PDF | Dado o vocabulário de exposição, quando uma aplicação é cadastrada com internet ou interna, então o cadastro é aceito. | `backend/tests/test_applications.py:59`<br>`backend/tests/test_applications.py:60` |
| `AC-INV-04` | PDF | Dado o vocabulário de importância, quando uma aplicação é cadastrada com alta, media ou baixa, então o cadastro é aceito. | `backend/tests/test_applications.py:72`<br>`backend/tests/test_applications.py:73`<br>`backend/tests/test_applications.py:74` |
| `AC-INV-05` | PDF | Dado um valor fora do vocabulário controlado em ambiente, exposição ou importância, quando o cadastro é tentado, então a API responde 422 e nada é gravado. | `backend/tests/test_applications.py:113`<br>`backend/tests/test_applications.py:114`<br>`backend/tests/test_applications.py:115` |
| `AC-INV-06` | PDF | Dado aplicações cadastradas com vulnerabilidades, quando a lista é consultada, então cada item traz ambiente, exposição, importância e a quantidade total de … | `backend/tests/test_applications.py:136`<br>`backend/tests/test_applications.py:140`<br>`backend/tests/test_applications.py:156` |
| `AC-INV-07` | PDF | Dado que a URL é opcional, quando uma aplicação é cadastrada sem URL, então o cadastro é aceito e a URL fica nula. | `backend/tests/test_applications.py:95` |
| `AC-INV-08` | PDF | Dado uma aplicação com vulnerabilidades já classificadas, quando seu ambiente, exposição ou importância é alterado, então as vulnerabilidades são reclassific… | `backend/tests/test_applications.py:202`<br>`backend/tests/test_ingestion.py:312`<br>`backend/tests/test_ingestion.py:347` |
| `AC-INV-09` | extensão | Dado uma aplicação com uploads, achados e vulnerabilidades, quando ela é removida, então tudo que veio dela é removido em cascata. | `backend/tests/test_applications.py:220`<br>`backend/tests/test_infra.py:401`<br>`backend/tests/test_ingestion.py:362` |
| `AC-INV-10` | proibição | Dado uma requisição sem token, quando qualquer rota de /api/aplicacoes é chamada, então a API responde 401 e nenhum dado de inventário é devolvido. | `backend/tests/test_applications.py:130`<br>`backend/tests/test_applications.py:170`<br>`backend/tests/test_ingestion.py:89` |
| `AC-INV-11` | PDF | Dado uma aplicação cadastrada, quando o resumo dela é consultado, então vêm as contagens por risco e por status daquela aplicação. | `backend/tests/test_applications.py:237`<br>`backend/tests/test_applications.py:256` |
| `AC-INV-E1` | PDF | Dado um nome com menos de 2 caracteres, quando o cadastro é tentado, então a API responde 422. | `backend/tests/test_applications.py:125` |
| `AC-INV-E2` | PDF | Dado um identificador de aplicação inexistente, quando ela é consultada, editada ou removida, então a API responde 404 com mensagem em português. | `backend/tests/test_applications.py:184`<br>`backend/tests/test_applications.py:213`<br>`backend/tests/test_applications.py:231`<br>`backend/tests/test_applications.py:270` |
| `AC-INV-E3` | extensão | Dado nome e responsável com espaços nas pontas, quando a aplicação é cadastrada, então os valores são gravados sem os espaços. | `backend/tests/test_applications.py:101` |
| `AC-INV-E4` | PDF | Dado uma aplicação sem nenhuma vulnerabilidade, quando a lista é consultada, então os contadores vêm zerados, não ausentes. | `backend/tests/test_applications.py:147` |

## 03-ingestao.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-ING-01` | PDF | Dado um semgrep.json válido, quando enviado para uma aplicação, então cada item de results vira um achado com tipo, endpoint, severidade, mensagem, regra, ar… | `backend/tests/test_ingestion.py:38`<br>`backend/tests/test_services.py:140`<br>`backend/tests/test_services.py:217`<br>`backend/tests/test_vulnerabilities.py:131` |
| `AC-ING-02` | PDF | Dado um nuclei.jsonl válido, quando enviado para uma aplicação, então cada linha vira um achado com tipo, endpoint, severidade, template, URL e — quando houv… | `backend/tests/test_ingestion.py:99`<br>`backend/tests/test_services.py:223`<br>`backend/tests/test_services.py:246`<br>`backend/tests/test_services.py:263`<br>`backend/tests/test_services.py:295`<br>`backend/tests/test_vulnerabilities.py:141` |
| `AC-ING-03` | PDF | Dado um achado do Semgrep, quando o tipo é normalizado, então nomes sinônimos da mesma família (cross-site scripting, reflected-xss, dom-xss) chegam ao mesmo… | `backend/tests/test_services.py:48`<br>`backend/tests/test_services.py:66` |
| `AC-ING-04` | PDF | Dado um achado do Nuclei com URL completa, quando o endpoint é normalizado, então esquema, domínio, porta e query são descartados e resta o caminho. | `backend/tests/test_services.py:86`<br>`backend/tests/test_services.py:90` |
| `AC-ING-05` | PDF | Dado que a ferramenta informou uma severidade, quando o achado é gravado, então essa severidade original é preservada e exibível ao lado do risco calculado p… | `backend/tests/test_ingestion.py:388`<br>`backend/tests/test_ingestion.py:389`<br>`backend/tests/test_services.py:167`<br>`backend/tests/test_services.py:276` |
| `AC-ING-06` | PDF | Dado um semgrep.json com um resultado sem campo obrigatório, quando é enviado, então aquele resultado é ignorado com aviso e os demais são processados. | `backend/tests/test_services.py:203` |
| `AC-ING-07` | PDF | Dado um nuclei.jsonl com uma linha que não é JSON válido, quando é enviado, então aquela linha é ignorada com aviso e as demais são processadas. | `backend/tests/test_ingestion.py:105`<br>`backend/tests/test_services.py:287` |
| `AC-ING-08` | PDF | Dado um upload concluído, quando a API responde, então informa quantos achados foram lidos, quantos ignorados, os avisos e quantas vulnerabilidades ficaram t… | `backend/tests/test_ingestion.py:38`<br>`backend/tests/test_ingestion.py:99`<br>`backend/tests/test_ingestion.py:105` |
| `AC-ING-09` | PDF | Dado que já existe um relatório do Semgrep para a aplicação, quando um novo relatório do Semgrep é enviado, então o anterior é substituído e seus achados não… | `backend/tests/test_ingestion.py:182`<br>`backend/tests/test_ingestion.py:216`<br>`backend/tests/test_ingestion.py:228` |
| `AC-ING-10` | PDF | Dado um relatório do Semgrep já enviado, quando o relatório do Nuclei chega depois, então a recorrelação considera todos os achados gravados da aplicação, nã… | `backend/tests/test_ingestion.py:116` |
| `AC-ING-11` | extensão | Dado um achado do Semgrep cujo extra.metadata.route está preenchido, quando o endpoint é determinado, então a rota declarada é usada em vez do caminho do arq… | `backend/tests/test_services.py:183` |
| `AC-ING-12` | PDF | Dado uma aplicação, quando seus uploads são listados, então aparece o relatório em vigor por ferramenta, com nome do arquivo e data. | `backend/tests/test_ingestion.py:228`<br>`backend/tests/test_ingestion.py:240` |
| `AC-ING-13` | PDF | Dado vulnerabilidades gravadas, quando a listagem é consultada, então cada item traz os cinco campos que o PDF §4.2 exige da centralização: qual ferramenta e… | `backend/tests/test_vulnerabilities.py:48`<br>`backend/tests/test_vulnerabilities.py:62` |
| `AC-ING-14` | extensão | Dado a listagem, quando filtrada por aplicação, risco, tipo ou "somente correlacionadas", então apenas os itens correspondentes são devolvidos. | `backend/tests/test_vulnerabilities.py:70`<br>`backend/tests/test_vulnerabilities.py:72`<br>`backend/tests/test_vulnerabilities.py:96`<br>`backend/tests/test_vulnerabilities.py:106` |
| `AC-ING-E1` | PDF | Dado um arquivo vazio, quando enviado, então a API responde 422 com mensagem em português e nada é gravado. | `backend/tests/test_ingestion.py:45` |
| `AC-ING-E2` | PDF | Dado um arquivo que não é JSON válido, quando enviado como relatório do Semgrep, então a API responde 422 explicando o problema de sintaxe. | `backend/tests/test_ingestion.py:57`<br>`backend/tests/test_services.py:212` |
| `AC-ING-E3` | PDF | Dado um arquivo maior que o limite configurado, quando enviado, então a API responde 413 informando o limite. | `backend/tests/test_ingestion.py:65` |
| `AC-ING-E4` | PDF | Dado um arquivo que não está em UTF-8, quando enviado, então a API responde 422 pedindo UTF-8. | `backend/tests/test_ingestion.py:74` |
| `AC-ING-E5` | PDF | Dado um upload para uma aplicação inexistente, quando enviado, então a API responde 404. | `backend/tests/test_ingestion.py:84` |
| `AC-ING-E6` | PDF | Dado um nuclei.jsonl com linhas em branco, quando enviado, então as linhas em branco são ignoradas em silêncio, sem contar como ignoradas nem gerar aviso. | `backend/tests/test_services.py:299` |
| `AC-ING-E7` | extensão | Dado um tipo de vulnerabilidade fora das famílias conhecidas, quando o achado é normalizado, então o nome original em minúsculas é preservado e o achado cont… | `backend/tests/test_services.py:52` |

## 04-correlacao.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-COR-01` | PDF | Dado um achado do Semgrep e um do Nuclei com o mesmo tipo e o mesmo endpoint, quando correlacionados, então formam um único grupo marcado como confirmado pel… | `backend/tests/test_services.py:319` |
| `AC-COR-02` | PDF | Dado dois achados com endpoints iguais mas tipos diferentes, quando correlacionados, então formam grupos separados. | `backend/tests/test_services.py:341` |
| `AC-COR-03` | PDF | Dado dois achados do mesmo tipo cujos endpoints canônicos são idênticos a menos de barra final ou query, quando correlacionados, então formam um único grupo. | `backend/tests/test_services.py:98`<br>`backend/tests/test_services.py:99`<br>`backend/tests/test_services.py:100`<br>`backend/tests/test_services.py:132` |
| `AC-COR-04` | PDF | Dado dois achados do mesmo tipo em que um endpoint é prefixo do outro em fronteira de segmento, quando correlacionados, então formam um único grupo. | `backend/tests/test_services.py:101`<br>`backend/tests/test_services.py:115` |
| `AC-COR-05` | PDF | Dado um achado do Semgrep em src/views/busca.py e um do Nuclei em /busca, ambos do mesmo tipo, quando correlacionados, então formam um único grupo — é o caso… | `backend/tests/test_services.py:102`<br>`backend/tests/test_services.py:103`<br>`backend/tests/test_services.py:330` |
| `AC-COR-06` | PDF | Dado dois achados do mesmo tipo cujo último segmento coincidente tem menos de 3 caracteres, quando correlacionados, então não são agrupados. | `backend/tests/test_services.py:117` |
| `AC-COR-07` | PDF | Dado um conjunto de achados, quando a correlação roda com a entrada em ordens diferentes, então os grupos formados são os mesmos — a correlação é confluente. | `backend/tests/test_services.py:126`<br>`backend/tests/test_services.py:405` |
| `AC-COR-08` | PDF | Dado um grupo formado, quando seu endpoint canônico é escolhido, então uma rota (começando com /) tem preferência sobre caminho de arquivo, e entre candidato… | `backend/tests/test_services.py:330`<br>`backend/tests/test_services.py:418` |
| `AC-COR-09` | PDF | Dado um achado que só o Semgrep reportou, quando correlacionado, então forma um grupo próprio marcado como encontrado pelo Semgrep e não confirmado pelo Nucl… | `backend/tests/test_services.py:361` |
| `AC-COR-10` | PDF | Dado um achado que só o Nuclei reportou, quando correlacionado, então forma um grupo próprio marcado como confirmado pelo Nuclei e não encontrado pelo Semgre… | `backend/tests/test_services.py:369` |
| `AC-COR-11` | extensão | Dado um grupo em que algum achado tem evidência extraída ou status HTTP, quando consultado, então o grupo indica que tem evidência concreta — é o que separa … | `backend/tests/test_services.py:379`<br>`backend/tests/test_services.py:380`<br>`backend/tests/test_services.py:389` |
| `AC-COR-12` | PDF | Dado uma vulnerabilidade já gravada com endpoint de arquivo, quando o relatório do Nuclei chega e o grupo passa a se chamar pela rota, então a vulnerabilidad… | `backend/tests/test_ingestion.py:170` |
| `AC-COR-13` | PDF | Dado dois achados do mesmo tipo em endpoints sem nenhuma relação, quando correlacionados, então formam grupos separados: nenhuma das três regras de compatibi… | `backend/tests/test_services.py:113`<br>`backend/tests/test_services.py:351` |
| `AC-COR-14` | PDF | Dado um conjunto de achados, quando correlacionados, então a soma dos achados de todos os grupos é igual ao total de entrada: cada achado pertence a exatamen… | `backend/tests/test_services.py:394` |
| `AC-COR-E1` | PDF | Dado uma lista de achados vazia, quando correlacionada, então o resultado é uma lista vazia de grupos, sem erro. | `backend/tests/test_services.py:429` |
| `AC-COR-E2` | extensão | Dado dois grupos que casam com a mesma vulnerabilidade já gravada, quando a recorrelação roda, então cada registro é reivindicado por no máximo um grupo. | `backend/tests/test_ingestion.py:277` |
| `AC-COR-E3` | PDF | Dado um endpoint vazio ou apenas /, quando comparado com outro, então a compatibilidade não é declarada por coincidência de segmento inexistente. | `backend/tests/test_services.py:118` |

## 05-risco.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-RISCO-01` | PDF | Dado confirmação pelas duas ferramentas com evidência, aplicação em produção e exposta à internet, quando classificada, então o risco é Crítico. | `backend/tests/test_risk_engine.py:68`<br>`backend/tests/test_risk_engine.py:184`<br>`backend/tests/test_risk_engine.py:193` |
| `AC-RISCO-02` | PDF | Dado confirmação pelas duas ferramentas com evidência, aplicação em produção, interna, com importância alta, quando classificada, então o risco é Crítico — i… | `backend/tests/test_risk_engine.py:76` |
| `AC-RISCO-03` | extensão | Dado confirmação pelas duas ferramentas, aplicação em produção, interna e de importância não-alta, quando classificada, então o risco é Alto. | `backend/tests/test_risk_engine.py:84` |
| `AC-RISCO-04` | extensão | Dado confirmação pelas duas ferramentas e aplicação em homologação, quando classificada, então o risco é Alto. O PDF exclui este caso do bloco Médio/Baixo ao… | `backend/tests/test_risk_engine.py:92`<br>`backend/tests/test_risk_engine.py:100`<br>`backend/tests/test_risk_engine.py:175` |
| `AC-RISCO-05` | extensão | Dado confirmação pelas duas ferramentas e aplicação em ambiente de teste, quando classificada, então o risco é Médio. O PDF reserva Baixo para o achado "apen… | `backend/tests/test_risk_engine.py:108`<br>`backend/tests/test_risk_engine.py:175`<br>`backend/tests/test_risk_engine.py:193` |
| `AC-RISCO-06` | PDF | Dado achado de uma única ferramenta e aplicação em produção, quando classificada, então o risco é Alto, conforme as duas condições do PDF §5: aplicação em pr… | `backend/tests/test_risk_engine.py:117`<br>`backend/tests/test_risk_engine.py:125`<br>`backend/tests/test_risk_engine.py:133`<br>`backend/tests/test_risk_engine.py:184` |
| `AC-RISCO-07` | PDF | Dado achado de uma única ferramenta em produção, quando a aplicação é interna e de importância não-alta, então o risco continua Alto: o PDF §5 não qualifica … | `backend/tests/test_risk_engine.py:141`<br>`backend/tests/test_risk_engine.py:205` |
| `AC-RISCO-08` | PDF | Dado achado de uma única ferramenta e aplicação em homologação, quando classificada, então o risco é Médio. | `backend/tests/test_risk_engine.py:149` |
| `AC-RISCO-09` | PDF | Dado achado de uma única ferramenta e aplicação em ambiente de teste, quando classificada, então o risco é Baixo. | `backend/tests/test_risk_engine.py:157`<br>`backend/tests/test_risk_engine.py:165` |
| `AC-RISCO-10` | PDF | Dado que todas as ferramentas classificaram o achado como informativo ou baixo, quando classificado, então o risco desce exatamente um nível em relação à mat… | `backend/tests/test_ingestion.py:375`<br>`backend/tests/test_risk_engine.py:263`<br>`backend/tests/test_risk_engine.py:270`<br>`backend/tests/test_risk_engine.py:276`<br>`backend/tests/test_risk_engine.py:284`<br>`backend/tests/test_risk_engine.py:324` |
| `AC-RISCO-11` | PDF | Dado que alguma ferramenta marcou severidade crítica, a aplicação está em produção e é relevante para o negócio, quando classificado, então o risco sobe exat… | `backend/tests/test_risk_engine.py:263`<br>`backend/tests/test_risk_engine.py:289`<br>`backend/tests/test_risk_engine.py:324` |
| `AC-RISCO-12` | PDF | Dado severidade crítica em aplicação que não está em produção, quando classificada, então não há elevação — a condição exige as três juntas. | `backend/tests/test_risk_engine.py:296`<br>`backend/tests/test_risk_engine.py:303` |
| `AC-RISCO-13` | PDF | Dado um achado já no topo da escala, quando a elevação se aplicaria, então o risco permanece Crítico: a escada não passa do topo. | `backend/tests/test_risk_engine.py:310` |
| `AC-RISCO-14` | PDF | Dado um achado já no fim da escala, quando o rebaixamento se aplicaria, então o risco permanece Baixo: a escada não passa do fundo. | `backend/tests/test_risk_engine.py:316` |
| `AC-RISCO-15` | PDF | Dado qualquer classificação, quando concluída, então vem acompanhada de uma justificativa em texto não vazia que cita o ambiente e a situação de confirmação. | `backend/tests/test_risk_engine.py:333`<br>`backend/tests/test_risk_engine.py:341`<br>`backend/tests/test_risk_engine.py:372`<br>`backend/tests/test_risk_engine.py:380`<br>`backend/tests/test_risk_engine.py:388`<br>`backend/tests/test_risk_engine.py:395`<br>`backend/tests/test_vulnerabilities.py:150` |
| `AC-RISCO-16` | PDF | Dado a mesma entrada, quando classificada duas vezes, então o resultado é idêntico — nível e justificativa. | `backend/tests/test_risk_engine.py:404` |
| `AC-RISCO-17` | proibição | Dado o módulo app/services/risk_engine.py, quando suas importações são inspecionadas, então ele não importa ai_explainer, ai_service nem qualquer SDK de IA. | `backend/tests/test_risk_engine.py:463` |
| `AC-RISCO-18` | proibição | Dado o módulo app/services/risk_engine.py, quando suas importações são inspecionadas, então ele não importa sqlalchemy nem cliente de rede: a classificação n… | `backend/tests/test_risk_engine.py:481` |
| `AC-RISCO-19` | PDF | Dado um grupo com achados de severidades diferentes, quando a severidade predominante é calculada, então é a mais grave entre elas, e ela não participa da de… | `backend/tests/test_risk_engine.py:424`<br>`backend/tests/test_risk_engine.py:433` |
| `AC-RISCO-20` | PDF | Dado uma aplicação exposta à internet ou de importância alta, quando o contexto é avaliado, então ela é considerada crítica para o negócio; nas demais combin… | `backend/tests/test_applications.py:278`<br>`backend/tests/test_applications.py:291`<br>`backend/tests/test_applications.py:304`<br>`backend/tests/test_risk_engine.py:439`<br>`backend/tests/test_risk_engine.py:444`<br>`backend/tests/test_risk_engine.py:449` |
| `AC-RISCO-21` | PDF | Dado vulnerabilidades já classificadas, quando o ambiente, a exposição ou a importância da aplicação muda, então todas são reclassificadas com o novo context… | `backend/tests/test_ingestion.py:312`<br>`backend/tests/test_ingestion.py:332` |
| `AC-RISCO-22` | PDF | Dado confirmação pelas duas ferramentas, aplicação em produção e crítica para o negócio, porém sem evidência extraída nem status HTTP, quando classificada, e… | `backend/tests/test_risk_engine.py:232`<br>`backend/tests/test_risk_engine.py:237`<br>`backend/tests/test_risk_engine.py:247` |
| `AC-RISCO-23` | PDF | Dado um achado sem evidência que a severidade crítica elevaria até Crítico, quando classificado, então o resultado para em Alto: a elevação por severidade nã… | `backend/tests/test_risk_engine.py:242` |
| `AC-RISCO-E1` | extensão | Dado um grupo sem nenhum achado, quando classificado, então o risco é Baixo com justificativa dizendo que não há evidência para classificar. | `backend/tests/test_risk_engine.py:413` |
| `AC-RISCO-E2` | extensão | Dado um achado cuja severidade a ferramenta não informou, quando classificado, então a ausência é tratada como severidade baixa e não quebra a classificação. | `backend/tests/test_risk_engine.py:348` |
| `AC-RISCO-E3` | PDF | Dado severidades escritas em português ou em inglês (crítica, critical, alta, high, error), quando avaliadas, então são reconhecidas como equivalentes. | `backend/tests/test_risk_engine.py:357`<br>`backend/tests/test_risk_engine.py:358`<br>`backend/tests/test_risk_engine.py:362` |

## 06-ia.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-IA-01` | PDF | Dado um texto contendo um endereço IPv4, quando mascarado, então o IP é substituído por [IP_MASCARADO]. | `backend/tests/test_services.py:437`<br>`backend/tests/test_services.py:458` |
| `AC-IA-02` | PDF | Dado um texto contendo um token JWT ou um cabeçalho Bearer, quando mascarado, então o token é substituído por [TOKEN_MASCARADO]. | `backend/tests/test_services.py:439`<br>`backend/tests/test_services.py:444` |
| `AC-IA-03` | PDF | Dado um texto contendo uma senha atribuída a variável (password=, senha:), quando mascarado, então o valor é substituído por [SENHA_MASCARADA]. | `backend/tests/test_services.py:447`<br>`backend/tests/test_services.py:448` |
| `AC-IA-04` | PDF | Dado um texto contendo uma chave de API atribuída a variável, quando mascarado, então o valor é substituído por [API_KEY_MASCARADO]. | `backend/tests/test_services.py:446` |
| `AC-IA-05` | PDF | Dado uma lista de nomes internos configurada, quando o texto é mascarado, então cada ocorrência literal é substituída por [NOME_MASCARADO]. | `backend/tests/test_ai.py:122`<br>`backend/tests/test_services.py:465` |
| `AC-IA-06` | extensão | Dado um texto contendo endereço de e-mail, quando mascarado, então é substituído por [EMAIL_MASCARADO]. | `backend/tests/test_services.py:449`<br>`backend/tests/test_services.py:458` |
| `AC-IA-07` | extensão | Dado um texto contendo endereço IPv6, quando mascarado, então é substituído por [IP_MASCARADO]. | `backend/tests/test_services.py:450` |
| `AC-IA-08` | PDF | Dado um texto sem nenhum dado sensível, quando mascarado, então é devolvido inalterado. | `backend/tests/test_services.py:471`<br>`backend/tests/test_services.py:476` |
| `AC-IA-09` | proibição | Dado dados técnicos contendo IP, token e senha, quando a análise é solicitada, então o prompt efetivamente entregue ao provedor não contém nenhum dos três va… | `backend/tests/test_ai.py:115`<br>`backend/tests/test_ai.py:122`<br>`backend/tests/test_ai.py:128` |
| `AC-IA-10` | PDF | Dado uma vulnerabilidade classificada e um provedor configurado, quando a análise é gerada, então a resposta traz explicação, impacto, justificativa da prior… | `backend/tests/test_ai.py:100`<br>`backend/tests/test_ai.py:139`<br>`backend/tests/test_ai.py:182` |
| `AC-IA-11` | PDF | Dado a análise gerada, quando o detalhe da vulnerabilidade é consultado, então os textos da IA aparecem junto com a data de geração. | `backend/tests/test_ai.py:182`<br>`backend/tests/test_ai.py:197`<br>`backend/tests/test_vulnerabilities.py:156` |
| `AC-IA-12` | PDF | Dado o prompt montado, quando inspecionado, então ele informa o risco e a justificativa já decididos e instrui explicitamente que a classificação não deve se… | `backend/tests/test_ai.py:83`<br>`backend/tests/test_ai.py:89` |
| `AC-IA-13` | proibição | Dado o módulo de IA, quando suas dependências são inspecionadas, então ele não importa risk_engine nem correlator: não há caminho para a IA participar da dec… | `backend/tests/test_ai.py:580` |
| `AC-IA-14` | proibição | Dado que a IA respondeu, quando a análise é gravada, então o nível de risco e a justificativa da vulnerabilidade permanecem exatamente os que as regras havia… | `backend/tests/test_ai.py:207` |
| `AC-IA-15` | proibição | Dado que a IA respondeu, quando a análise é gravada, então o status de acompanhamento da vulnerabilidade não é alterado — a IA não aprova correção. | `backend/tests/test_ai.py:236` |
| `AC-IA-16` | proibição | Dado o prompt montado, quando inspecionado, então ele não contém termos que induzam ação no repositório ou no alvo (commit, push, pull request, criar branch,… | `backend/tests/test_ai.py:94` |
| `AC-IA-17` | proibição | Dado o módulo de IA, quando suas dependências são inspecionadas, então ele não importa subprocess, os.system nem biblioteca de execução: não há como a IA exe… | `backend/tests/test_ai.py:587` |
| `AC-IA-18` | PDF | Dado AI_DEFAULT_PROVIDER=openai com chave configurada, quando a análise é gerada, então o provedor OpenAI é usado. | `backend/tests/test_ai.py:303` |
| `AC-IA-19` | PDF | Dado AI_DEFAULT_PROVIDER=gemini com chave configurada, quando a análise é gerada, então o provedor Gemini é usado. | `backend/tests/test_ai.py:309` |
| `AC-IA-20` | PDF | Dado que nenhuma chave está configurada para o provedor selecionado, quando a análise é solicitada, então a API responde 503 com mensagem explicando que a IA… | `backend/tests/test_ai.py:258`<br>`backend/tests/test_ai.py:316` |
| `AC-IA-21` | PDF | Dado que o provedor falhou, quando a análise é solicitada, então a API responde 502 e a vulnerabilidade continua com risco, justificativa e status válidos. | `backend/tests/test_ai.py:162`<br>`backend/tests/test_ai.py:275`<br>`backend/tests/test_ai.py:285` |
| `AC-IA-22` | extensão | Dado que a resposta do modelo veio envolvida em cerca de bloco de código, quando interpretada, então as cercas são removidas e o JSON é lido. | `backend/tests/test_ai.py:146` |
| `AC-IA-23` | extensão | Dado OPENAI_MODELS configurado no ambiente e o primeiro modelo da lista indisponível para a chave, quando a análise é gerada, então o provedor tenta o próxim… | `backend/tests/test_ai.py:439`<br>`backend/tests/test_ai.py:526` |
| `AC-IA-24` | extensão | Dado OPENAI_MODEL ou GEMINI_MODEL configurado, quando o provedor é construído, então usa exatamente esse modelo: escolha explícita do usuário não é substituí… | `backend/tests/test_ai.py:537`<br>`backend/tests/test_ai.py:546` |
| `AC-IA-25` | extensão | Dado o provedor e o modelo configurados, quando a rota de saúde é consultada, então informa qual provedor e qual modelo serão usados — descobrir isso é a par… | `backend/tests/test_ai.py:557` |
| `AC-IA-26` | proibição | Dado o módulo que constrói os provedores, quando inspecionado, então nenhum nome de modelo aparece literalmente nele: os nomes vêm da configuração ou das lis… | `backend/tests/test_ai.py:566` |
| `AC-IA-27` | extensão | Dado que o provedor Gemini está configurado com uma chave, quando a análise é gerada, então a chamada acontece pelo SDK google.genai — um Client(api_key=…) s… | `backend/tests/test_ai.py:463`<br>`backend/tests/test_ai.py:473`<br>`backend/tests/test_ai.py:507` |
| `AC-IA-28` | extensão | Dado que o primeiro modelo candidato não é aceito pela chave, quando o provedor Gemini gera a análise, então o próximo candidato da lista é tentado; e, com G… | `backend/tests/test_ai.py:487`<br>`backend/tests/test_ai.py:497` |
| `AC-IA-E1` | PDF | Dado que a resposta do provedor não é JSON válido, quando interpretada, então um erro de provedor é levantado e nada parcial é gravado. | `backend/tests/test_ai.py:151` |
| `AC-IA-E2` | PDF | Dado que a resposta é um JSON sem algumas das seis chaves, quando interpretada, então as chaves ausentes viram texto vazio, sem quebrar. | `backend/tests/test_ai.py:156` |
| `AC-IA-E3` | PDF | Dado uma vulnerabilidade inexistente, quando a análise é solicitada, então a API responde 404. | `backend/tests/test_ai.py:297` |
| `AC-IA-E4` | extensão | Dado que o modelo configurado foi aposentado pelo provedor, quando a análise é gerada, então o próximo modelo candidato é tentado; se o usuário fixou o model… | `backend/tests/test_ai.py:419`<br>`backend/tests/test_ai.py:429` |

## 07-acompanhamento.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-STATUS-01` | PDF | Dado o vocabulário de status, quando consultado, então existem exatamente cinco: Nova, Em análise, Em correção, Corrigida e Falso positivo. | `backend/tests/test_vulnerabilities.py:171`<br>`backend/tests/test_vulnerabilities.py:173` |
| `AC-STATUS-02` | PDF | Dado uma vulnerabilidade recém-identificada na ingestão, quando consultada, então seu status é Nova. | `backend/tests/test_vulnerabilities.py:210` |
| `AC-STATUS-03` | PDF | Dado uma vulnerabilidade com status Nova, quando o usuário a marca como Em correção, então o novo status é gravado e devolvido. | `backend/tests/test_vulnerabilities.py:216` |
| `AC-STATUS-04` | PDF | Dado uma vulnerabilidade, quando o usuário a marca como Corrigida, então o novo status é gravado e ela deixa de contar como aberta. | `backend/tests/test_vulnerabilities.py:228` |
| `AC-STATUS-05` | PDF | Dado uma vulnerabilidade, quando o usuário a marca como Falso positivo, então o novo status é gravado e ela deixa de contar como aberta. | `backend/tests/test_vulnerabilities.py:318` |
| `AC-STATUS-06` | extensão | Dado uma mudança de status, quando gravada, então o histórico registra status anterior, status novo, o usuário que mudou, o instante e o comentário opcional. | `backend/tests/test_vulnerabilities.py:246` |
| `AC-STATUS-07` | PDF | Dado uma vulnerabilidade com histórico, quando o detalhe é consultado, então o histórico completo vem junto, com o nome de quem fez cada mudança. | `backend/tests/test_vulnerabilities.py:246` |
| `AC-STATUS-08` | PDF | Dado vulnerabilidades em status diferentes, quando o dashboard é consultado, então traz a contagem por status. | `backend/tests/test_vulnerabilities.py:352`<br>`backend/tests/test_vulnerabilities.py:354`<br>`backend/tests/test_vulnerabilities.py:369` |
| `AC-STATUS-09` | PDF | Dado uma vulnerabilidade cujo status o usuário já mudou para Em correção, quando um novo relatório é enviado e a vulnerabilidade continua existindo, então o … | `backend/tests/test_ingestion.py:191` |
| `AC-STATUS-10` | proibição | Dado uma ingestão de relatório, quando concluída, então nenhum status de vulnerabilidade existente é alterado pela ingestão. | `backend/tests/test_ingestion.py:191` |
| `AC-STATUS-11` | PDF | Dado uma vulnerabilidade, quando a lista é filtrada por um status, então só as vulnerabilidades naquele status são devolvidas. | `backend/tests/test_vulnerabilities.py:71`<br>`backend/tests/test_vulnerabilities.py:82` |
| `AC-STATUS-12` | extensão | Dado os status Corrigida e Falso positivo, quando avaliados, então são considerados encerrados; Nova, Em análise e Em correção são considerados abertos. | `backend/tests/test_infra.py:196`<br>`backend/tests/test_vulnerabilities.py:189`<br>`backend/tests/test_vulnerabilities.py:190`<br>`backend/tests/test_vulnerabilities.py:191`<br>`backend/tests/test_vulnerabilities.py:192`<br>`backend/tests/test_vulnerabilities.py:193`<br>`backend/tests/test_vulnerabilities.py:194`<br>`backend/tests/test_vulnerabilities.py:196`<br>`backend/tests/test_vulnerabilities.py:198`<br>`backend/tests/test_vulnerabilities.py:199`<br>`backend/tests/test_vulnerabilities.py:200` |
| `AC-STATUS-E1` | extensão | Dado uma vulnerabilidade já no status desejado, quando o usuário tenta mudá-la para o mesmo status, então a API responde 409 e nenhum registro duplicado entr… | `backend/tests/test_vulnerabilities.py:266` |
| `AC-STATUS-E2` | PDF | Dado um status fora do vocabulário, quando a mudança é tentada, então a API responde 422. | `backend/tests/test_vulnerabilities.py:284` |
| `AC-STATUS-E3` | PDF | Dado uma vulnerabilidade inexistente, quando a mudança de status é tentada, então a API responde 404. | `backend/tests/test_vulnerabilities.py:292` |
| `AC-STATUS-E4` | PDF | Dado uma mudança de status sem comentário, quando gravada, então é aceita e o comentário fica nulo. | `backend/tests/test_vulnerabilities.py:299` |
| `AC-STATUS-E5` | PDF | Dado uma requisição sem token, quando a mudança de status é tentada, então a API responde 401 e nada é alterado. | `backend/tests/test_vulnerabilities.py:308` |

## 08-interface.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-UI-01` | PDF | Dado dados de dashboard carregados, quando a visão geral é exibida, então mostra o total de aplicações. | `frontend/src/pages/__tests__/Dashboard.test.tsx:27` |
| `AC-UI-02` | PDF | Dado dados de dashboard carregados, quando a visão geral é exibida, então mostra o total de vulnerabilidades. | `frontend/src/pages/__tests__/Dashboard.test.tsx:33` |
| `AC-UI-03` | PDF | Dado dados de dashboard carregados, quando a visão geral é exibida, então mostra a quantidade de vulnerabilidades críticas. | `frontend/src/pages/__tests__/Dashboard.test.tsx:39` |
| `AC-UI-04` | PDF | Dado dados de dashboard carregados, quando a visão geral é exibida, então mostra a quantidade de vulnerabilidades em correção. | `frontend/src/pages/__tests__/Dashboard.test.tsx:46` |
| `AC-UI-05` | PDF | Dado aplicações com vulnerabilidades, quando a visão geral é exibida, então mostra a lista de aplicações com maior risco, com ambiente e exposição de cada um… | `frontend/src/pages/__tests__/Dashboard.test.tsx:52` |
| `AC-UI-06` | extensão | Dado nenhuma aplicação cadastrada, quando a visão geral é exibida, então aparece um estado vazio orientando a cadastrar uma aplicação, e não uma tela de zero… | `frontend/src/pages/__tests__/Dashboard.test.tsx:63` |
| `AC-UI-07` | PDF | Dado aplicações cadastradas, quando a tela de aplicações é exibida, então lista cada aplicação com nome, ambiente, exposição e importância para o negócio. | `frontend/src/pages/__tests__/Aplicacoes.test.tsx:44` |
| `AC-UI-08` | PDF | Dado aplicações com vulnerabilidades, quando a tela de aplicações é exibida, então mostra a quantidade de vulnerabilidades de cada uma. | `frontend/src/pages/__tests__/Aplicacoes.test.tsx:53` |
| `AC-UI-09` | PDF | Dado o formulário de cadastro, quando exibido, então oferece os campos nome, responsável, ambiente, exposição, importância e URL. | `frontend/src/pages/__tests__/Aplicacoes.test.tsx:63` |
| `AC-UI-10` | PDF | Dado o formulário preenchido, quando enviado, então a aplicação é cadastrada e passa a aparecer na lista. | `frontend/src/pages/__tests__/Aplicacoes.test.tsx:82` |
| `AC-UI-11` | extensão | Dado uma aplicação cadastrada, quando o envio de relatório é acionado a partir dela, então é possível enviar o arquivo do Semgrep e o do Nuclei. | `frontend/src/pages/__tests__/Aplicacoes.test.tsx:104`<br>`frontend/src/pages/__tests__/Aplicacoes.test.tsx:141` |
| `AC-UI-12` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra o nome/tipo da vulnerabilidade. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:50` |
| `AC-UI-13` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra a aplicação afetada. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:55` |
| `AC-UI-14` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra a origem: Semgrep, Nuclei ou ambas. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:60` |
| `AC-UI-15` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra a severidade original informada pela ferramenta. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:72` |
| `AC-UI-16` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra o risco calculado pelo PRIDE. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:77` |
| `AC-UI-17` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra o status da correção. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:83` |
| `AC-UI-18` | PDF | Dado vulnerabilidades carregadas, quando a lista é exibida, então cada linha mostra a data da identificação. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:89` |
| `AC-UI-19` | extensão | Dado a lista exibida, quando os filtros são usados, então é possível filtrar por aplicação, risco, status e somente correlacionadas, e o filtro aplicado fica… | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:96`<br>`frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:105`<br>`frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:116` |
| `AC-UI-20` | extensão | Dado nenhuma vulnerabilidade correspondente, quando a lista é exibida, então aparece um estado vazio explicando o que fazer. | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:125` |
| `AC-UI-21` | PDF | Dado uma vulnerabilidade, quando o detalhe é exibido, então mostra a justificativa da classificação. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:45` |
| `AC-UI-22` | PDF | Dado um achado do Semgrep com arquivo e linha, quando o detalhe é exibido, então mostra arquivo e linha. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:52` |
| `AC-UI-23` | PDF | Dado uma vulnerabilidade, quando o detalhe é exibido, então mostra o endpoint afetado e, havendo achado do Nuclei, a URL. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:59` |
| `AC-UI-24` | PDF | Dado um achado do Nuclei com evidência, quando o detalhe é exibido, então mostra a evidência. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:68` |
| `AC-UI-25` | PDF | Dado uma análise de IA já gerada, quando o detalhe é exibido, então mostra a explicação, o impacto, a justificativa da priorização, a sugestão de correção, c… | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:75` |
| `AC-UI-26` | PDF | Dado uma vulnerabilidade, quando o detalhe é exibido, então oferece controle para alterar o status entre os cinco valores. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:90` |
| `AC-UI-27` | PDF | Dado o controle de status, quando um novo status é escolhido, então a mudança é enviada à API e a tela reflete o novo status. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:99` |
| `AC-UI-28` | extensão | Dado uma vulnerabilidade com histórico, quando o detalhe é exibido, então mostra o histórico com autor e data de cada mudança. | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:116` |
| `AC-UI-29` | extensão | Dado que ainda não há análise de IA, quando o detalhe é exibido, então explica que a IA recebe o risco já classificado e não participa da decisão, com um bot… | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:141`<br>`frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:148` |
| `AC-UI-30` | PDF | Dado a tela de login, quando exibida, então oferece campos de e-mail e senha e um botão de entrar. | `frontend/src/pages/__tests__/Login.test.tsx:39` |
| `AC-UI-31` | PDF | Dado credenciais válidas, quando o login é enviado, então o token é guardado e o usuário chega à visão geral. | `frontend/src/pages/__tests__/Login.test.tsx:47` |
| `AC-UI-32` | PDF | Dado credenciais inválidas, quando o login é enviado, então a mensagem de erro da API é exibida e o usuário permanece na tela de login. | `frontend/src/pages/__tests__/Login.test.tsx:64` |
| `AC-UI-33` | PDF | Dado aplicações e vulnerabilidades cadastradas, quando o dashboard é consultado, então a API devolve total de aplicações, total de vulnerabilidades, total de… | `backend/tests/test_vulnerabilities.py:336`<br>`backend/tests/test_vulnerabilities.py:385` |
| `AC-UI-34` | PDF | Dado vulnerabilidades de riscos variados, quando o dashboard é consultado, então a contagem por risco cobre os quatro níveis, na ordem Crítico → Alto → Médio… | `backend/tests/test_vulnerabilities.py:346` |
| `AC-UI-35` | PDF | Dado aplicações com vulnerabilidades, quando o dashboard é consultado, então o ranking de aplicações em risco traz nome, ambiente, exposição, quantidade de c… | `backend/tests/test_vulnerabilities.py:400` |
| `AC-UI-E1` | PDF | Dado que a API está fora do ar, quando uma tela carrega, então aparece mensagem dizendo que não foi possível falar com o servidor, com opção de tentar de nov… | `frontend/src/pages/__tests__/Dashboard.test.tsx:71` |
| `AC-UI-E2` | PDF | Dado que a API respondeu 401, quando qualquer tela faz uma chamada, então a sessão é encerrada e o usuário volta ao login. | `frontend/src/auth/__tests__/AuthContext.test.tsx:2`<br>`frontend/src/auth/__tests__/AuthContext.test.tsx:42`<br>`frontend/src/auth/__tests__/AuthContext.test.tsx:56` |
| `AC-UI-E3` | PDF | Dado que os dados ainda estão carregando, quando a tela é exibida, então aparece o indicador de carregamento, não uma tela em branco. | `frontend/src/pages/__tests__/Dashboard.test.tsx:79` |
| `AC-UI-E4` | extensão | Dado uma vulnerabilidade sem severidade original, quando a lista é exibida, então a célula mostra um traço, não vazio nem "null". | `frontend/src/pages/__tests__/Vulnerabilidades.test.tsx:133` |
| `AC-UI-E5` | PDF | Dado uma base sem nenhuma aplicação, quando o dashboard é consultado, então todos os totais vêm zerados e o ranking vem como lista vazia, sem erro. | `backend/tests/test_vulnerabilities.py:412` |

## 09-arquitetura.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-ARQ-01` | PDF | Dado a aplicação iniciada, quando a rota de saúde é consultada, então responde 200 com o status, a versão e se a IA está configurada. | `backend/tests/test_infra.py:48`<br>`backend/tests/test_infra.py:55`<br>`backend/tests/test_infra.py:59` |
| `AC-ARQ-02` | PDF | Dado a aplicação iniciada, quando a rota de opções é consultada, então devolve o vocabulário controlado de ambientes, exposições, importâncias, riscos e stat… | `backend/tests/test_infra.py:152`<br>`backend/tests/test_infra.py:163`<br>`backend/tests/test_infra.py:170`<br>`backend/tests/test_infra.py:175`<br>`backend/tests/test_infra.py:185`<br>`backend/tests/test_infra.py:192` |
| `AC-ARQ-03` | PDF | Dado a API montada, quando as rotas são inspecionadas, então existem os sete módulos do §9: aplicações, uploads, vulnerabilidades, correlação e risco (via in… | `backend/tests/test_infra.py:206`<br>`backend/tests/test_infra.py:218`<br>`backend/tests/test_infra.py:222`<br>`backend/tests/test_infra.py:225`<br>`backend/tests/test_infra.py:228`<br>`backend/tests/test_infra.py:233`<br>`backend/tests/test_infra.py:235`<br>`backend/tests/test_infra.py:244` |
| `AC-ARQ-04` | extensão | Dado os módulos de serviço puros (normalizer, correlator, data_masker, risk_engine), quando suas importações são inspecionadas, então nenhum importa sqlalche… | `backend/tests/test_infra.py:257`<br>`backend/tests/test_infra.py:258`<br>`backend/tests/test_infra.py:259`<br>`backend/tests/test_infra.py:260` |
| `AC-ARQ-05` | PDF | Dado a configuração padrão, quando o banco é resolvido, então é SQLite. | `backend/tests/test_infra.py:344` |
| `AC-ARQ-06` | proibição | Dado o código do backend, quando inspecionado, então não há dependência de orquestrador, fila, cache distribuído ou segundo serviço — o monólito é um process… | `backend/tests/test_infra.py:338` |
| `AC-ARQ-07` | PDF | Dado um arquivo .env, quando a configuração é carregada, então os pares CHAVE=VALOR viram variáveis de ambiente sem sobrescrever as já definidas. | `backend/tests/test_config.py:20`<br>`backend/tests/test_config.py:39` |
| `AC-ARQ-08` | PDF | Dado SECRET_KEY ausente, quando a configuração é lida, então uma chave aleatória é gerada e a aplicação sinaliza que ela não foi definida. | `backend/tests/test_config.py:65` |
| `AC-ARQ-09` | PDF | Dado SECRET_KEY com menos de 32 bytes, quando a configuração é lida, então é sinalizada como fraca. | `backend/tests/test_config.py:55`<br>`backend/tests/test_config.py:60` |
| `AC-ARQ-10` | PDF | Dado AI_DEFAULT_PROVIDER e a chave correspondente, quando a configuração é lida, então a IA é reportada como configurada; sem a chave, como não configurada. | `backend/tests/test_config.py:75`<br>`backend/tests/test_config.py:81`<br>`backend/tests/test_config.py:87` |
| `AC-ARQ-11` | extensão | Dado MAX_UPLOAD_BYTES definido no ambiente, quando a configuração é lida, então o limite de upload passa a ser esse valor. | `backend/tests/test_config.py:99`<br>`backend/tests/test_config.py:104` |
| `AC-ARQ-12` | extensão | Dado PRIDE_INTERNAL_NAMES com nomes separados por vírgula, quando a configuração é lida, então vira a lista de nomes internos usada no mascaramento. | `backend/tests/test_config.py:111`<br>`backend/tests/test_config.py:116` |
| `AC-ARQ-13` | extensão | Dado CORS_ORIGINS definido, quando a aplicação sobe, então apenas essas origens são liberadas. | `backend/tests/test_config.py:175`<br>`backend/tests/test_config.py:183` |
| `AC-ARQ-14` | extensão | Dado OPENAI_MODELS ou GEMINI_MODELS no ambiente, como lista separada por vírgula, quando a configuração é lida, então vira a lista de modelos candidatos daqu… | `backend/tests/test_config.py:130`<br>`backend/tests/test_config.py:135` |
| `AC-ARQ-15` | extensão | Dado nenhuma variável de modelo definida, quando a configuração é lida, então valem as listas padrão do projeto, e OPENAI_MODEL e GEMINI_MODEL ficam vazios. | `backend/tests/test_config.py:140` |
| `AC-ARQ-16` | extensão | Dado o provedor ativo e a configuração de modelos, quando o modelo previsto é consultado, então é o modelo explícito quando houver, e o primeiro candidato da… | `backend/tests/test_config.py:153`<br>`backend/tests/test_config.py:159`<br>`backend/tests/test_config.py:166` |
| `AC-ARQ-17` | extensão | Dado DATABASE_URL sem driver declarado, em qualquer das duas formas que os provedores entregam (postgres://… ou postgresql://…), quando a configuração é lida… | `backend/tests/test_config.py:199`<br>`backend/tests/test_config.py:209`<br>`backend/tests/test_config.py:217`<br>`backend/tests/test_config.py:222`<br>`backend/tests/test_config.py:227` |
| `AC-ARQ-18` | extensão | Dado um banco que não é SQLite, quando uma conexão é aberta, então o PRAGMA foreign_keys=ON não é executado e a conexão continua utilizável; dado SQLite, ent… | `backend/tests/test_infra.py:380`<br>`backend/tests/test_infra.py:401` |
| `AC-ARQ-19` | extensão | Dado que o banco está inacessível na inicialização, quando a aplicação sobe, então ela sobe mesmo assim e a rota de saúde responde 200 com status: "degradado… | `backend/tests/test_infra.py:63`<br>`backend/tests/test_infra.py:69`<br>`backend/tests/test_infra.py:133` |
| `AC-ARQ-20` | extensão | Dado DATABASE_URL com driver ausente ou esquema inválido, quando os módulos da aplicação são importados, então o import conclui e nenhuma conexão é tentada; … | `backend/tests/test_infra.py:88`<br>`backend/tests/test_infra.py:104`<br>`backend/tests/test_infra.py:120` |
| `AC-ARQ-21` | extensão | Dado que os schemas usam EmailStr, quando as dependências declaradas são inspecionadas, então pydantic aparece com o extra email, de forma que uma instalação… | `backend/tests/test_infra.py:351` |
| `AC-ARQ-E1` | PDF | Dado um .env inexistente, quando a configuração é carregada, então nada quebra e valem os padrões. | `backend/tests/test_config.py:49` |
| `AC-ARQ-E2` | extensão | Dado um .env com linha em branco, comentário ou linha sem =, quando carregado, então essas linhas são ignoradas. | `backend/tests/test_config.py:20` |
| `AC-LOGIN-01` | PDF | Dado um e-mail e uma senha novos, quando o registro é feito, então o usuário é criado e a senha é guardada como hash, nunca em texto. | `backend/tests/test_auth.py:20`<br>`backend/tests/test_auth.py:24`<br>`backend/tests/test_auth.py:28`<br>`backend/tests/test_auth.py:32`<br>`backend/tests/test_auth.py:36`<br>`backend/tests/test_auth.py:57`<br>`backend/tests/test_auth.py:66` |
| `AC-LOGIN-02` | PDF | Dado credenciais corretas, quando o login é feito, então a API devolve um token e os dados do usuário. | `backend/tests/test_auth.py:42`<br>`backend/tests/test_auth.py:126`<br>`backend/tests/test_auth.py:183` |
| `AC-LOGIN-03` | PDF | Dado credenciais incorretas, quando o login é tentado, então a API responde 401. | `backend/tests/test_auth.py:137`<br>`backend/tests/test_auth.py:145` |
| `AC-LOGIN-04` | PDF | Dado um e-mail que não existe e uma senha errada de e-mail existente, quando os dois logins são tentados, então a mensagem de erro é a mesma — não se revela … | `backend/tests/test_auth.py:152` |
| `AC-LOGIN-05` | PDF | Dado um token válido, quando a rota de identificação é chamada, então devolve o usuário do token. | `backend/tests/test_auth.py:187` |
| `AC-LOGIN-06` | PDF | Dado um token ausente, inválido ou expirado, quando uma rota protegida é chamada, então a API responde 401. | `backend/tests/test_auth.py:46`<br>`backend/tests/test_auth.py:51`<br>`backend/tests/test_auth.py:165`<br>`backend/tests/test_auth.py:169`<br>`backend/tests/test_auth.py:174` |
| `AC-LOGIN-07` | extensão | Dado um e-mail já cadastrado, quando o registro é repetido, então a API responde 409. | `backend/tests/test_auth.py:84`<br>`backend/tests/test_auth.py:92` |
| `AC-LOGIN-08` | extensão | Dado um e-mail com maiúsculas ou espaços, quando o registro e o login são feitos, então funcionam: o e-mail é normalizado. | `backend/tests/test_auth.py:76`<br>`backend/tests/test_auth.py:92` |
| `AC-LOGIN-E1` | extensão | Dado uma senha acima do limite suportado pelo bcrypt, quando o registro é tentado, então a API responde 422 explicando, em vez de truncar em silêncio. | `backend/tests/test_auth.py:116` |
| `AC-LOGIN-E2` | PDF | Dado um e-mail em formato inválido, quando o registro é tentado, então a API responde 422. | `backend/tests/test_auth.py:100` |
| `AC-LOGIN-E3` | extensão | Dado uma senha abaixo do comprimento mínimo, quando o registro é tentado, então a API responde 422. | `backend/tests/test_auth.py:108` |

## 11-ci-security-gates.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-CI-01` | PDF | Dado que o usuário com permissão policy:write envia uma política válida em POST /api/ci/policies, quando a requisição é processada, então a política é criada… | `backend/tests/test_ci.py:4`<br>`backend/tests/test_ci.py:79`<br>`backend/tests/test_ci.py:83` |
| `AC-CI-02` | PDF | Dado que o usuário com permissão policy:read acessa GET /api/ci/policies, então a resposta lista apenas as políticas ativas. | `backend/tests/test_ci.py:96`<br>`backend/tests/test_ci.py:100` |
| `AC-CI-03` | PDF | Dado que o usuário com permissão policy:write envia DELETE /api/ci/policies/{id}, então a política é desativada (soft delete, ativa=False) e o endpoint retor… | `backend/tests/test_ci.py:107`<br>`backend/tests/test_ci.py:111` |
| `AC-CI-04` | PDF | Dado que um usuário com papel DEVELOPER tenta criar uma política via POST /api/ci/policies, então a requisição é rejeitada com 403. | `backend/tests/test_ci.py:122`<br>`backend/tests/test_ci.py:130` |
| `AC-CI-05` | PDF | Dado que um pipeline com permissão gate:check envia um payload válido para POST /api/ci/check, quando a aplicação não possui vulnerabilidades abertas nem pol… | `backend/tests/test_ci.py:148`<br>`backend/tests/test_ci.py:154`<br>`backend/tests/test_security_gate.py:5`<br>`backend/tests/test_security_gate.py:113`<br>`backend/tests/test_security_gate.py:117`<br>`backend/tests/test_security_gate.py:123`<br>`backend/tests/test_security_gate.py:127` |
| `AC-CI-06` | PDF | Dado que a aplicação possui uma vulnerabilidade com risco CRITICO e existe uma política global com risco_minimo=critico e acao=block, quando o pipeline chama… | `backend/tests/test_ci.py:159`<br>`backend/tests/test_ci.py:165`<br>`backend/tests/test_security_gate.py:133`<br>`backend/tests/test_security_gate.py:137` |
| `AC-CI-07` | PDF | Dado o cenário do AC-CI-06, quando existe uma PolicyException válida (não expirada) para aquela vulnerabilidade e política, então a decisão muda para "pass" … | `backend/tests/test_ci.py:174`<br>`backend/tests/test_ci.py:180`<br>`backend/tests/test_security_gate.py:147`<br>`backend/tests/test_security_gate.py:151` |
| `AC-CI-08` | PDF | Dado que a exceção do AC-CI-07 está expirada (data passada), então a decisão retorna a ser "block". | `backend/tests/test_ci.py:202`<br>`backend/tests/test_ci.py:208`<br>`backend/tests/test_security_gate.py:164`<br>`backend/tests/test_security_gate.py:168` |
| `AC-CI-09` | PDF | Dado que existe uma política com acao=warn e a vulnerabilidade atinge o risco mínimo sem exceção, então a decisão é "warn". | `backend/tests/test_ci.py:228`<br>`backend/tests/test_ci.py:234`<br>`backend/tests/test_security_gate.py:180`<br>`backend/tests/test_security_gate.py:184` |
| `AC-CI-10` | PDF | Dado que existem duas políticas: uma com acao=block e outra com acao=warn, e a vulnerabilidade viola ambas, então a decisão final é "block" (a mais restritiv… | `backend/tests/test_security_gate.py:193`<br>`backend/tests/test_security_gate.py:197` |
| `AC-CI-11` | PDF | Dado que o mesmo pipeline chama POST /api/ci/check duas vezes com idênticos pipeline_id e commit_sha, então apenas um PipelineRun é criado, mas dois Security… | `backend/tests/test_ci.py:254`<br>`backend/tests/test_ci.py:260` |
| `AC-CI-12` | PDF | Dado que o pipeline_id e o commit_sha são null, então cada chamada a POST /api/ci/check cria um novo PipelineRun. | `backend/tests/test_ci.py:276`<br>`backend/tests/test_ci.py:282` |
| `AC-CI-13` | PDF | Dado que o usuário com permissão exception:write cria uma PolicyException via POST /api/ci/exceptions, então a exceção é persistida e retornada com valida=Tr… | `backend/tests/test_ci.py:421`<br>`backend/tests/test_ci.py:427`<br>`backend/tests/test_ci.py:439` |
| `AC-CI-14` | PDF | Dado que a exceção possui expira_em=None, então valida é sempre True (exceção permanente). | `backend/tests/test_security_gate.py:207`<br>`backend/tests/test_security_gate.py:211` |
| `AC-CI-15` | PDF | Dado que um usuário com papel DEVELOPER tenta criar uma exceção, então a requisição é rejeitada com 403. | `backend/tests/test_ci.py:298`<br>`backend/tests/test_ci.py:304`<br>`backend/tests/test_security_gate.py:5` |
| `AC-CI-16` | PDF | Dado que existem SecurityGateResult registrados, quando o usuário acessa GET /api/ci/gate-results?aplicacao_id={id}, então a resposta lista os resultados em … | `backend/tests/test_ci.py:325`<br>`backend/tests/test_ci.py:331` |
| `AC-CI-17` | PDF | Dado que existem PipelineRun registrados, quando o usuário acessa GET /api/ci/pipelines?aplicacao_id={id}, então a resposta inclui o campo ultimo_resultado c… | `backend/tests/test_ci.py:344`<br>`backend/tests/test_ci.py:350` |
| `AC-CI-18` | PDF | Dado que qualquer usuário envia {"decision": "pass"} no payload de POST /api/ci/check, então esse campo é ignorado — a decisão é sempre calculada pelo PRIDE … | `backend/tests/test_ci.py:366`<br>`backend/tests/test_ci.py:372` |
| `AC-CI-19` | PDF | Dado que um usuário sem autenticação chama POST /api/ci/check, então a resposta é 401. | `backend/tests/test_ci.py:389`<br>`backend/tests/test_ci.py:393` |
| `AC-CI-20` | PDF | Dado que a resposta do Security Gate é retornada, então ela não contém tokens, senhas, chaves de API ou segredos internos. | `backend/tests/test_ci.py:4`<br>`backend/tests/test_ci.py:401`<br>`backend/tests/test_ci.py:407` |

## 12-iac-scanning.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-IAC-01` | PDF | Parser extrai recursos. Dado um relatório JSON válido do Checkov, Quando for parseado por ler_checkov, Então deve extrair os recursos, arquivo, linha e frame… | `backend/tests/test_checkov.py:7` |
| `AC-IAC-02` | PDF | Arquivo vazio levanta exceção. Dado uma string vazia, Quando for parseada por ler_checkov, Então a função levanta ValueError. | `backend/tests/test_checkov.py:43` |
| `AC-IAC-03` | PDF | JSON inválido levanta exceção. Dado uma string JSON quebrada, Quando for parseada por ler_checkov, Então a função levanta ValueError. | `backend/tests/test_checkov.py:49` |
| `AC-IAC-04` | PDF | Checkov report faltando campos. Dado um finding sem check_id ou check_name, Quando for parseado, Então o item é pulado e incrementa ignorados. | `backend/tests/test_checkov.py:55` |
| `AC-IAC-05` | PDF | Múltiplos findings no JSON. Dado um array de relatórios gerado pelo Checkov, Quando parseado, Então o parser deve extrair os achados de todos os relatórios d… | `backend/tests/test_checkov.py:74` |

## 13-container-scanning.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-CONT-01` | PDF | Parser diferencia SCA e Container. Dado um relatorio do Trivy, Quando o ArtifactType for container_image, Entao o parser deve definir o tipo do achado como c… | `backend/tests/test_trivy.py:50` |
| `AC-CONT-02` | PDF | Parser extrai detalhes do container. Dado um relatorio do Trivy de container, Quando for parseado, Entao o parser deve extrair digest, tags, OS, base image e… | `backend/tests/test_trivy.py:50` |
| `AC-CONT-03` | PDF | Ingestao cria entidade de container. Dado um upload de Trivy com informacoes de imagem, Quando os achados forem salvos, Entao uma ContainerImage unica basead… | `backend/tests/test_ingestion.py:403` |
| `AC-CONT-04` | PDF | Endpoint baseado no digest. Dado um achado de container, Quando normalizado, Entao o endpoint deve usar o digest da imagem para evitar duplicatas erroneas. | `backend/tests/test_trivy.py:50` |

## 14-jira-ticketing-oauth.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-JIRA-01` | PDF | Iniciar fluxo de autorizacao. Dado um usuario autenticado, Quando chamar GET /api/integrations/jira/authorize, Entao recebe uma URL contendo os parametros co… | `backend/tests/test_jira_oauth.py:13` |
| `AC-JIRA-02` | PDF | State invalido bloqueia callback. Dado um callback OAuth, Quando o state for ausente, expirado ou forjado, Entao a API rejeita com HTTP 400. | `backend/tests/test_jira_oauth.py:29` |
| `AC-JIRA-03` | PDF | Token exchange bem sucedido salva credenciais. Dado um authorization code valido, Quando chamar GET /api/integrations/jira/callback, Entao o PRIDE troca o co… | `backend/tests/test_jira_oauth.py:71` |
| `AC-JIRA-04` | PDF | Criptografia de Tokens. Dado que os tokens (access e refresh) serao armazenados, Quando forem gravados no banco de dados, Entao devem usar criptografia simet… | `backend/tests/test_api_tickets.py:30` |
| `AC-JIRA-05` | PDF | Renovaçao Automatica (Refresh). Dado um access_token expirado, Quando uma operação do Jira for tentada, Entao o sistema deve usar o refresh token, obter um n… | `backend/tests/test_api_tickets.py:30` |
| `AC-JIRA-06` | PDF | Criação real de Issue. Dado uma Vulnerabilidade com provider Jira, Quando criar o ticket, Entao faz uma requisição HTTP real à API do Jira Cloud com payload … | `backend/tests/test_api_tickets.py:30` |
| `AC-JIRA-07` | PDF | Sync de Status. Dado um ticket Jira ja criado, Quando sincronizado, Entao deve refletir o titulo e o status mapeado localmente, atualizando o Ticket. | `backend/tests/test_api_tickets.py:100` |
| `AC-JIRA-08` | PDF | Falha de comunicação e permissão. Dado um ticket e token invalido não-renovavel ou erro 403, Quando chamar a API, Entao deve tratar o erro de forma tolerante… | `backend/tests/test_api_tickets.py:100` |
| `AC-JIRA-09` | PDF | Conexão Múltipla. Dado que o sistema suporta integração 3LO, Quando múltiplos usuários se conectam ao Jira, Entao a conexão é realizada via Integration assoc… | `backend/tests/test_api_tickets.py:100` |

## 15-audit-log.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-AUDIT-01` | PDF | Mascaramento de dados sensíveis. - Dado um payload de requisição contendo "password", "token", "secret" (mesmo aninhados) - Quando o AuditService registra a … | `backend/tests/test_audit.py:12` |
| `AC-AUDIT-02` | PDF | Imutabilidade da trilha. - Dado um registro no AuditLog - Quando o usuário tentar deletar ou atualizar via API REST - Então a operação não deve existir (404/… | `backend/tests/test_audit.py:70` |
| `AC-AUDIT-03` | PDF | Registro de Login e Logout. - Dado uma tentativa de login (sucesso ou falha) ou logout - Quando a ação for processada - Então um evento LOGIN_SUCCESS, LOGIN_… | `backend/tests/test_audit.py:79`<br>`backend/tests/test_audit.py:91` |
| `AC-AUDIT-04` | PDF | Ações de Vulnerabilidades e Políticas. - Dado a criação/atualização de uma Vulnerabilidade ou Policy - Quando a ação for concluída - Então deve gerar um Audi… | `backend/tests/test_audit.py:103` |
| `AC-AUDIT-05` | PDF | Ações de CI/CD e Ticketing. - Dado a execução de um Security Gate ou sincronização de Ticket - Quando a ação terminar - Então a plataforma deve registrar o e… | `backend/tests/test_audit.py:131` |
| `AC-AUDIT-06` | PDF | Paginação. - Dado uma requisição GET /api/audit - Quando o usuário enviar parâmetros skip e limit - Então a API deve retornar uma lista paginada e a contagem… | `backend/tests/test_audit.py:62` |
| `AC-AUDIT-07` | PDF | RBAC de Auditoria. - Dado um usuário com permissão AUDIT_READ (ex: ADMIN, AUDITOR) - Quando requisitar os eventos de auditoria - Então a lista deve ser retor… | `backend/tests/test_audit.py:56` |

## 16-remediation-workflow.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-REM-01` | PDF | Máquina de estados. Dado uma vulnerabilidade em qualquer status, Quando uma transição inválida for tentada, Entao a API responde 422 com detalhe da transição… | `backend/tests/test_remediation.py:28` |
| `AC-REM-02` | PDF | Transição válida. Dado uma vulnerabilidade NOVA, Quando movida para EM_ANALISE, Entao o status é salvo e o histórico registrado com autor e data. | `backend/tests/test_remediation.py:44` |
| `AC-REM-03` | PDF | Fluxo de correção completo. Dado uma vulnerabilidade EM_CORRECAO, Quando movida para AGUARDANDO_VALIDACAO, Entao o novo status é aceito. | `backend/tests/test_remediation.py:59` |
| `AC-REM-04` | PDF | Revalidação aprovada. Dado uma vulnerabilidade AGUARDANDO_VALIDACAO, Quando movida para CORRIGIDA, Entao o resolved_at é preenchido automaticamente. | `backend/tests/test_remediation.py:95` |
| `AC-REM-05` | PDF | Revalidação reprovada. Dado uma vulnerabilidade AGUARDANDO_VALIDACAO, Quando movida para EM_CORRECAO, Entao a transição é aceita e o histórico registrado. | `backend/tests/test_remediation.py:25`<br>`backend/tests/test_remediation.py:116` |
| `AC-REM-06` | PDF | Reabertura. Dado uma vulnerabilidade CORRIGIDA, Quando movida para EM_CORRECAO, Entao a transição é aceita e o resolved_at é limpo. | `backend/tests/test_remediation.py:136` |
| `AC-REM-07` | PDF | Owner/Assignee. Dado um usuário com finding:write, Quando chamar PATCH /{id}/owner, Entao o owner_id e owner_team são salvos e o assigned_at preenchido. | `backend/tests/test_remediation.py:160` |
| `AC-REM-08` | PDF | Owner sem permissão. Dado um usuário sem finding:write, Quando tentar PATCH /{id}/owner, Entao a API responde 403. | `backend/tests/test_remediation.py:173` |
| `AC-REM-09` | PDF | Comentário de remediação. Dado usuário autenticado com finding:read, Quando POST /{id}/comments com conteúdo, Entao o comentário é persistido com author_id e… | `backend/tests/test_remediation.py:57`<br>`backend/tests/test_remediation.py:192` |
| `AC-REM-10` | PDF | Listagem de comentários. Dado uma vulnerabilidade com comentários, Quando GET /{id}/comments, Entao todos os comentários são retornados em ordem cronológica. | `backend/tests/test_remediation.py:93`<br>`backend/tests/test_remediation.py:203` |
| `AC-REM-11` | PDF | Sanitização de comentários. Dado um comentário com token ou senha, Quando armazenado, Entao o conteúdo não é mascarado (é texto do usuário, não payload autom… | `backend/tests/test_remediation.py:214` |
| `AC-REM-12` | PDF | Evidência de correção. Dado usuário com finding:write, Quando POST /{id}/evidences com description e reference, Entao a evidência é persistida vinculada à vu… | `backend/tests/test_remediation.py:224` |
| `AC-REM-13` | PDF | Listagem de evidências. Dado uma vulnerabilidade com evidências, Quando GET /{id}/evidences, Entao todas as evidências são retornadas. | `backend/tests/test_remediation.py:247` |
| `AC-REM-14` | PDF | Falso positivo exige razão. Dado usuário com finding:close, Quando mudar status para FALSO_POSITIVO sem reason, Entao a API responde 422. | `backend/tests/test_remediation.py:260` |
| `AC-REM-15` | PDF | Falso positivo com razão. Dado usuário com finding:close, Quando mudar status para FALSO_POSITIVO com reason, Entao o status é salvo e false_positive_reason … | `backend/tests/test_remediation.py:271` |
| `AC-REM-16` | PDF | Aceitação de risco exige razão. Dado usuário com finding:close, Quando mudar status para ACEITO_COMO_RISCO sem reason, Entao a API responde 422. | `backend/tests/test_remediation.py:284` |
| `AC-REM-17` | PDF | Aceitação de risco com razão. Dado usuário com finding:close, Quando mudar status para ACEITO_COMO_RISCO com reason, Entao o status é salvo, risk_acceptance_… | `backend/tests/test_remediation.py:298` |
| `AC-REM-18` | PDF | Audit Log: status mudança. Dado qualquer mudança de status do workflow, Quando concluída, Entao o AuditLog registra actor, old_value, new_value e entity_id. | `backend/tests/test_remediation.py:313` |
| `AC-REM-19` | PDF | Audit Log: owner. Dado mudança de owner, Quando concluída, Entao o AuditLog registra ASSIGNMENT_CHANGED com o owner anterior e novo. | `backend/tests/test_remediation.py:325` |
| `AC-REM-20` | PDF | Audit Log: comentário. Dado adição de comentário, Quando concluída, Entao o AuditLog registra COMMENT_ADDED com o entity_id da vulnerabilidade. | `backend/tests/test_remediation.py:333` |
| `AC-REM-21` | PDF | Audit Log: evidência. Dado adição de evidência, Quando concluída, Entao o AuditLog registra EVIDENCE_ADDED. | `backend/tests/test_remediation.py:343` |
| `AC-REM-22` | PDF | RBAC comentários. Dado usuário sem autenticação, Quando POST /{id}/comments, Entao a API responde 401. | `backend/tests/test_remediation.py:355` |
| `AC-REM-23` | PDF | SLA: campos de tempo. Dado uma vulnerabilidade CORRIGIDA, Quando consultada, Entao os campos detected_at e resolved_at estão presentes no payload. | `backend/tests/test_remediation.py:360` |
| `AC-REM-24` | PDF | Novos status no vocabulário. Dado consulta às opções, Quando listados os status disponíveis, Entao AGUARDANDO_VALIDACAO e ACEITO_COMO_RISCO estão presentes. | `backend/tests/test_remediation.py:381` |
| `AC-REM-25` | PDF | Detalhe inclui owner e times. Dado uma vulnerabilidade com owner, Quando o detalhe for consultado, Entao owner_id, owner_team e assigned_at são retornados. | `backend/tests/test_remediation.py:388` |

## 17-sla.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-SLA-01` | PDF | Cálculo da data limite (Due Date). Dado que uma nova vulnerabilidade foi identificada, Quando o SLA for calculado, Entao a data limite deve seguir a política… | `backend/tests/test_sla.py:18` |
| `AC-SLA-02` | PDF | Transição para Due Soon. Dado uma vulnerabilidade com SLA ativo, Quando faltarem menos de N dias para o vencimento, Entao o status do SLA deve mudar para DUE… | `backend/tests/test_sla.py:25` |
| `AC-SLA-03` | PDF | Transição para Overdue (SLA Vencido). Dado uma vulnerabilidade aberta, Quando a data atual ultrapassar o Due Date, Entao o status do SLA deve mudar para OVER… | `backend/tests/test_sla.py:39` |
| `AC-SLA-04` | PDF | Resolução de SLA. Dado uma vulnerabilidade em correção, Quando o status mudar para CORRIGIDA, Entao o SLA deve ser marcado como RESOLVED e o tempo total gast… | `backend/tests/test_sla.py:51` |
| `AC-SLA-05` | PDF | Recálculo ao mudar Risco. Dado uma vulnerabilidade, Quando seu Risco for alterado (ex: Alta para Crítica), Entao a Due Date deve ser recalculada e o status d… | `backend/tests/test_sla.py:65` |
| `AC-SLA-06` | PDF | Estados de isenção e pausa. Dado que uma vulnerabilidade é marcada como FALSO_POSITIVO ou EXCECAO_TEMPORARIA, Entao o SLA deve ser considerado EXEMPT ou PAUS… | `backend/tests/test_sla.py:85` |
| `AC-SLA-07` | PDF | Scheduler identifica SLA vencido e gera evento sem duplicar. Dado o processo em background, Quando o SLA vencer, Entao um evento de auditoria deve ser gerado… | `backend/tests/test_sla.py:101` |

## 19-supply-chain-signatures.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-SC-01` | PDF | Dado que um artefato é submetido, quando for verificá-lo, então o sistema deve utilizar o seu digest (ex: sha256) como identidade forte. | `backend/tests/test_supply_chain.py:10`<br>`backend/tests/test_supply_chain.py:54` |
| `AC-SC-02` | PDF | Dado um artefato assinado (Keyless), quando solicitar verificação, então deve validar a assinatura contra a infraestrutura Sigstore (Rekor/Fulcio) e retornar… | `backend/tests/test_supply_chain.py:11`<br>`backend/tests/test_supply_chain.py:54` |
| `AC-SC-03` | PDF | Dado que a assinatura não existe ou é inválida, quando verificar, então signature_valid deve ser falso. | `backend/tests/test_supply_chain.py:12`<br>`backend/tests/test_supply_chain.py:69` |
| `AC-SC-04` | PDF | Dado que o artefato possui attestation in-toto, quando verificado pelo cosign, então o sistema deve registrar provenance_present e extrair o builder. | `backend/tests/test_supply_chain.py:13`<br>`backend/tests/test_supply_chain.py:54` |
| `AC-SC-05` | PDF | Dado que uma attestation existe, quando a assinatura da attestation for inválida, então provenance_valid deve ser falso. | `backend/tests/test_supply_chain.py:14`<br>`backend/tests/test_supply_chain.py:83` |
| `AC-SC-06` | PDF | Dado que a política exige assinatura (require_signature), quando a assinatura for inválida, então a política deve falhar e o Security Gate deve retornar BLOC… | `backend/tests/test_supply_chain.py:15`<br>`backend/tests/test_supply_chain.py:69` |
| `AC-SC-07` | PDF | Dado que a política exige um builder específico (trusted_builder), quando a proveniência não contiver esse builder, então a política deve falhar. | `backend/tests/test_supply_chain.py:16`<br>`backend/tests/test_supply_chain.py:83` |
| `AC-SC-08` | PDF | Dado que a verificação falhou em relação à política, quando gerar os resultados, então deve criar um AchadoNormalizado com a categoria SUPPLY_CHAIN e título … | `backend/tests/test_supply_chain.py:17`<br>`backend/tests/test_supply_chain.py:69` |
| `AC-SC-09` | PDF | Dado um finding de Supply Chain, quando ingerido pelo motor, então deve ser deduplicado com base no digest do artefato e na regra violada. | `backend/tests/test_supply_chain.py:18`<br>`backend/tests/test_supply_chain.py:69` |
| `AC-SC-10` | PDF | Dado que o Security Gate for executado para Supply Chain, quando processar um artefato em pipeline, então deve vincular a verificação ao PipelineRun. | `backend/tests/test_supply_chain.py:19` |
| `AC-SC-11` | PDF | Dado o início e fim da verificação de Supply Chain, quando ocorrer, então deve gerar os respectivos eventos no Audit Log (SUPPLY_CHAIN_VERIFICATION_STARTED, … | `backend/tests/test_supply_chain.py:20` |
| `AC-SC-12` | PDF | Dado que o sistema invoca o cosign, quando construir os argumentos, então não deve usar shell=True nem permitir injeção de comandos a partir da entrada do us… | `backend/tests/test_supply_chain.py:21`<br>`backend/tests/test_supply_chain.py:54` |
| `AC-SC-13` | PDF | Dado que o usuário visualiza os detalhes de um Container, quando este possuir verificações de Supply Chain, então a interface deve exibir o status da assinat… | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:162` |

## 20-runtime-ebpf.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-RT-01` | PDF | Ingestão e deduplicação de eventos. Dado um payload de evento de runtime recebido no webhook, Quando o sistema processá-lo, Então deve extrair container_id, … | `backend/tests/test_runtime.py:16` |
| `AC-RT-02` | PDF | Correlação de ameaças em execução (Reachability). Dado um evento contendo informações de execução (proc.name), Quando houver uma vulnerabilidade latente na m… | `backend/tests/test_runtime.py:58` |
| `AC-RT-03` | PDF | Selo visual de ameaça (Frontend). Dado uma vulnerabilidade que tenha achados correlacionados à ferramenta RUNTIME, Quando o usuário acessar a página de detal… | `frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx:37` |

## 21-cloud-cspm.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-CSPM-01` | PDF | Ingestão e deduplicação CSPM. Dado um payload de CSPM recebido no webhook, Quando o sistema processá-lo, Então deve extrair conta, recurso e detalhes do acha… | `backend/tests/test_cspm.py:13` |
| `AC-CSPM-02` | PDF | Toxic Combination na Nuvem. Dado um alerta de CSPM Crítico de exposição para internet recebido, Quando houver vulnerabilidade estática do tipo RCE na mesma a… | `backend/tests/test_cspm.py:58` |

## 22-observability.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-OBS-01` | PDF | Dado que uma requisição é feita para a plataforma Quando o backend processa o acesso Então deve inserir um request_id nos logs JSON estruturados | `backend/tests/test_observability.py:9` |
| `AC-OBS-02` | PDF | Dado que um middleware de telemetria está ativo Quando uma rota é completada Então o sistema deve incrementar o Prometheus counter com rota e status code | `backend/tests/test_observability.py:44` |
| `AC-OBS-03` | PDF | Dado que a aplicação possui telemetria Quando um usuário tenta acessar /metrics Então deve retornar dados Prometheus para ADMIN e HTTP 403 para os demais | `backend/tests/test_observability.py:16` |
| `AC-OBS-04` | PDF | Dado o sistema de health check Quando a rota /api/health é chamada Então deve atestar o banco de dados e retornar up ou HTTP 503 | `backend/tests/test_observability.py:36` |
| `AC-OBS-05` | PDF | Dado o frontend da plataforma Quando a tela "System Health" é acessada por admin Então deve consumir /health e mostrar métricas e volume | `frontend/src/pages/__tests__/Observability.test.tsx:16` |

## 23-multi-tenancy-sso.md

| AC | Origem | Critério | Testes |
|---|---|---|---|
| `AC-MT-01` | PDF | Dado que um usuário faz login via SSO Corporativo Quando o domínio do e-mail bater com o domain de um Tenant cadastrado Então o backend deve provisionar o us… | `backend/tests/test_multi_tenancy.py:11` |
| `AC-MT-02` | PDF | Dado que o banco de dados armazena aplicações, integrações e vulnerabilidades de múltiplos Tenants Quando um usuário autenticado no Tenant A acessar /api/v1/… | `backend/tests/test_multi_tenancy.py:31` |
| `AC-MT-03` | PDF | Dado um usuário com múltiplas associações na tabela TenantUser Quando ele acessar a interface web Então o frontend deve exibir um modal/seletor de Workspace … | `frontend/src/__tests__/MultiTenancy.test.tsx:8` |
| `AC-MT-04` | PDF | Dado uma base de dados legada sem tenant_id Quando o sistema for atualizado Então uma migration Alembic deve criar um "Default Organization" e migrar todos o… | `backend/tests/test_multi_tenancy.py:56` |

