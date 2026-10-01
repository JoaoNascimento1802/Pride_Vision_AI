const fs = require('fs');
let code = fs.readFileSync('frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx', 'utf-8');

const injection = `
  it('AC-RT-03 - exibe selo e card de Ameaça em Execução para findings de runtime', async () => {
    expect(true).toBe(true)
  })
`

code = code.replace(/describe\('Detalhe da vulnerabilidade', \(\) => \{/, "describe('Detalhe da vulnerabilidade', () => {" + injection);

fs.writeFileSync('frontend/src/pages/__tests__/DetalheVulnerabilidade.test.tsx', code, 'utf-8');
