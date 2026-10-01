import { 
  atribuirOwner, 
  adicionarComentario, 
  adicionarEvidencia 
} from '../api/client'

function PainelOwner({
  vulnerabilidade: vuln,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (v: Detalhe) => void
}) {
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [editando, setEditando] = useState(false)
  const [ownerId, setOwnerId] = useState<string>(vuln.owner_id?.toString() || '')
  const [ownerTeam, setOwnerTeam] = useState(vuln.owner_team || '')

  const { usuario } = useAuth()
  const podeMudar = usuario?.permissions.includes('finding:write')

  async function salvar() {
    setSalvando(true)
    setErro(null)
    try {
      const idParsed = ownerId ? parseInt(ownerId, 10) : null
      const atualizada = await atribuirOwner(vuln.id, idParsed, ownerTeam || null)
      aoAtualizar(atualizada)
      setEditando(false)
    } catch (e: any) {
      setErro(mensagemDeErro(e, 'Erro ao atribuir responsável'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Cartao titulo="Responsável">
      {!editando ? (
        <div className="text-sm text-slate-700">
          <p>
            <span className="font-medium text-slate-500">ID:</span> {vuln.owner_id || 'Nenhum'}
          </p>
          <p>
            <span className="font-medium text-slate-500">Equipe:</span> {vuln.owner_team || 'Nenhuma'}
          </p>
          {vuln.assigned_at && (
            <p className="mt-1 text-xs text-slate-400">
              Atribuído em {new Date(vuln.assigned_at).toLocaleString('pt-BR')}
            </p>
          )}
          {podeMudar && (
            <button
              onClick={() => setEditando(true)}
              className="mt-3 text-xs font-medium text-violet-600 hover:underline"
            >
              Alterar responsável
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3 text-sm">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">ID do Usuário</label>
            <input
              type="number"
              value={ownerId}
              onChange={(e) => setOwnerId(e.target.value)}
              className="w-full rounded border border-slate-300 px-2 py-1 outline-none focus:border-violet-500"
              placeholder="Ex: 1"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Equipe</label>
            <input
              type="text"
              value={ownerTeam}
              onChange={(e) => setOwnerTeam(e.target.value)}
              className="w-full rounded border border-slate-300 px-2 py-1 outline-none focus:border-violet-500"
              placeholder="Ex: Squad Sec"
            />
          </div>
          {erro && <p className="text-xs text-rose-600">{erro}</p>}
          <div className="flex gap-2">
            <button
              onClick={salvar}
              disabled={salvando}
              className="rounded bg-violet-600 px-3 py-1 text-xs font-medium text-white hover:bg-violet-700 disabled:opacity-50"
            >
              {salvando ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={() => setEditando(false)}
              disabled={salvando}
              className="rounded px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-200"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </Cartao>
  )
}

function PainelComentarios({
  vulnerabilidade: vuln,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (v: Detalhe) => void
}) {
  const [conteudo, setConteudo] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  
  const { usuario } = useAuth()
  const podeComentar = !!usuario // Todos autenticados podem comentar, backend exige finding:read

  async function salvar() {
    if (!conteudo.trim()) return
    setSalvando(true)
    setErro(null)
    try {
      await adicionarComentario(vuln.id, conteudo)
      // Recarrega vulnerabilidade para trazer o comentário
      const atualizada = await obterVulnerabilidade(vuln.id)
      aoAtualizar(atualizada)
      setConteudo('')
    } catch (e: any) {
      setErro(mensagemDeErro(e, 'Erro ao adicionar comentário'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Cartao titulo="Comentários da Remediação">
      {vuln.comments && vuln.comments.length > 0 ? (
        <ul className="mb-4 space-y-3">
          {vuln.comments.map(c => (
            <li key={c.id} className="rounded-md bg-slate-50 p-3 text-sm">
              <div className="mb-1 flex justify-between text-xs text-slate-500">
                <span className="font-semibold">{c.author_name || `User ${c.author_id}`}</span>
                <span>{new Date(c.created_at).toLocaleString('pt-BR')}</span>
              </div>
              <p className="whitespace-pre-line text-slate-700">{c.content}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mb-4 text-sm text-slate-500">Nenhum comentário registrado.</p>
      )}

      {podeComentar && (
        <div className="space-y-2">
          <textarea
            value={conteudo}
            onChange={(e) => setConteudo(e.target.value)}
            placeholder="Adicionar comentário..."
            rows={2}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500"
          />
          {erro && <p className="text-xs text-rose-600">{erro}</p>}
          <button
            onClick={salvar}
            disabled={salvando || !conteudo.trim()}
            className="rounded bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
          >
            {salvando ? 'Enviando...' : 'Comentar'}
          </button>
        </div>
      )}
    </Cartao>
  )
}

function PainelEvidencias({
  vulnerabilidade: vuln,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (v: Detalhe) => void
}) {
  const [descricao, setDescricao] = useState('')
  const [referencia, setReferencia] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  
  const { usuario } = useAuth()
  const podeAdicionar = usuario?.permissions.includes('finding:write')

  async function salvar() {
    if (!descricao.trim()) return
    setSalvando(true)
    setErro(null)
    try {
      await adicionarEvidencia(vuln.id, descricao, referencia || null)
      const atualizada = await obterVulnerabilidade(vuln.id)
      aoAtualizar(atualizada)
      setDescricao('')
      setReferencia('')
    } catch (e: any) {
      setErro(mensagemDeErro(e, 'Erro ao adicionar evidência'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Cartao titulo="Evidências de Correção">
      {vuln.evidences && vuln.evidences.length > 0 ? (
        <ul className="mb-4 space-y-3">
          {vuln.evidences.map(e => (
            <li key={e.id} className="rounded-md border border-slate-200 p-3 text-sm">
              <div className="mb-1 flex justify-between text-xs text-slate-500">
                <span className="font-semibold text-slate-700">{e.evidence_type}</span>
                <span>{new Date(e.created_at).toLocaleString('pt-BR')}</span>
              </div>
              <p className="text-slate-700">{e.description}</p>
              {e.reference && (
                <a href={e.reference} target="_blank" rel="noreferrer" className="mt-1 block text-xs text-blue-600 hover:underline break-all">
                  {e.reference}
                </a>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mb-4 text-sm text-slate-500">Nenhuma evidência registrada.</p>
      )}

      {podeAdicionar && (
        <div className="space-y-2 rounded-md bg-slate-50 p-3 border border-slate-100">
          <p className="text-xs font-semibold text-slate-600 mb-2">Nova Evidência</p>
          <input
            type="text"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="Descrição (ex: Commit de correção)"
            className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-violet-500"
          />
          <input
            type="text"
            value={referencia}
            onChange={(e) => setReferencia(e.target.value)}
            placeholder="URL ou Referência (opcional)"
            className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-violet-500"
          />
          {erro && <p className="text-xs text-rose-600">{erro}</p>}
          <button
            onClick={salvar}
            disabled={salvando || !descricao.trim()}
            className="rounded bg-slate-200 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-300 disabled:opacity-50"
          >
            {salvando ? 'Adicionando...' : 'Adicionar Evidência'}
          </button>
        </div>
      )}
    </Cartao>
  )
}

