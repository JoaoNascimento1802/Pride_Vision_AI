import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Shield,
  Server,
  FileText,
  Activity,
  History,
  User,
  MessageSquare,
  Link as LinkIcon,
  CheckCircle,
  AlertTriangle,
  Plus,
  RefreshCw,
  Cpu,
  Ticket
} from 'lucide-react'

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

import { Carregando, Erro } from '../components/Feedback'
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

function Card({ titulo, acao, icone: Icon, children }: { titulo: string; acao?: React.ReactNode; icone?: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-6">
      <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
        <h3 className="text-lg font-medium text-slate-900 flex items-center gap-2">
          {Icon && <Icon className="w-5 h-5 text-indigo-600" />}
          {titulo}
        </h3>
        {acao && <div>{acao}</div>}
      </div>
      <div className="p-6">{children}</div>
    </div>
  )
}

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
    <div className="min-h-screen bg-slate-50 p-6">
      <Link
        to="/vulnerabilidades"
        className="mb-4 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-indigo-600 hover:underline transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar para a lista
      </Link>

      <header className="mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold uppercase text-slate-900 flex items-center gap-2">
            <Shield className="w-7 h-7 text-indigo-600" />
            {vuln.tipo_vuln.replace(/_/g, ' ')}
          </h1>
          <BadgeRisco risco={vuln.risco} label={vuln.risco_label} />
          <BadgeStatus status={vuln.status} label={vuln.status_label} />
          {vuln.correlacionada && <SeloCorrelacionada />}
        </div>
        <p className="mt-3 flex flex-wrap items-center gap-2 text-sm text-slate-600 bg-white inline-flex px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
          <Server className="w-4 h-4 text-slate-400" />
          <span className="font-mono text-slate-700">{vuln.endpoint}</span>
          <span className="text-slate-300">|</span>
          <span className="font-medium text-slate-700">{vuln.aplicacao_nome}</span>
          <EtiquetaAmbiente label={vuln.aplicacao_ambiente} />
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card titulo="Visão Geral do Risco" icone={AlertTriangle}>
            <p className="text-sm leading-relaxed text-slate-700">{vuln.justificativa}</p>
            <dl className="mt-4 grid grid-cols-2 gap-4 border-t border-slate-100 pt-4 text-sm sm:grid-cols-4">
              <Dado rotulo="Encontrada no Semgrep" valor={vuln.encontrada_semgrep ? 'Sim' : 'Não'} />
              <Dado rotulo="Confirmada pelo Nuclei" valor={vuln.confirmada_nuclei ? 'Sim' : 'Não'} />
              <Dado
                rotulo="Correlação"
                valor={vuln.correlacionada ? 'Encontrada' : 'Não encontrada'}
              />
              <Dado rotulo="Severidade Original" valor={vuln.severidade_original ?? '—'} />
            </dl>
          </Card>

          <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
            {vuln.achados.map((achado) => (
              <Card key={achado.id} titulo={`Resultado: ${achado.origem_label}`} icone={FileText}>
                <DetalheAchado achado={achado} />
              </Card>
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

          <Card titulo="Histórico" icone={History}>
            <ol className="space-y-4">
              {vuln.historico.map((item, index) => (
                <li key={item.id} className="relative pl-4">
                  {index !== vuln.historico.length - 1 && (
                    <div className="absolute left-[7px] top-5 bottom-[-16px] w-[2px] bg-slate-200" />
                  )}
                  <div className="absolute left-0 top-1.5 w-4 h-4 rounded-full border-2 border-indigo-600 bg-white" />
                  <div className="pl-2">
                    <p className="font-medium text-sm text-slate-700">
                      {item.status_anterior_label
                        ? `${item.status_anterior_label} → ${item.status_novo_label}`
                        : item.status_novo_label}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(item.criado_em).toLocaleString('pt-BR')}
                      {item.usuario_nome && ` · ${item.usuario_nome}`}
                    </p>
                    {item.comentario && (
                      <p className="mt-2 text-sm text-slate-600 bg-slate-50 p-2 rounded-md border border-slate-100">{item.comentario}</p>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </Card>
        </div>
      </div>
    </div>
  )
}

function Clock({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
  )
}

function Dado({ rotulo, valor }: { rotulo: string; valor: string }) {
  return (
    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
      <dt className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">{rotulo}</dt>
      <dd className="font-medium text-slate-900">{valor}</dd>
    </div>
  )
}

function DetalheAchado({ achado }: { achado: Achado }) {
  return (
    <div className="space-y-3 text-sm">
      <div className="flex items-center gap-2 mb-3">
        <BadgeFerramenta nome={achado.origem_label} />
        <span className="text-slate-500 bg-white px-2 py-0.5 rounded text-xs border border-slate-200">Severidade {achado.severidade}</span>
      </div>

      <p className="font-mono text-xs break-all text-indigo-700 bg-indigo-50 p-2 rounded-md border border-indigo-100">{achado.regra_id}</p>

      <div className="space-y-2 mt-3 divide-y divide-slate-100">
        {achado.arquivo && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Arquivo</span>
            <span className="font-mono text-xs text-right break-all ml-4">
              {achado.arquivo}
              {achado.linha != null && `:${achado.linha}`}
            </span>
          </p>
        )}
        {achado.cwe && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">CWE</span>
            <span className="text-right">{achado.cwe}</span>
          </p>
        )}
        {achado.repository && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Repositório</span>
            <span className="text-right font-medium">{achado.repository}</span>
          </p>
        )}
        {achado.commit && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Commit</span>
            <span className="font-mono text-xs text-right break-all ml-4">{achado.commit}</span>
          </p>
        )}
        {achado.resource && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Recurso (IaC)</span>
            <span className="font-mono text-xs text-right break-all ml-4">{achado.resource}</span>
          </p>
        )}
        {achado.framework && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Framework (IaC)</span>
            <span className="text-right">{achado.framework}</span>
          </p>
        )}
        {achado.guideline && (
          <p className="py-2 text-slate-700 flex flex-col gap-1">
            <span className="text-slate-500 font-medium">Guideline</span>
            <a href={achado.guideline} target="_blank" rel="noreferrer" className="text-indigo-600 hover:text-indigo-800 hover:underline break-all flex items-center gap-1">
              <LinkIcon className="w-3 h-3" /> {achado.guideline}
            </a>
          </p>
        )}
        {achado.registry_name && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Registry</span>
            <span className="text-right">{achado.registry_name}</span>
          </p>
        )}
        {achado.image_repository && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Image Repository</span>
            <span className="text-right">{achado.image_repository}</span>
          </p>
        )}
        {achado.image_name && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Image Name</span>
            <span className="text-right">{achado.image_name}</span>
          </p>
        )}
        {achado.image_tag && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Image Tag</span>
            <span className="text-right">{achado.image_tag}</span>
          </p>
        )}
        {achado.image_digest && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Image Digest</span>
            <span className="font-mono text-xs text-right break-all ml-4">{achado.image_digest}</span>
          </p>
        )}
        {achado.base_image && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Base Image</span>
            <span className="text-right">{achado.base_image}</span>
          </p>
        )}
        {achado.os && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">OS</span>
            <span className="text-right">{achado.os}</span>
          </p>
        )}
        {achado.layer && (
          <p className="py-2 text-slate-700 flex flex-col gap-1">
            <span className="text-slate-500 font-medium">Layer</span>
            <span className="font-mono text-xs break-all text-slate-600 bg-slate-50 p-2 rounded">{achado.layer}</span>
          </p>
        )}
        {achado.pacote && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Pacote</span>
            <span className="font-mono text-xs text-right">{achado.pacote}</span>
          </p>
        )}
        {achado.versao && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Versão Instalada</span>
            <span className="font-mono text-xs text-right">{achado.versao}</span>
          </p>
        )}
        {achado.versao_corrigida && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Versão Corrigida</span>
            <span className="font-mono text-xs text-right text-emerald-600 font-bold">{achado.versao_corrigida}</span>
          </p>
        )}
        {achado.url && (
          <p className="py-2 text-slate-700 flex flex-col gap-1">
            <span className="text-slate-500 font-medium">URL</span>
            <span className="font-mono text-xs break-all text-indigo-600">{achado.url}</span>
          </p>
        )}
        {achado.http_status != null && (
          <p className="py-2 text-slate-700 flex justify-between">
            <span className="text-slate-500 font-medium">Status HTTP</span>
            <span className="text-right font-mono">{achado.http_status}</span>
          </p>
        )}
        {achado.evidencia && (
          <div className="py-2">
            <p className="text-slate-500 font-medium mb-1">Evidência</p>
            <pre className="overflow-x-auto rounded-lg bg-slate-800 p-3 font-mono text-xs text-slate-50 shadow-inner">
              {achado.evidencia}
            </pre>
          </div>
        )}
      </div>

      {achado.image_name && <ContainerVerifications imageName={achado.image_name} />}
      <p className="border-t border-slate-100 pt-3 mt-3 text-slate-600 leading-relaxed bg-slate-50/50 p-3 rounded-lg">{achado.mensagem}</p>
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
    <Card
      titulo="Análise da IA"
      icone={Cpu}
      acao={
        <button
          type="button"
          onClick={gerar}
          disabled={gerando}
          className="flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white transition-all duration-200 hover:bg-indigo-700 hover:shadow-md disabled:opacity-60"
        >
          {gerando ? (
            <><RefreshCw className="w-3 h-3 animate-spin" /> Gerando...</>
          ) : analise ? (
            <><RefreshCw className="w-3 h-3" /> Gerar Novamente</>
          ) : (
            <><Cpu className="w-3 h-3" /> Gerar Explicação</>
          )}
        </button>
      }
    >
      {erro && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
          <AlertTriangle className="w-4 h-4" />
          {erro}
        </div>
      )}

      {!analise ? (
        <div className="text-center p-6 bg-slate-50 rounded-lg border border-slate-100 border-dashed">
          <Cpu className="w-8 h-8 text-indigo-300 mx-auto mb-3" />
          <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
            A IA explica o problema, o impacto e como corrigir. Ela recebe o risco já
            classificado pelas regras do sistema e não participa dessa decisão. Dados
            sensíveis são mascarados antes do envio.
          </p>
        </div>
      ) : (
        <div className="space-y-5 text-sm">
          <SecaoIA titulo="Explicação" texto={analise.explicacao} />
          <SecaoIA titulo="Impacto" texto={analise.impacto} />
          <SecaoIA titulo="Por que foi priorizado assim" texto={analise.priorizacao} />
          <SecaoIA titulo="Sugestão de Correção" texto={analise.sugestao} />
          <SecaoIA titulo="Como Validar" texto={analise.validacao} />
          
          {analise.descricao_ticket && (
            <div className="rounded-lg bg-indigo-50 p-4 border border-indigo-100">
              <p className="mb-2 text-xs font-bold uppercase tracking-wider text-indigo-800 flex items-center gap-1">
                <Ticket className="w-3 h-3" /> Descrição para Ticket
              </p>
              <p className="whitespace-pre-line text-indigo-900 leading-relaxed font-medium">{analise.descricao_ticket}</p>
            </div>
          )}
          {analise.gerada_em && (
            <p className="text-xs text-slate-400 text-right italic">
              Gerada em {new Date(analise.gerada_em).toLocaleString('pt-BR')}
            </p>
          )}
        </div>
      )}
    </Card>
  )
}

function SecaoIA({ titulo, texto }: { titulo: string; texto: string | null }) {
  if (!texto) return null
  return (
    <div className="bg-white p-4 rounded-lg border border-slate-100 shadow-sm">
      <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
        <CheckCircle className="w-3 h-3 text-indigo-500" /> {titulo}
      </h4>
      <p className="leading-relaxed text-slate-700 whitespace-pre-line">{texto}</p>
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
    <Card titulo="Acompanhamento" icone={Activity}>
      {podeMudar && (
        <textarea
          value={comentario}
          onChange={(evento) => setComentario(evento.target.value)}
          placeholder="Comentário da mudança (opcional)"
          rows={2}
          className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-shadow"
        />
      )}

      {statusConfirmacao && (
        <div className="mb-4 rounded-lg bg-amber-50 p-4 border border-amber-200 shadow-sm">
          <p className="text-sm text-amber-800 mb-3 font-semibold flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            Justificativa obrigatória para {statusConfirmacao === 'falso_positivo' ? 'Falso Positivo' : 'Aceitação de Risco'}:
          </p>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Descreva o motivo técnico detalhado..."
            rows={3}
            className="mb-3 w-full rounded-md border border-amber-300 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-200 bg-white"
          />
          <div className="flex gap-2">
            <button
              onClick={() => alterar(statusConfirmacao, reason)}
              disabled={!reason.trim() || salvando !== null}
              className="rounded-lg bg-amber-600 px-4 py-2 text-xs font-semibold text-white hover:bg-amber-700 hover:shadow-md transition-all disabled:opacity-50"
            >
              Confirmar
            </button>
            <button
              onClick={() => { setStatusConfirmacao(null); setReason(''); }}
              className="rounded-lg px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 transition-all"
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
                className={`w-full flex justify-between items-center rounded-lg border px-4 py-3 text-left text-sm font-medium transition-all duration-200 ${
                  atual
                    ? 'border-indigo-300 bg-indigo-50 text-indigo-700 shadow-sm ring-1 ring-indigo-300'
                    : 'border-slate-200 text-slate-700 bg-white hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 disabled:opacity-50 disabled:hover:bg-white disabled:hover:border-slate-200 disabled:hover:text-slate-700'
                }`}
              >
                <span>{salvando === opcao.valor ? 'Salvando…' : opcao.label}</span>
                {atual && <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-bold">Atual</span>}
              </button>
            )
          })}
        </div>
      )}

      {erro && (
        <div className="mt-4 flex items-center gap-1 text-sm text-red-600 bg-red-50 p-2 rounded-lg border border-red-100">
          <AlertTriangle className="w-4 h-4" /> {erro}
        </div>
      )}
    </Card>
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
    <Card titulo="Tickets e Remediação" icone={Ticket}>
      {erro && (
        <div className="mb-4 flex items-center gap-1 text-sm text-red-600 bg-red-50 p-2 rounded-lg border border-red-100">
          <AlertTriangle className="w-4 h-4" /> {erro}
        </div>
      )}
      
      {vuln.tickets && vuln.tickets.length > 0 ? (
        <div className="mb-4 overflow-hidden rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <tbody className="divide-y divide-slate-200 bg-white">
              {vuln.tickets.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <a href={t.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-semibold text-indigo-600 hover:text-indigo-800 hover:underline">
                          {t.external_key || t.external_id} <LinkIcon className="w-3 h-3" />
                        </a>
                        <p className="text-slate-700 mt-1 font-medium">{t.title}</p>
                        <p className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                          Status: <span className="uppercase font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">{t.status}</span>
                        </p>
                      </div>
                      {podeSync && (
                        <button
                          type="button"
                          onClick={() => sincronizar(t.id)}
                          disabled={carregando}
                          title="Sincronizar"
                          className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors disabled:opacity-50"
                        >
                          <RefreshCw className={`w-4 h-4 ${carregando ? 'animate-spin' : ''}`} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center p-4 bg-slate-50 rounded-lg border border-slate-100 border-dashed mb-4">
          <p className="text-sm text-slate-500">Nenhum ticket associado.</p>
        </div>
      )}

      {podeCriar && (
        <button
          type="button"
          onClick={() => criar('jira')}
          disabled={carregando}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-white border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-indigo-600 hover:border-indigo-300 transition-all shadow-sm disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          Criar no Jira
        </button>
      )}
    </Card>
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
      setErro(mensagemDeErro(e, 'Erro ao atribuir responsável'))
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Card titulo="Responsável" icone={User}>
      {!editando ? (
        <div className="text-sm">
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 space-y-2">
            <p className="flex justify-between items-center">
              <span className="font-semibold text-slate-500 text-xs uppercase tracking-wide">ID do Usuário</span> 
              <span className="font-medium text-slate-900">{vuln.owner_id || 'Nenhum'}</span>
            </p>
            <div className="border-t border-slate-200" />
            <p className="flex justify-between items-center">
              <span className="font-semibold text-slate-500 text-xs uppercase tracking-wide">Equipe</span> 
              <span className="font-medium text-slate-900">{vuln.owner_team || 'Nenhuma'}</span>
            </p>
          </div>
          
          {vuln.assigned_at && (
            <p className="mt-3 text-xs text-slate-400 text-center flex items-center justify-center gap-1">
              <Clock className="w-3 h-3" /> Atribuído em {new Date(vuln.assigned_at).toLocaleString('pt-BR')}
            </p>
          )}
          {podeMudar && (
            <button
              onClick={() => setEditando(true)}
              className="mt-4 w-full rounded-lg bg-white border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-indigo-600 transition-all shadow-sm"
            >
              Alterar Responsável
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4 text-sm bg-slate-50 p-4 rounded-lg border border-slate-200">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">ID do Usuário</label>
            <input
              type="number"
              value={ownerId}
              onChange={(e) => setOwnerId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white"
              placeholder="Ex: 1"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">Equipe</label>
            <input
              type="text"
              value={ownerTeam}
              onChange={(e) => setOwnerTeam(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white"
              placeholder="Ex: Squad Sec"
            />
          </div>
          {erro && <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{erro}</p>}
          <div className="flex gap-2 pt-2">
            <button
              onClick={salvar}
              disabled={salvando}
              className="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 hover:shadow-md transition-all disabled:opacity-50"
            >
              {salvando ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={() => setEditando(false)}
              disabled={salvando}
              className="flex-1 rounded-lg px-4 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 transition-all"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </Card>
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
    <Card titulo="Comentários da Remediação" icone={MessageSquare}>
      {vuln.comments && vuln.comments.length > 0 ? (
        <ul className="mb-6 space-y-4">
          {vuln.comments.map((c) => (
            <li key={c.id} className="rounded-xl bg-slate-50 p-4 border border-slate-100 shadow-sm relative">
              <div className="absolute -left-2 -top-2 bg-indigo-100 rounded-full p-1 border-2 border-white">
                <User className="w-4 h-4 text-indigo-600" />
              </div>
              <div className="ml-2">
                <div className="mb-2 flex flex-col sm:flex-row sm:justify-between sm:items-center text-xs text-slate-500 gap-1">
                  <span className="font-bold text-slate-700 text-sm">{c.author_name || `User ${c.author_id}`}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(c.created_at).toLocaleString('pt-BR')}</span>
                </div>
                <p className="whitespace-pre-line text-slate-800 text-sm leading-relaxed">{c.content}</p>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-center p-4 bg-slate-50 rounded-lg border border-slate-100 border-dashed mb-6">
          <p className="text-sm text-slate-500">Nenhum comentário registrado.</p>
        </div>
      )}

      {podeComentar && (
        <div className="space-y-3 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <textarea
            value={conteudo}
            onChange={(e) => setConteudo(e.target.value)}
            placeholder="Adicionar comentário..."
            rows={3}
            className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all resize-none"
          />
          {erro && <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{erro}</p>}
          <div className="flex justify-end">
            <button
              onClick={salvar}
              disabled={salvando || !conteudo.trim()}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700 hover:shadow-md transition-all disabled:opacity-50"
            >
              <MessageSquare className="w-4 h-4" />
              {salvando ? 'Enviando...' : 'Comentar'}
            </button>
          </div>
        </div>
      )}
    </Card>
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
    <Card titulo="Evidências de Correção" icone={CheckCircle}>
      {vuln.evidences && vuln.evidences.length > 0 ? (
        <div className="mb-6 overflow-hidden rounded-xl border border-slate-200 shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <tbody className="divide-y divide-slate-200 bg-white">
              {vuln.evidences.map((e) => (
                <tr key={e.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center text-xs text-slate-500 mb-2 gap-1">
                      <span className="font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-1 rounded-md">{e.evidence_type}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(e.created_at).toLocaleString('pt-BR')}</span>
                    </div>
                    <p className="text-slate-800 text-sm font-medium mb-1">{e.description}</p>
                    {e.reference && (
                      <a href={e.reference} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 hover:underline break-all mt-2 bg-indigo-50 px-2 py-1 rounded-md w-fit">
                        <LinkIcon className="w-3 h-3" /> {e.reference}
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center p-4 bg-slate-50 rounded-lg border border-slate-100 border-dashed mb-6">
          <p className="text-sm text-slate-500">Nenhuma evidência registrada.</p>
        </div>
      )}

      {podeAdicionar && (
        <div className="space-y-3 bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-inner">
          <p className="text-sm font-bold text-slate-700 mb-3 flex items-center gap-1 uppercase tracking-wide">
            <Plus className="w-4 h-4 text-indigo-600" /> Nova Evidência
          </p>
          <div>
            <input
              type="text"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              placeholder="Descrição (ex: Commit de correção)"
              className="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white"
            />
          </div>
          <div>
            <input
              type="text"
              value={referencia}
              onChange={(e) => setReferencia(e.target.value)}
              placeholder="URL ou Referência (opcional)"
              className="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white"
            />
          </div>
          {erro && <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{erro}</p>}
          <div className="pt-2">
            <button
              onClick={salvar}
              disabled={salvando || !descricao.trim()}
              className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 hover:shadow-md transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {salvando ? <><RefreshCw className="w-4 h-4 animate-spin" /> Adicionando...</> : <><CheckCircle className="w-4 h-4" /> Adicionar Evidência</>}
            </button>
          </div>
        </div>
      )}
    </Card>
  )
}
