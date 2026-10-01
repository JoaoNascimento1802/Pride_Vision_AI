const fs = require('fs');
let code = fs.readFileSync('backend/app/services/normalizer.py', 'utf-8');

const correct = `            achado = AchadoNormalizado(
                origem=Ferramenta.API_SECURITY,
                tipo_vuln=item.get("titulo", "API Security Finding"),
                endpoint=item.get("endpoint", ""),
                severidade=item.get("severidade", "medium"),
                mensagem=item.get("descricao", ""),
                regra_id=item.get("titulo", "API Security Finding"),
                evidencia=item.get("log", "")
            )`;

code = code.replace(/achado = AchadoNormalizado\([\s\S]*?origem=Ferramenta\.API_SECURITY\n            \)/, correct);
fs.writeFileSync('backend/app/services/normalizer.py', code, 'utf-8');
