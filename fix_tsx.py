# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import os

with open('frontend/src/pages/DetalheVulnerabilidade.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if 'async function alterar(status: StatusVulnerabilidade' in line:
        start = i
        break

for i in range(start, len(lines)):
    if 'function PainelTickets({' in lines[i]:
        end = i
        break

new_block = """  async function alterar(status: StatusVulnerabilidade, reasonValue?: string) {
    setSalvando(status)
    setErro(null)
    try {
      aoAtualizar(await mudarStatus(vulnerabilidade.id, status, comentario, reasonValue))
      setComentario('')
      setReason('')
      setStatusConfirmacao(null)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível alterar o status.'))
    } finally {
      setSalvando(null)
    }
  }

  function clickStatus(status: StatusVulnerabilidade) {
    if (status === 'falso_positivo' || status === 'aceito_como_risco') {
      setStatusConfirmacao(status)
    } else {
      alterar(status)
    }
  }

  return (
    <Cartao titulo=\"Acompanhamento\">
      {podeMudar && (
        <textarea
          value={comentario}
          onChange={(evento) => setComentario(evento.target.value)}
          placeholder=\"Comentário da mudança (opcional)\"
          rows={2}
          className=\"mb-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200\"
        />
      )}

      {statusConfirmacao && (
        <div className=\"mb-3 rounded-md bg-amber-50 p-3 border border-amber-200\">
          <p className=\"text-sm text-amber-800 mb-2 font-medium\">
            Justificativa obrigatória para {statusConfirmacao === 'falso_positivo' ? 'Falso Positivo' : 'Aceitação de Risco'}:
          </p>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder=\"Descreva o motivo técnico detalhado...\"
            rows={3}
            className=\"mb-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500\"
          />
          <div className=\"flex gap-2\">
            <button
              onClick={() => alterar(statusConfirmacao, reason)}
              disabled={!reason.trim() || salvando !== null}
              className=\"rounded bg-amber-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-700 disabled:opacity-50\"
            >
              {salvando === statusConfirmacao ? 'Salvando...' : 'Confirmar'}
            </button>
            <button
              onClick={() => { setStatusConfirmacao(null); setReason(''); }}
              className=\"rounded px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200\"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {!statusConfirmacao && (
        <div className=\"space-y-2\">
          {STATUS_DISPONIVEIS.map((opcao) => {
            const atual = opcao.valor === vulnerabilidade.status
            const ehFechamento = ['corrigida', 'falso_positivo', 'aceito_como_risco', 'duplicado'].includes(opcao.valor)
            
            if (!atual && !podeMudar) return null
            if (!atual && ehFechamento && !podeFechar) return null

            return (
              <button
                key={opcao.valor}
                type=\"button\"
                disabled={atual || salvando !== null || !podeMudar}
                onClick={() => clickStatus(opcao.valor)}
                className={`w-full rounded-md border px-3 py-2 text-left text-sm transition ${
                  atual
                    ? 'border-violet-300 bg-violet-50 font-medium text-violet-700'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50 disabled:opacity-50'
                }`}
              >
                {salvando === opcao.valor ? 'Salvando...' : opcao.label}
                {atual && <span className=\"ml-2 text-xs\">— atual</span>}
              </button>
            )
          })}
        </div>
      )}

      {erro && <p className=\"mt-3 text-sm text-rose-700\">{erro}</p>}
    </Cartao>
  )
}

"""

new_lines = lines[:start] + [new_block] + lines[end:]

with open('frontend/src/pages/DetalheVulnerabilidade.tsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Fixed!')

