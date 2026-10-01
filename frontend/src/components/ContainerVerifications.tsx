import { obterVerificacoes } from '../api/client'
import { useRequisicao } from '../hooks/useRequisicao'

export function ContainerVerifications({ imageName }: { imageName: string | null | undefined }) {
  const { dados: verifications, carregando, erro } = useRequisicao(
    async () => {
      if (!imageName) return []
      return obterVerificacoes(imageName)
    },
    [imageName]
  )

  if (!imageName) return null
  if (carregando) return <p className="text-sm text-slate-500 mt-2">Carregando verificações...</p>
  if (erro) return <p className="text-sm text-red-500 mt-2">Erro ao carregar verificações: {erro}</p>
  if (!verifications || verifications.length === 0) return null

  // Pega a verificação mais recente (vem na ordem desc do backend)
  const v = verifications[0]

  return (
    <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded-md">
      <h4 className="text-sm font-semibold text-slate-800 mb-2">Supply Chain Verification</h4>
      
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-slate-500 w-24">Assinatura:</span>
          {v.signature_valid ? (
            <span className="text-green-700 bg-green-100 px-2 py-0.5 rounded text-xs font-medium">VÁLIDA</span>
          ) : (
            <span className="text-red-700 bg-red-100 px-2 py-0.5 rounded text-xs font-medium">INVÁLIDA / AUSENTE</span>
          )}
        </div>

        {v.signer_identity && (
          <div className="flex items-center gap-2">
            <span className="text-slate-500 w-24">Identidade:</span>
            <span className="text-slate-700 font-mono text-xs truncate" title={v.signer_identity}>
              {v.signer_identity}
            </span>
          </div>
        )}

        <div className="flex items-center gap-2">
          <span className="text-slate-500 w-24">Proveniência:</span>
          {v.provenance_valid ? (
            <span className="text-green-700 bg-green-100 px-2 py-0.5 rounded text-xs font-medium">VÁLIDA</span>
          ) : (
            <span className="text-red-700 bg-red-100 px-2 py-0.5 rounded text-xs font-medium">INVÁLIDA / AUSENTE</span>
          )}
        </div>

        {v.builder && (
          <div className="flex items-center gap-2">
            <span className="text-slate-500 w-24">Builder:</span>
            <span className="text-slate-700 font-mono text-xs truncate" title={v.builder}>
              {v.builder}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
