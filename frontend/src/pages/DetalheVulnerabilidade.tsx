/**
 * DetalheVulnerabilidade.tsx — Tudo sobre um achado, e onde se age sobre ele.
 *
 * Reúne o que cada ferramenta reportou, por que aquele risco foi atribuído, a
 * explicação da IA e o histórico de tratamento.
 */
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { 
  criarTicket,
  gerarAnaliseIA, 
  mensagemDeErro,
  mudarStatus, 
  obterVulnerabilidade,
  sincronizarTicket,
  atribuirOwner,
  adicionarComentario,
  adicionarEvidencia,
} from '../api/client'
import type { Achado, StatusVulnerabilidade, VulnerabilidadeDetalhe as Detalhe } from '../api/types'
import {
  BadgeFerramenta,
  BadgeRisco,
  BadgeStatus,
  EtiquetaAmbiente,
  SeloCorrelacionada,
} from '../components/Badges'

import { Cartao, Carregando, Erro } from '../components/Feedback'
import { ContainerVerifications } from '../components/ContainerVerifications'
import { useRequisicao } from '../hooks/useRequisicao'
import { useAuth } from '../auth/useAuth'

const STATUS_DISPONIVEIS: { valor: StatusVulnerabilidade; label: string }[] = [
  { valor: 'nova', label: 'Nova' },
  { valor: 'em_analise', label: 'Em análise' },
  { valor: 'em_correcao', label: 'Em correção' },
  { valor: 'corrigida', label: 'Corrigida' },
  { valor: 'falso_positivo', label: 'Falso positivo' },
]

export function DetalheVulnerabilidade() {
  const { id } = useParams<{ id: string }>()
  const vulnId = Number(id)
  const { dados, carregando, erro, recarregar } = useRequisicao(
    () => obterVulnerabilidade(vulnId),
    [vulnId],
  )
  const [local, setLocal] = useState<Detalhe | null>(null)

  const vuln = local ?? dados

  if (carregando) return <Carregando />
  if (erro) return <Erro mensagem={erro} aoTentar={recarregar} />
  if (!vuln) return null

  return (
    <>
      <Link
        to="/vulnerabilidades"
        className="mb-4 inline-block text-sm text-slate-500 hover:text-slate-800 hover:underline"
      >
        ← Voltar para a lista
      </Link>

      <header className="mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-xl font-semibold uppercase text-slate-900">
            {vuln.tipo_vuln.replace(/_/g, ' ')}
          </h1>
          <BadgeRisco risco={vuln.risco} label={vuln.risco_label} />
          <BadgeStatus status={vuln.status} label={vuln.status_label} />
          {vuln.correlacionada && <SeloCorrelacionada />}
        </div>
        <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-500">
          <span className="font-mono">{vuln.endpoint}</span>
          <span>·</span>
          <span>{vuln.aplicacao_nome}</span>
          <EtiquetaAmbiente label={vuln.aplicacao_ambiente} />
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Cartao titulo="Por que este risco">
            <p className="text-sm leading-relaxed text-slate-700">{vuln.justificativa}</p>
            <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 text-sm sm:grid-cols-4">
              <Dado rotulo="Encontrada no Semgrep" valor={vuln.encontrada_semgrep ? 'sim' : 'não'} />
              <Dado rotulo="Confirmada pelo Nuclei" valor={vuln.confirmada_nuclei ? 'sim' : 'não'} />
              <Dado
                rotulo="Correlação"
                valor={vuln.correlacionada ? 'encontrada' : 'não encontrada'}
              />
              <Dado rotulo="Severidade original" valor={vuln.severidade_original ?? '—'} />
            </dl>
          </Cartao>

          <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
            {vuln.achados.map((achado) => (
              <Cartao key={achado.id} titulo={`Resultado de ${achado.origem_label}`}>
                <DetalheAchado achado={achado} />
              </Cartao>
            ))}
          </div>

          <PainelIA vulnerabilidade={vuln} aoAtualizar={setLocal} />
        </div>

        <div className="space-y-6">
          <PainelOwner vulnerabilidade={vuln} aoAtualizar={setLocal} />
          <PainelStatus vulnerabilidade={vuln} aoAtualizar={setLocal} />
          <PainelTickets vulnerabilidade={vuln} aoAtualizar={setLocal} />
          <PainelEvidencias vulnerabilidade={vuln} aoAtualizar={setLocal} />
          <PainelComentarios vulnerabilidade={vuln} aoAtualizar={setLocal} />

          <Cartao titulo="Histórico">
            <ol className="space-y-3">
              {vuln.historico.map((item) => (
                <li key={item.id} className="border-l-2 border-slate-200 pl-3 text-sm">
                  <p className="font-medium text-slate-700">
                    {item.status_anterior_label
                      ? `${item.status_anterior_label} → ${item.status_novo_label}`
                      : item.status_novo_label}
                  </p>
                  <p className="text-xs text-slate-400">
                    {new Date(item.criado_em).toLocaleString('pt-BR')}
                    {item.usuario_nome && ` · ${item.usuario_nome}`}
                  </p>
                  {item.comentario && (
                    <p className="mt-1 text-slate-600">{item.comentario}</p>
                  )}
                </li>
              ))}
            </ol>
          </Cartao>
        </div>
      </div>
    </>
  )
}

function Dado({ rotulo, valor }: { rotulo: string; valor: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-400">{rotulo}</dt>
      <dd className="mt-0.5 font-medium text-slate-700">{valor}</dd>
    </div>
  )
}



function DetalheAchado({ achado }: { achado: Achado }) {
  return (
    <div className="space-y-2 text-sm">
      <div className="flex items-center gap-2">
        <BadgeFerramenta nome={achado.origem_label} />
        <span className="text-slate-500">severidade {achado.severidade}</span>
      </div>

      <p className="font-mono text-xs break-all text-slate-600">{achado.regra_id}</p>

      {achado.arquivo && (
        <p className="text-slate-700">
          <span className="text-slate-400">Arquivo:</span>{' '}
          <span className="font-mono text-xs">
            {achado.arquivo}
            {achado.linha != null && `:${achado.linha}`}
          </span>
        </p>
      )}
      {achado.cwe && (
        <p className="text-slate-700">
          <span className="text-slate-400">CWE:</span> {achado.cwe}
        </p>
      )}
      {achado.repository && (
        <p className="text-slate-700">
          <span className="text-slate-400">Repositório:</span> {achado.repository}
        </p>
      )}
      {achado.commit && (
        <p className="text-slate-700">
          <span className="text-slate-400">Commit:</span>{' '}
          <span className="font-mono text-xs">{achado.commit}</span>
        </p>
      )}
      {achado.resource && (
        <p className="text-slate-700">
          <span className="text-slate-400">Recurso (IaC):</span>{' '}
          <span className="font-mono text-xs">{achado.resource}</span>
        </p>
      )}
      {achado.framework && (
        <p className="text-slate-700">
          <span className="text-slate-400">Framework (IaC):</span> {achado.framework}
        </p>
      )}
      {achado.guideline && (
        <p className="text-slate-700 break-all">
          <span className="text-slate-400">Guideline:</span>{' '}
          <a href={achado.guideline} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
            {achado.guideline}
          </a>
        </p>
      )}

      {/* Container Fields */}
      {achado.registry_name && (
        <p className="text-slate-700">
          <span className="text-slate-400">Registry:</span> {achado.registry_name}
        </p>
      )}
      {achado.image_repository && (
        <p className="text-slate-700">
          <span className="text-slate-400">Image Repository:</span> {achado.image_repository}
        </p>
      )}
      {achado.image_name && (
        <p className="text-slate-700">
          <span className="text-slate-400">Image Name:</span> {achado.image_name}
        </p>
      )}
      {achado.image_tag && (
        <p className="text-slate-700">
          <span className="text-slate-400">Image Tag:</span> {achado.image_tag}
        </p>
      )}
      {achado.image_digest && (
        <p className="text-slate-700">
          <span className="text-slate-400">Image Digest:</span> <span className="font-mono text-xs">{achado.image_digest}</span>
        </p>
      )}
      {achado.base_image && (
        <p className="text-slate-700">
          <span className="text-slate-400">Base Image:</span> {achado.base_image}
        </p>
      )}
      {achado.os && (
        <p className="text-slate-700">
          <span className="text-slate-400">OS:</span> {achado.os}
        </p>
      )}
      {achado.layer && (
        <p className="text-slate-700 break-all">
          <span className="text-slate-400">Layer:</span> <span className="font-mono text-xs">{achado.layer}</span>
        </p>
      )}
      {achado.pacote && (
        <p className="text-slate-700">
          <span className="text-slate-400">Package:</span> <span className="font-mono text-xs">{achado.pacote}</span>
        </p>
      )}
      {achado.versao && (
        <p className="text-slate-700">
          <span className="text-slate-400">Installed Version:</span> <span className="font-mono text-xs">{achado.versao}</span>
        </p>
      )}
      {achado.versao_corrigida && (
        <p className="text-slate-700">
          <span className="text-slate-400">Fixed Version:</span> <span className="font-mono text-xs">{achado.versao_corrigida}</span>
        </p>
      )}

      {achado.url && (
        <p className="break-all text-slate-700">
          <span className="text-slate-400">URL:</span>{' '}
          <span className="font-mono text-xs">{achado.url}</span>
        </p>
      )}
      {achado.http_status != null && (
        <p className="text-slate-700">
          <span className="text-slate-400">Status HTTP:</span> {achado.http_status}
        </p>
      )}
      {achado.evidencia && (
        <div>
          <p className="text-slate-400">Evidência:</p>
          <pre className="mt-1 overflow-x-auto rounded bg-slate-50 p-2 font-mono text-xs text-slate-700">
            {achado.evidencia}
          </pre>
        </div>
      )}

      {achado.image_name && <ContainerVerifications imageName={achado.image_name} />}
        <p className="border-t border-slate-100 pt-2 text-slate-600">{achado.mensagem}</p>
    </div>
  )
}

function PainelIA({
  vulnerabilidade,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (dados: Detalhe) => void
}) {
  const [gerando, setGerando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const analise = vulnerabilidade.analise_ia

  async function gerar() {
    setGerando(true)
    setErro(null)
    try {
      aoAtualizar(await gerarAnaliseIA(vulnerabilidade.id))
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível gerar a análise.'))
    } finally {
      setGerando(false)
    }
  }

  return (
    <Cartao
      titulo="Análise da IA"
      acao={
        <button
          type="button"
          onClick={gerar}
          disabled={gerando}
          className="rounded-md border border-violet-300 px-3 py-1 text-xs font-medium text-violet-700 transition hover:bg-violet-50 disabled:opacity-60"
        >
          {gerando ? 'Gerando…' : analise ? 'Gerar de novo' : 'Gerar explicação'}
        </button>
      }
    >
      {erro && (
        <p className="mb-3 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{erro}</p>
      )}

      {!analise ? (
        <p className="text-sm text-slate-500">
          A IA explica o problema, o impacto e como corrigir. Ela recebe o risco já
          classificado pelas regras do sistema e não participa dessa decisão. Dados
          sensíveis são mascarados antes do envio.
        </p>
      ) : (
        <div className="space-y-4 text-sm">
          <SecaoIA titulo="Explicação" texto={analise.explicacao} />
          <SecaoIA titulo="Impacto" texto={analise.impacto} />
          <SecaoIA titulo="Por que foi priorizado assim" texto={analise.priorizacao} />
          <SecaoIA titulo="Sugestão de correção" texto={analise.sugestao} />
          <SecaoIA titulo="Como validar" texto={analise.validacao} />
          {analise.descricao_ticket && (
            <div className="rounded-md bg-slate-50 p-3">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Descrição para ticket
              </p>
              <p className="whitespace-pre-line text-slate-700">{analise.descricao_ticket}</p>
            </div>
          )}
          {analise.gerada_em && (
            <p className="text-xs text-slate-400">
              Gerada em {new Date(analise.gerada_em).toLocaleString('pt-BR')}
            </p>
          )}
        </div>
      )}
    </Cartao>
  )
}

function SecaoIA({ titulo, texto }: { titulo: string; texto: string | null }) {
  if (!texto) return null
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
        {titulo}
      </p>
      <p className="leading-relaxed text-slate-700">{texto}</p>
    </div>
  )
}

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

function PainelTickets({
  vulnerabilidade: vuln,
  aoAtualizar,
}: {
  vulnerabilidade: Detalhe
  aoAtualizar: (v: Detalhe) => void
}) {
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const { usuario } = useAuth()
  const podeCriar = usuario?.permissions.includes('ticket:create')
  const podeSync = usuario?.permissions.includes('ticket:sync')
  
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
                {podeSync && (
                  <button
                    type="button"
                    onClick={() => sincronizar(t.id)}
                    disabled={carregando}
                    title="Sincronizar"
                    className="text-slate-400 hover:text-slate-600"
                  >
                    🔄
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-500 mb-4">Nenhum ticket associado.</p>
      )}

      {podeCriar && (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => criar('jira')}
            disabled={carregando}
            className="flex items-center gap-2 rounded bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-50"
          >
            ✨
            Criar no Jira
          </button>
        </div>
      )}
    </Cartao>
  )
}

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
      setErro(mensagemDeErro(e, 'Erro ao atribuir responsÃ¡vel'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Cartao titulo="ResponsÃ¡vel">
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
              AtribuÃ­do em {new Date(vuln.assigned_at).toLocaleString('pt-BR')}
            </p>
          )}
          {podeMudar && (
            <button
              onClick={() => setEditando(true)}
              className="mt-3 text-xs font-medium text-violet-600 hover:underline"
            >
              Alterar responsÃ¡vel
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3 text-sm">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">ID do UsuÃ¡rio</label>
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
              className="rounded bg-violet-600 px-3 py-1 text-xs font-medium text-white hover:bg-violet-700 
disabled:opacity-50"
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
      // Recarrega vulnerabilidade para trazer o comentÃ¡rio
      const atualizada = await obterVulnerabilidade(vuln.id)
      aoAtualizar(atualizada)
      setConteudo('')
    } catch (e: any) {
      setErro(mensagemDeErro(e, 'Erro ao adicionar comentÃ¡rio'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Cartao titulo="ComentÃ¡rios da RemediaÃ§Ã£o">
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
        <p className="mb-4 text-sm text-slate-500">Nenhum comentÃ¡rio registrado.</p>
      )}

      {podeComentar && (
        <div className="space-y-2">
          <textarea
            value={conteudo}
            onChange={(e) => setConteudo(e.target.value)}
            placeholder="Adicionar comentÃ¡rio..."
            rows={2}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none 
focus:border-violet-500"
          />
          {erro && <p className="text-xs text-rose-600">{erro}</p>}
          <button
            onClick={salvar}
            disabled={salvando || !conteudo.trim()}
            className="rounded bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200 
disabled:opacity-50"
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
      setErro(mensagemDeErro(e, 'Erro ao adicionar evidÃªncia'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Cartao titulo="EvidÃªncias de CorreÃ§Ã£o">
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
                <a href={e.reference} target="_blank" rel="noreferrer" className="mt-1 block text-xs text-blue-600 
hover:underline break-all">
                  {e.reference}
                </a>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mb-4 text-sm text-slate-500">Nenhuma evidÃªncia registrada.</p>
      )}

      {podeAdicionar && (
        <div className="space-y-2 rounded-md bg-slate-50 p-3 border border-slate-100">
          <p className="text-xs font-semibold text-slate-600 mb-2">Nova EvidÃªncia</p>
          <input
            type="text"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="DescriÃ§Ã£o (ex: Commit de correÃ§Ã£o)"
            className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-violet-500"
          />
          <input
            type="text"
            value={referencia}
            onChange={(e) => setReferencia(e.target.value)}
            placeholder="URL ou ReferÃªncia (opcional)"
            className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm outline-none focus:border-violet-500"
          />
          {erro && <p className="text-xs text-rose-600">{erro}</p>}
          <button
            onClick={salvar}
            disabled={salvando || !descricao.trim()}
            className="rounded bg-slate-200 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-300 
disabled:opacity-50"
          >
            {salvando ? 'Adicionando...' : 'Adicionar EvidÃªncia'}
          </button>
        </div>
      )}
    </Cartao>
  )
}


