<#
.SYNOPSIS
    O gate unico do PRIDE Vision AI.

.DESCRIPTION
    Roda tudo que precisa estar verde para uma tarefa ser considerada concluida:
    suite do backend, lint, tipos, testes do frontend, build e rastreabilidade
    AC <-> teste.

    Diferente de um pipeline comum, NAO aborta no primeiro erro. Um ruff
    vermelho nao pode esconder o resultado da suite: e justamente quando algo
    quebra que se precisa ver o quadro inteiro.

    Este script substitui a CI enquanto o projeto nao e um repositorio git.

    ATENCAO AO EDITAR: este arquivo e ASCII puro de proposito. O PowerShell 5.1
    le .ps1 sem BOM como ANSI, e um travessao em UTF-8 vira byte invalido que
    quebra o parser antes de qualquer coisa rodar. As mensagens acentuadas ficam
    nas ferramentas chamadas, nao aqui.

.PARAMETER Rapido
    Pula o build do frontend (o passo mais lento). Use durante a implementacao;
    nunca para dar tarefa por concluida.

.EXAMPLE
    .\scripts\verificar.ps1

.EXAMPLE
    .\scripts\verificar.ps1 -Rapido
#>
[CmdletBinding()]
param(
    [switch]$Rapido
)

# No PowerShell 5.1 uma linha em stderr de executavel nativo vira ErrorRecord,
# mesmo quando o processo termina com codigo 0 (o aviso de tamanho de chunk do
# vite e o caso classico). O gate julga pelo codigo de saida, nao por stderr.
$ErrorActionPreference = 'SilentlyContinue'

# As ferramentas chamadas imprimem em portugues; sem isto o console mostra
# mojibake no lugar dos acentos.
$env:PYTHONIOENCODING = 'utf-8'

$raiz = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $raiz 'backend'
$frontend = Join-Path $raiz 'frontend'

# Lista de resultados no escopo do script. A funcao escreve aqui em vez de
# devolver o objeto: em PowerShell, tudo que um comando dentro da funcao imprime
# tambem faz parte do valor de retorno dela, e cada linha de saida do pytest
# entraria na lista como se fosse uma etapa.
$script:resultados = [System.Collections.ArrayList]::new()

function Invoke-Etapa {
    param(
        [string]$Nome,
        [string]$Diretorio,
        [scriptblock]$Acao
    )

    Write-Host ''
    Write-Host "=== $Nome ===" -ForegroundColor Cyan

    $anterior = Get-Location
    Set-Location $Diretorio
    try {
        # Out-Host manda a saida para a tela sem deixa-la virar valor de retorno
        & $Acao | Out-Host
        $codigo = $LASTEXITCODE
        if ($null -eq $codigo) { $codigo = 0 }
    }
    catch {
        Write-Host $_.Exception.Message -ForegroundColor Red
        $codigo = 1
    }
    finally {
        Set-Location $anterior
    }

    if ($codigo -eq 0) {
        Write-Host "OK - $Nome" -ForegroundColor Green
    }
    else {
        Write-Host "FALHOU - $Nome (codigo $codigo)" -ForegroundColor Red
    }

    [void]$script:resultados.Add([pscustomobject]@{ Nome = $Nome; Codigo = $codigo })
}

function Add-Falha {
    param([string]$Nome, [string]$Motivo)

    Write-Host ''
    Write-Host "=== $Nome ===" -ForegroundColor Cyan
    Write-Host "FALHOU - $Motivo" -ForegroundColor Red
    [void]$script:resultados.Add([pscustomobject]@{ Nome = $Nome; Codigo = 1 })
}

# --- Backend ---------------------------------------------------------------

Invoke-Etapa -Nome 'Suite do backend (pytest)' -Diretorio $backend -Acao {
    ..\venv\Scripts\python.exe -m pytest -q
}

Invoke-Etapa -Nome 'Lint do backend (ruff)' -Diretorio $backend -Acao {
    ..\venv\Scripts\python.exe -m ruff check app/ tests/
}

Invoke-Etapa -Nome 'Tipos do backend (mypy --strict)' -Diretorio $backend -Acao {
    ..\venv\Scripts\python.exe -m mypy --strict app/
}

# --- Frontend --------------------------------------------------------------

if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
    Add-Falha -Nome 'Dependencias do frontend' `
        -Motivo 'node_modules ausente. Rode: npm install --prefix frontend'
}
else {
    Invoke-Etapa -Nome 'Testes do frontend (vitest)' -Diretorio $frontend -Acao {
        npm run test --silent
    }

    if ($Rapido) {
        Write-Host ''
        Write-Host 'PULADO - Build do frontend (-Rapido)' -ForegroundColor Yellow
    }
    else {
        Invoke-Etapa -Nome 'Build do frontend (tsc + vite)' -Diretorio $frontend -Acao {
            npm run build --silent
        }
    }
}

# --- O gate que define o projeto -------------------------------------------

Invoke-Etapa -Nome 'Rastreabilidade AC <-> teste' -Diretorio $raiz -Acao {
    .\venv\Scripts\python.exe scripts/rastreabilidade.py --emitir
}

# --- Resumo ----------------------------------------------------------------

Write-Host ''
Write-Host '================ RESUMO ================' -ForegroundColor Cyan
foreach ($resultado in $script:resultados) {
    if ($resultado.Codigo -eq 0) {
        Write-Host ('  [ OK ]  ' + $resultado.Nome) -ForegroundColor Green
    }
    else {
        Write-Host ('  [FALHA] ' + $resultado.Nome) -ForegroundColor Red
    }
}

$falhas = @($script:resultados | Where-Object { $_.Codigo -ne 0 })
Write-Host ''

if ($falhas.Count -eq 0) {
    Write-Host 'GATE VERDE - a tarefa pode ser considerada concluida.' -ForegroundColor Green
    exit 0
}

$mensagem = 'GATE VERMELHO - ' + $falhas.Count + ' etapa(s) falharam. A tarefa NAO esta concluida.'
Write-Host $mensagem -ForegroundColor Red
exit 1
