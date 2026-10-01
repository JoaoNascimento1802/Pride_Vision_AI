from pathlib import Path

content = Path('frontend/src/pages/DetalheVulnerabilidade.tsx').read_text(encoding='utf-8')

painel = """
function PainelTickets({
  vulnerabilidade: vuln,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (v: Detalhe) => void
}) {
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  
  async function criar(provider: 'jira' | 'github' | 'gitlab' | 'azure_devops') {
    setCarregando(true)
    setErro(null)
    try {
      await criarTicket(vuln.id, provider)
      const atualizada = await obterVulnerabilidade(vuln.id)
      aoAtualizar(atualizada)
    } catch (e: any) {
      setErro(mensagemDeErro(e, 'Erro ao criar ticket'))
    } finally {
      setCarregando(false)
    }
  }

  async function sincronizar(ticketId: number) {
    setCarregando(true)
    setErro(null)
    try {
      await sincronizarTicket(vuln.id, ticketId)
      const atualizada = await obterVulnerabilidade(vuln.id)
      aoAtualizar(atualizada)
    } catch (e: any) {
      setErro(mensagemDeErro(e, 'Erro ao sincronizar ticket'))
    } finally {
      setCarregando(false)
    }
  }

  return (
    <Cartao titulo="Tickets e Remediação">
      {erro && <p className="mb-3 text-sm text-red-600">{erro}</p>}
      
      {vuln.tickets && vuln.tickets.length > 0 ? (
        <ul className="space-y-4 mb-4">
          {vuln.tickets.map(t => (
            <li key={t.id} className="text-sm border rounded p-3 bg-slate-50">
              <div className="flex justify-between items-start">
                <div>
                  <a href={t.url} target="_blank" rel="noreferrer" className="font-medium text-blue-600 hover:underline">
                    {t.external_key || t.external_id}
                  </a>
                  <p className="text-slate-600 mt-1">{t.title}</p>
                  <p className="text-xs text-slate-400 mt-2">Status: <span className="uppercase font-semibold">{t.status}</span></p>
                </div>
                <button
                  type="button"
                  onClick={() => sincronizar(t.id)}
                  disabled={carregando}
                  title="Sincronizar"
                  className="text-slate-400 hover:text-slate-600"
                >
                  <ArrowPathIcon className="w-4 h-4" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-500 mb-4">Nenhum ticket associado.</p>
      )}

      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => criar('jira')}
          disabled={carregando}
          className="flex items-center gap-2 rounded bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
        >
          <TicketIcon className="w-4 h-4" />
          Criar no Jira
        </button>
      </div>
    </Cartao>
  )
}
"""

content += painel
Path('frontend/src/pages/DetalheVulnerabilidade.tsx').write_text(content, encoding='utf-8')

