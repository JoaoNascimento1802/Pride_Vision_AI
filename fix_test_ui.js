const fs = require('fs');
let text = fs.readFileSync('frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx', 'utf-8');

text = text.replace("expect(mudarStatusMock).toHaveBeenCalledWith(DETALHE.id, 'em_correcao', '')", "expect(mudarStatusMock).toHaveBeenCalledWith(DETALHE.id, 'em_correcao', '', undefined)");

fs.writeFileSync('frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx', text, 'utf-8');
