import { useEffect, useState } from 'react'
import { apiGetAuditLogs } from '../api/client'
import { Erro, Vazio } from '../components/Feedback'

export function Auditoria() {
  const [logs, setLogs] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [erro, setErro] = useState<Error | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [pagina, setPagina] = useState(1)
  const limite = 20

  useEffect(() => {
    let ativo = true
    setCarregando(true)
    
    apiGetAuditLogs((pagina - 1) * limite, limite)
      .then((res) => {
        if (ativo) {
          setLogs(res.items)
          setTotal(res.total)
          setErro(null)
        }
      })
      .catch((err) => {
        if (ativo) setErro(err)
      })
      .finally(() => {
        if (ativo) setCarregando(false)
      })
      
    return () => {
      ativo = false
    }
  }, [pagina])

  if (erro) {
    return <div className="p-8"><Erro mensagem={erro.message} /></div>
  }

  const totalPaginas = Math.ceil(total / limite)

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold leading-7 text-slate-900 sm:truncate sm:tracking-tight">
            Trilha de Auditoria
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Registro imutável de ações e eventos de segurança da plataforma.
          </p>
        </div>
      </div>

      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-slate-300">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900">
                      Data/Hora
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
                      Ação
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
                      Entidade
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
                      Ator
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
                      Detalhes
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {carregando ? (
                    <tr>
                      <td colSpan={5} className="py-10 text-center text-sm text-slate-500">
                        Carregando...
                      </td>
                    </tr>
                  ) : logs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-10 text-center text-sm text-slate-500">
                        <Vazio titulo="Nenhum registro" descricao="A trilha de auditoria está vazia." />
                      </td>
                    </tr>
                  ) : (
                    logs.map((log) => (
                      <tr key={log.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-slate-900">
                          {new Date(log.criado_em).toLocaleString('pt-BR')}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500 font-mono">
                          {log.action}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                          {log.entity_type} {log.entity_id ? `(#${log.entity_id})` : ''}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                          {log.actor ? (
                            <div>
                              <div>{log.actor.nome}</div>
                              <div className="text-xs text-slate-400">{log.actor.email}</div>
                            </div>
                          ) : (
                            <span className="text-slate-400">Sistema / Desconhecido</span>
                          )}
                        </td>
                        <td className="px-3 py-4 text-xs text-slate-500 max-w-xs truncate" title={JSON.stringify(log.new_value || log.metadata_info || {})}>
                          {log.new_value ? JSON.stringify(log.new_value) : (log.metadata_info ? JSON.stringify(log.metadata_info) : '-')}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
              
              {!carregando && totalPaginas > 1 && (
                <div className="flex items-center justify-between border-t border-slate-200 bg-white px-4 py-3 sm:px-6">
                  <div className="flex flex-1 justify-between sm:hidden">
                    <button
                      onClick={() => setPagina(p => Math.max(1, p - 1))}
                      disabled={pagina === 1}
                      className="relative inline-flex items-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))}
                      disabled={pagina === totalPaginas}
                      className="relative ml-3 inline-flex items-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                    >
                      Próxima
                    </button>
                  </div>
                  <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-slate-700">
                        Mostrando de <span className="font-medium">{(pagina - 1) * limite + 1}</span> a{' '}
                        <span className="font-medium">{Math.min(pagina * limite, total)}</span> de{' '}
                        <span className="font-medium">{total}</span> resultados
                      </p>
                    </div>
                    <div>
                      <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                        <button
                          onClick={() => setPagina(p => Math.max(1, p - 1))}
                          disabled={pagina === 1}
                          className="relative inline-flex items-center rounded-l-md px-2 py-2 text-slate-400 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                        >
                          <span className="sr-only">Anterior</span>
                          &larr;
                        </button>
                        <button
                          onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))}
                          disabled={pagina === totalPaginas}
                          className="relative inline-flex items-center rounded-r-md px-2 py-2 text-slate-400 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                        >
                          <span className="sr-only">Próxima</span>
                          &rarr;
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
