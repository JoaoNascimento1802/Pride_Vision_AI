const fs = require('fs');
let code = fs.readFileSync('frontend/src/pages/DetalheVulnerabilidade.tsx', 'utf-8');

const targetAchado = `{achado.cwe && (
        <p className="text-slate-700">
          <span className="text-slate-400">CWE:</span> {achado.cwe}
        </p>
      )}`;

const replacementAchado = `{achado.cwe && (
        <p className="text-slate-700">
          <span className="text-slate-400">CWE:</span> {achado.cwe}
        </p>
      )}
      
      {achado.origem === 'runtime' && (
        <div className="mt-2 p-3 bg-red-50 border border-red-100 rounded-md">
          <p className="text-red-800 font-semibold mb-1 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            Ameaça em Execução (Runtime)
          </p>
          <p className="text-red-700 text-xs font-mono">Processo: {achado.process_name}</p>
          {achado.syscall && <p className="text-red-700 text-xs font-mono">Syscall: {achado.syscall}</p>}
          <p className="text-red-700 text-xs font-mono">Container: {achado.container_id}</p>
          <p className="text-red-700 text-xs font-mono mt-1 pt-1 border-t border-red-200">
            Contagem: {achado.hit_count} hits (Último: {achado.last_seen_at ? new Date(achado.last_seen_at).toLocaleString() : 'N/A'})
          </p>
        </div>
      )}`;

code = code.replace(targetAchado, replacementAchado);

const targetBadge = `<div className="flex flex-wrap items-center gap-3">
          <BadgeRisco risco={vuln.risco} />
          <BadgeStatus status={vuln.status} />`;
          
const replacementBadge = `<div className="flex flex-wrap items-center gap-3">
          <BadgeRisco risco={vuln.risco} />
          <BadgeStatus status={vuln.status} />
          {vuln.achados.some(a => a.origem === 'runtime') && (
            <span className="inline-flex items-center gap-1.5 rounded bg-red-600 px-2.5 py-1 text-xs font-bold text-white shadow-sm ring-1 ring-inset ring-red-700/20">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
              REACHABLE
            </span>
          )}`;

code = code.replace(targetBadge, replacementBadge);

fs.writeFileSync('frontend/src/pages/DetalheVulnerabilidade.tsx', code, 'utf-8');
