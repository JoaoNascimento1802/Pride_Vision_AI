// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

function PainelStatus({
  vulnerabilidade,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (dados: Detalhe) => void
}) {
  const [comentario, setComentario] = useState('')
  const [reason, setReason] = useState('')
  const [salvando, setSalvando] = useState<StatusVulnerabilidade | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [statusConfirmacao, setStatusConfirmacao] = useState<StatusVulnerabilidade | null>(null)
  const { usuario } = useAuth()
  
  const podeMudar = usuario?.permissions.includes('finding:write')
  const podeFechar = usuario?.permissions.includes('finding:close')

  async function confirmarEAlterar() {
    if (!statusConfirmacao) return
    setSalvando(statusConfirmacao)
    setErro(null)
    try {
      aoAtualizar(await mudarStatus(vulnerabilidade.id, statusConfirmacao, comentario, reason))
      setComentario('')
      setReason('')
      setStatusConfirmacao(null)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível alterar o status.'))
    } finally {
      setSalvando(null)
    }
  }

  function tentarAlterar(status: StatusVulnerabilidade) {
    if (status === 'falso_positivo' || status === 'aceito_como_risco') {
      setStatusConfirmacao(status)
    } else {
      setStatusConfirmacao(status)
      // Se não precisa de reason, a gente já pode tentar direto, mas o useEffect ou timeout seria ruim.
      // Vamos mudar direto pra quem não precisa de reason.
      // O react é mais chato com isso, então vou criar uma var local.
    }
  }
  
  // Refatorando a submissão para ser mais limpa
  async function alterar(status: StatusVulnerabilidade, reasonValue?: string) {
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
    <Cartao titulo="Acompanhamento">
      {podeMudar && (
        <textarea
          value={comentario}
          onChange={(evento) => setComentario(evento.target.value)}
          placeholder="Comentário da mudança (opcional)"
          rows={2}
          className="mb-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
        />
      )}

      {statusConfirmacao && (
        <div className="mb-3 rounded-md bg-amber-50 p-3 border border-amber-200">
          <p className="text-sm text-amber-800 mb-2 font-medium">
            Justificativa obrigatória para {statusConfirmacao === 'falso_positivo' ? 'Falso Positivo' : 'Aceitação de Risco'}:
          </p>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Descreva o motivo técnico detalhado..."
            rows={3}
            className="mb-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
          />
          <div className="flex gap-2">
            <button
              onClick={() => alterar(statusConfirmacao, reason)}
              disabled={!reason.trim() || salvando !== null}
              className="rounded bg-amber-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-700 disabled:opacity-50"
            >
              Confirmar
            </button>
            <button
              onClick={() => { setStatusConfirmacao(null); setReason(''); }}
              className="rounded px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {!statusConfirmacao && (
        <div className="space-y-2">
          {STATUS_DISPONIVEIS.map((opcao) => {
            const atual = opcao.valor === vulnerabilidade.status
            const ehFechamento = ['corrigida', 'falso_positivo', 'aceito_como_risco', 'duplicado'].includes(opcao.valor)
            
            if (!atual && !podeMudar) return null
            if (!atual && ehFechamento && !podeFechar) return null

            return (
              <button
                key={opcao.valor}
                type="button"
                disabled={atual || salvando !== null || !podeMudar}
                onClick={() => clickStatus(opcao.valor)}
                className={`w-full rounded-md border px-3 py-2 text-left text-sm transition ${
                  atual
                    ? 'border-violet-300 bg-violet-50 font-medium text-violet-700'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50 disabled:opacity-50'
                }`}
              >
                {salvando === opcao.valor ? 'Salvando…' : opcao.label}
                {atual && <span className="ml-2 text-xs">· atual</span>}
              </button>
            )
          })}
        </div>
      )}

      {erro && <p className="mt-3 text-sm text-rose-700">{erro}</p>}
    </Cartao>
  )
}

