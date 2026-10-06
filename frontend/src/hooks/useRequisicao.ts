// Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

/**
 * useRequisicao.ts — Busca de dados com os três estados sempre tratados.
 *
 * Pequeno o suficiente para não justificar uma biblioteca de cache, e garante
 * que nenhuma tela esqueça de tratar carregamento ou erro.
 */
import { useCallback, useEffect, useRef, useState } from 'react'

import { mensagemDeErro } from '../api/client'

export function useRequisicao<T>(buscar: () => Promise<T>, dependencias: unknown[] = []) {
  const [dados, setDados] = useState<T | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [recarregando, setRecarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const jaCarregou = useRef(false)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const executar = useCallback(buscar, dependencias)

  const recarregar = useCallback(() => {
    let cancelado = false

    // `carregando` só vale para a primeira busca. Numa recarga, a tela precisa
    // continuar desenhada: trocá-la por um indicador de página inteira
    // desmontaria os componentes filhos e apagaria o estado local deles — o
    // resultado de um upload, um formulário aberto, um aviso recém-exibido.
    if (jaCarregou.current) {
      setRecarregando(true)
    } else {
      setCarregando(true)
    }
    setErro(null)

    executar()
      .then((resultado) => {
        if (!cancelado) setDados(resultado)
      })
      .catch((falha) => {
        // Um 401 já derruba a sessão pelo interceptor; mostrar erro aqui
        // duplicaria a mensagem em cima da tela de login.
        if (!cancelado) setErro(mensagemDeErro(falha))
      })
      .finally(() => {
        if (cancelado) return
        jaCarregou.current = true
        setCarregando(false)
        setRecarregando(false)
      })

    return () => {
      cancelado = true
    }
  }, [executar])

  useEffect(() => recarregar(), [recarregar])

  return { dados, carregando, recarregando, erro, recarregar }
}
