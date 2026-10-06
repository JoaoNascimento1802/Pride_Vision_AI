// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * Aplicacoes.tsx — Inventário e envio dos relatórios.
 *
 * O cadastro e o upload ficam juntos porque são um fluxo só: cadastrar uma
 * aplicação sem enviar relatório não produz nada de útil.
 */
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Edit2, Trash2, Eye, FileUp, Package } from 'lucide-react'

import {
  atualizarAplicacao,
  criarAplicacao,
  enviarRelatorio,
  enviarSbom,
  listarAplicacoes,
  listarUploads,
  mensagemDeErro,
  obterOpcoes,
  removerAplicacao,
} from '../api/client'
import type {
  AplicacaoNaLista,
  NovaAplicacao,
  ResultadoUpload,
  UploadResumo,
} from '../api/types'
import { BadgeFerramenta, EtiquetaAmbiente } from '../components/Badges'
import { Aviso, Carregando, Erro, Vazio } from '../components/Feedback'
import { TituloDaPagina } from '../components/Layout'
import { useRequisicao } from '../hooks/useRequisicao'
import { useAuth } from '../auth/useAuth'

export function Aplicacoes() {
  const lista = useRequisicao(listarAplicacoes, [])
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const { usuario } = useAuth()
  const podeEscrever = usuario?.permissions.includes('application:write')

  if (lista.carregando) return <Carregando />
  if (lista.erro) return <Erro mensagem={lista.erro} aoTentar={lista.recarregar} />
  if (!lista.dados) return null

  return (
    <>
      <TituloDaPagina
        titulo="Aplicações"
        descricao="Inventário com o contexto de negócio que define a prioridade das vulnerabilidades."
        acao={
          podeEscrever && (
            <button
              type="button"
              onClick={() => setMostrarFormulario((atual) => !atual)}
              className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-all duration-200 hover:bg-indigo-700 hover:shadow-md"
            >
              {mostrarFormulario ? 'Cancelar' : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Nova aplicação
                </>
              )}
            </button>
          )
        }
      />

      <div className="space-y-6">
        {mostrarFormulario && (
          <FormularioAplicacao
            aoCriar={() => {
              setMostrarFormulario(false)
              lista.recarregar()
            }}
          />
        )}

        {lista.dados.length === 0 ? (
          <Vazio
            titulo="Nenhuma aplicação cadastrada"
            descricao="Comece cadastrando a aplicação que você quer acompanhar. O ambiente e a exposição informados aqui definem o quanto cada vulnerabilidade pesa."
            acao={
              podeEscrever && (
                <button
                  type="button"
                  onClick={() => setMostrarFormulario(true)}
                  className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-all duration-200 hover:bg-indigo-700 hover:shadow-md"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Cadastrar primeira aplicação
                </button>
              )
            }
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {lista.dados.map((app) => (
              <CartaoAplicacao
                key={app.id}
                aplicacao={app}
                aoMudar={lista.recarregar}
              />
            ))}
          </div>
        )}
      </div>
    </>
  )
}

function CartaoAplicacao({
  aplicacao,
  aoMudar,
}: {
  aplicacao: AplicacaoNaLista
  aoMudar: () => void
}) {
  const [resultado, setResultado] = useState<ResultadoUpload | null>(null)
  const [erroUpload, setErroUpload] = useState<string | null>(null)
  const [enviando, setEnviando] = useState<string | null>(null)
  const [editando, setEditando] = useState(false)
  const [avisoReclassificacao, setAvisoReclassificacao] = useState<string | null>(null)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const uploads = useRequisicao(() => listarUploads(aplicacao.id), [aplicacao.id])

  const { usuario } = useAuth()
  const podeEscrever = usuario?.permissions.includes('application:write')

  async function enviar(ferramenta: 'semgrep' | 'nuclei' | 'trivy' | 'gitleaks' | 'checkov', arquivo: File) {
    setEnviando(ferramenta)
    setErroUpload(null)
    setResultado(null)
    try {
      setResultado(await enviarRelatorio(aplicacao.id, ferramenta, arquivo))
      uploads.recarregar()
      aoMudar()
    } catch (falha) {
      setErroUpload(mensagemDeErro(falha, 'Não foi possível processar o relatório.'))
    } finally {
      setEnviando(null)
    }
  }

  async function enviarArqSbom(arquivo: File) {
    setEnviando('sbom')
    setErroUpload(null)
    setResultado(null)
    try {
      const result = await enviarSbom(aplicacao.id, arquivo)
      alert(`SBOM importado com sucesso! ${result.componentes.length} componentes encontrados.`)
      aoMudar()
    } catch (e: any) {
      setErroUpload(mensagemDeErro(e, 'Erro ao enviar SBOM'))
    } finally {
      setEnviando(null)
    }
  }

  async function excluir() {
    if (!confirm(`Remover "${aplicacao.nome}" e todas as suas vulnerabilidades?`)) return
    await removerAplicacao(aplicacao.id)
    aoMudar()
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-6 transition-all hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-slate-900">{aplicacao.nome}</h3>
            <EtiquetaAmbiente label={aplicacao.ambiente_label} />
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {aplicacao.responsavel} · {aplicacao.exposicao_label} · importância{' '}
            {aplicacao.importancia_label.toLowerCase()}
            {aplicacao.url && ` · ${aplicacao.url}`}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm w-full sm:w-auto">
          <Contador rotulo="Total" valor={aplicacao.total_vulnerabilidades} />
          <Contador rotulo="Críticas" valor={aplicacao.total_criticas} alerta />
          <Contador rotulo="Abertas" valor={aplicacao.total_abertas} />
          <div className="flex items-center gap-2 w-full sm:w-auto mt-2 sm:mt-0">
            {aplicacao.total_vulnerabilidades > 0 && (
              <Link
                to={`/vulnerabilidades?aplicacao_id=${aplicacao.id}`}
                className="inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition-all duration-200 hover:bg-slate-50 hover:shadow-sm"
              >
                <Eye className="mr-1.5 h-3 w-3" />
                Ver
              </Link>
            )}
            <Link to={`/aplicacoes/${aplicacao.id}/sboms`} className="inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition-all duration-200 hover:bg-slate-50 hover:shadow-sm"><Package className="mr-1.5 h-3 w-3" />Ver SBOM</Link>{podeEscrever && (
              <>
                <button
                  type="button"
                  onClick={() => setEditando((atual) => !atual)}
                  className="inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition-all duration-200 hover:bg-slate-50 hover:shadow-sm"
                >
                  <Edit2 className="mr-1.5 h-3 w-3" />
                  {editando ? 'Cancelar' : 'Editar'}
                </button>
                <button
                  type="button"
                  onClick={excluir}
                  className="inline-flex items-center rounded-md px-2 py-1.5 text-xs text-slate-400 transition-all duration-200 hover:bg-rose-50 hover:text-rose-600"
                >
                  <Trash2 className="mr-1.5 h-3 w-3" />
                  Remover
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {editando && (
        <div className="mt-4 border-t border-slate-200 pt-4">
          <FormularioAplicacao
            aplicacao={aplicacao}
            aoSalvar={(mudouContexto) => {
              setEditando(false)
              if (mudouContexto) {
                setAvisoReclassificacao(
                  'Contexto de negócio alterado — as vulnerabilidades desta aplicação foram reclassificadas.',
                )
              }
              aoMudar()
            }}
          />
        </div>
      )}

      {avisoReclassificacao && (
        <p className="mt-3 rounded-md bg-sky-50 px-3 py-2 text-sm text-sky-800">
          {avisoReclassificacao}
        </p>
      )}

      <div className="mt-4 border-t border-slate-200 pt-4">
        <RelatoriosEmVigor uploads={uploads.dados} carregando={uploads.carregando} />

        {usuario?.permissions.includes('upload:create') && (
          <div className="mt-3 flex flex-wrap gap-3">
            <BotaoUpload
              rotulo="Enviar relatório do Semgrep"
              extensao=".json,application/json"
              ocupado={enviando === 'semgrep'}
              aoEscolher={(arquivo) => enviar('semgrep', arquivo)}
            />
            <BotaoUpload
              rotulo="Enviar relatório do Nuclei"
              extensao=".jsonl,.json,.txt"
              ocupado={enviando === 'nuclei'}
              aoEscolher={(arquivo) => enviar('nuclei', arquivo)}
            />
            <BotaoUpload
              rotulo="Enviar relatório do Trivy"
              extensao=".json,application/json"
              ocupado={enviando === 'trivy'}
              aoEscolher={(arquivo) => enviar('trivy', arquivo)}
            />
            <BotaoUpload
              rotulo="Enviar relatório do Gitleaks"
              extensao=".json,application/json"
              ocupado={enviando === 'gitleaks'}
              aoEscolher={(arquivo) => enviar('gitleaks', arquivo)}
            />
            <BotaoUpload
              rotulo="Enviar relatório do Checkov (IaC)"
              extensao=".json,application/json"
              ocupado={enviando === 'checkov'}
              aoEscolher={(arquivo) => enviar('checkov', arquivo)}
            />
            <BotaoUpload
              rotulo="Enviar SBOM (CycloneDX / SPDX)"
              extensao=".json,application/json"
              ocupado={enviando === 'sbom'}
              aoEscolher={enviarArqSbom}
            />
          </div>
        )}
      </div>

      {erroUpload && (
        <p className="mt-3 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{erroUpload}</p>
      )}

      {resultado && (
        <div className="mt-3 space-y-2">
          <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            {resultado.ferramenta_label}: {resultado.achados_lidos} achado(s) lido(s) ·{' '}
            {resultado.vulnerabilidades_totais} vulnerabilidade(s) ·{' '}
            {resultado.vulnerabilidades_novas} nova(s)
          </p>
          {resultado.avisos.length > 0 && (
            <Aviso>
              <p className="font-medium">
                {resultado.achados_ignorados} entrada(s) do arquivo foram ignoradas:
              </p>
              <ul className="mt-1 list-inside list-disc space-y-0.5">
                {resultado.avisos.slice(0, 5).map((aviso) => (
                  <li key={aviso}>{aviso}</li>
                ))}
              </ul>
            </Aviso>
          )}
        </div>
      )}
    </div>
  )
}

function RelatoriosEmVigor({
  uploads,
  carregando,
}: {
  uploads: UploadResumo[] | null
  carregando: boolean
}) {
  if (carregando) {
    return <p className="text-xs text-slate-400">Verificando relatórios…</p>
  }

  if (!uploads?.length) {
    return (
      <p className="text-xs text-slate-400">
        Nenhum relatório enviado. A correlação só acontece com os dois.
      </p>
    )
  }

  return (
    <div className="flex flex-wrap gap-4 text-xs">
      {uploads.map((upload) => (
        <div key={upload.id} className="flex items-center gap-2">
          <BadgeFerramenta nome={upload.ferramenta_label} />
          <span className="text-slate-600">
            {upload.nome_arquivo} · {upload.total_achados} achado(s)
            {upload.total_ignorados > 0 && `, ${upload.total_ignorados} ignorado(s)`} ·{' '}
            {new Date(upload.criado_em).toLocaleDateString('pt-BR')}
          </span>
        </div>
      ))}
    </div>
  )
}

function Contador({
  rotulo,
  valor,
  alerta,
}: {
  rotulo: string
  valor: number
  alerta?: boolean
}) {
  return (
    <div className="text-center">
      <p className="text-xs uppercase tracking-wide text-slate-400">{rotulo}</p>
      <p
        className={`text-lg font-semibold ${
          alerta && valor > 0 ? 'text-rose-600' : 'text-slate-800'
        }`}
      >
        {valor}
      </p>
    </div>
  )
}

function BotaoUpload({
  rotulo,
  extensao,
  ocupado,
  aoEscolher,
}: {
  rotulo: string
  extensao: string
  ocupado: boolean
  aoEscolher: (arquivo: File) => void
}) {
  return (
    <label
      className={`inline-flex cursor-pointer items-center justify-center rounded-md border border-dashed border-slate-300 px-4 py-2 text-sm transition-all duration-200 ${
        ocupado ? 'bg-slate-50 text-slate-400' : 'text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700'
      }`}
    >
      <FileUp className="mr-2 h-4 w-4" />
      {ocupado ? 'Processando…' : rotulo}
      <input
        type="file"
        accept={extensao}
        className="hidden"
        disabled={ocupado}
        onChange={(evento) => {
          const arquivo = evento.target.files?.[0]
          if (arquivo) aoEscolher(arquivo)
          // Limpa para permitir reenviar o mesmo arquivo em seguida
          evento.target.value = ''
        }}
      />
    </label>
  )
}

/**
 * Formulário de cadastro e de edição.
 *
 * O mesmo componente serve aos dois casos: os campos são idênticos, e duplicá-lo
 * faria as validações saírem de sincronia com o tempo. Sem `aplicacao`, cria;
 * com ela, edita.
 */
function FormularioAplicacao({
  aplicacao,
  aoCriar,
  aoSalvar,
}: {
  aplicacao?: AplicacaoNaLista
  aoCriar?: () => void
  aoSalvar?: (mudouContexto: boolean) => void
}) {
  const opcoes = useRequisicao(obterOpcoes, [])
  const editando = Boolean(aplicacao)

  const [form, setForm] = useState<NovaAplicacao>({
    nome: aplicacao?.nome ?? '',
    responsavel: aplicacao?.responsavel ?? '',
    ambiente: aplicacao?.ambiente ?? 'producao',
    exposicao: aplicacao?.exposicao ?? 'internet',
    importancia: aplicacao?.importancia ?? 'alta',
    url: aplicacao?.url ?? '',
  })
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(evento: FormEvent) {
    evento.preventDefault()
    setErro(null)
    setEnviando(true)
    try {
      if (aplicacao) {
        // Só estes três alteram o risco das vulnerabilidades já registradas
        const mudouContexto =
          form.ambiente !== aplicacao.ambiente ||
          form.exposicao !== aplicacao.exposicao ||
          form.importancia !== aplicacao.importancia

        await atualizarAplicacao(aplicacao.id, { ...form, url: form.url || null })
        aoSalvar?.(mudouContexto)
      } else {
        await criarAplicacao({ ...form, url: form.url || null })
        aoCriar?.()
      }
    } catch (falha) {
      setErro(
        mensagemDeErro(falha, editando ? 'Não foi possível salvar.' : 'Não foi possível cadastrar.'),
      )
    } finally {
      setEnviando(false)
    }
  }

  if (opcoes.carregando || !opcoes.dados) {
    return <Carregando texto="Carregando opções…" />
  }

  const conteudo = (
      <form onSubmit={aoEnviar} className="grid gap-4 sm:grid-cols-2">
        <Texto
          rotulo="Nome"
          valor={form.nome}
          aoMudar={(v) => setForm({ ...form, nome: v })}
        />
        <Texto
          rotulo="Responsável"
          valor={form.responsavel}
          aoMudar={(v) => setForm({ ...form, responsavel: v })}
        />
        <Selecao
          rotulo="Ambiente"
          valor={form.ambiente}
          opcoes={opcoes.dados.ambientes}
          aoMudar={(v) => setForm({ ...form, ambiente: v as NovaAplicacao['ambiente'] })}
        />
        <Selecao
          rotulo="Exposição"
          valor={form.exposicao}
          opcoes={opcoes.dados.exposicoes}
          aoMudar={(v) => setForm({ ...form, exposicao: v as NovaAplicacao['exposicao'] })}
        />
        <Selecao
          rotulo="Importância para o negócio"
          valor={form.importancia}
          opcoes={opcoes.dados.importancias}
          aoMudar={(v) => setForm({ ...form, importancia: v as NovaAplicacao['importancia'] })}
        />
        <Texto
          rotulo="URL (opcional)"
          valor={form.url ?? ''}
          obrigatorio={false}
          aoMudar={(v) => setForm({ ...form, url: v })}
        />

        {erro && (
          <p className="sm:col-span-2 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {erro}
          </p>
        )}

        <div className="sm:col-span-2 mt-2">
          <button
            type="submit"
            disabled={enviando}
            className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-all duration-200 hover:bg-indigo-700 hover:shadow-md disabled:opacity-60"
          >
            {enviando ? 'Salvando…' : editando ? 'Salvar alterações' : 'Cadastrar'}
          </button>
          <p className="mt-2 text-xs text-slate-500">
            Ambiente, exposição e importância definem o peso das vulnerabilidades: a mesma
            falha vale mais em produção exposta à internet do que em ambiente de teste.
            {editando && ' Alterar qualquer um dos três reclassifica o que já foi registrado.'}
          </p>
        </div>
      </form>
  )

  // Na edição o formulário já está dentro do cartão da aplicação; envolvê-lo em
  // outro cartão criaria uma moldura dentro da outra.
  return editando ? conteudo : (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-6 mb-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Nova aplicação</h2>
      {conteudo}
    </div>
  )
}

function Texto({
  rotulo,
  valor,
  aoMudar,
  obrigatorio = true,
}: {
  rotulo: string
  valor: string
  aoMudar: (valor: string) => void
  obrigatorio?: boolean
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{rotulo}</span>
      <input
        type="text"
        value={valor}
        required={obrigatorio}
        onChange={(evento) => aoMudar(evento.target.value)}
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none transition-colors duration-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
      />
    </label>
  )
}

function Selecao({
  rotulo,
  valor,
  opcoes,
  aoMudar,
}: {
  rotulo: string
  valor: string
  opcoes: { valor: string; label: string }[]
  aoMudar: (valor: string) => void
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{rotulo}</span>
      <select
        value={valor}
        onChange={(evento) => aoMudar(evento.target.value)}
        className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition-colors duration-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
      >
        {opcoes.map((opcao) => (
          <option key={opcao.valor} value={opcao.valor}>
            {opcao.label}
          </option>
        ))}
      </select>
    </label>
  )
}
