# SDD 19 — Supply Chain Signatures & Provenance

## 1. Objetivo
Transformar o PRIDE de uma plataforma que apenas analisa imagens/SBOMs em uma plataforma capaz de verificar se um artefato possui assinatura e proveniência verificáveis, e se atende às políticas de confiança da organização.

## 2. Artefato e Identidade
- **AC-SC-01** - Dado que um artefato é submetido, quando for verificá-lo, então o sistema deve utilizar o seu digest (ex: sha256) como identidade forte.

## 3. Verificação Keyless e Cosign
O projeto usará a ferramenta `cosign` (Sigstore) via `backend/bin/cosign.exe` para verificações criptográficas.
- **AC-SC-02** - Dado um artefato assinado (Keyless), quando solicitar verificação, então deve validar a assinatura contra a infraestrutura Sigstore (Rekor/Fulcio) e retornar o status `signature_valid` e o `signer_identity`.
- **AC-SC-03** - Dado que a assinatura não existe ou é inválida, quando verificar, então `signature_valid` deve ser falso.

## 4. Proveniência e Attestations (in-toto)
- **AC-SC-04** - Dado que o artefato possui attestation in-toto, quando verificado pelo cosign, então o sistema deve registrar `provenance_present` e extrair o `builder`.
- **AC-SC-05** - Dado que uma attestation existe, quando a assinatura da attestation for inválida, então `provenance_valid` deve ser falso.

## 5. Integração com Policy Engine
O Policy Engine deve suportar novas regras.
- **AC-SC-06** - Dado que a política exige assinatura (`require_signature`), quando a assinatura for inválida, então a política deve falhar e o Security Gate deve retornar BLOCK (ou WARN).
- **AC-SC-07** - Dado que a política exige um builder específico (`trusted_builder`), quando a proveniência não contiver esse builder, então a política deve falhar.

## 6. Normalização e Findings
- **AC-SC-08** - Dado que a verificação falhou em relação à política, quando gerar os resultados, então deve criar um `AchadoNormalizado` com a categoria `SUPPLY_CHAIN` e título correspondente (ex: SIGNATURE_INVALID).
- **AC-SC-09** - Dado um finding de Supply Chain, quando ingerido pelo motor, então deve ser deduplicado com base no digest do artefato e na regra violada.

## 7. Integração CI/CD e Audit
- **AC-SC-10** - Dado que o Security Gate for executado para Supply Chain, quando processar um artefato em pipeline, então deve vincular a verificação ao `PipelineRun`.
- **AC-SC-11** - Dado o início e fim da verificação de Supply Chain, quando ocorrer, então deve gerar os respectivos eventos no Audit Log (`SUPPLY_CHAIN_VERIFICATION_STARTED`, `SUPPLY_CHAIN_VERIFICATION_FINISHED`).

## 8. Segurança na Execução
- **AC-SC-12** - Dado que o sistema invoca o `cosign`, quando construir os argumentos, então não deve usar shell=True nem permitir injeção de comandos a partir da entrada do usuário.

## 9. Frontend
- **AC-SC-13** - Dado que o usuário visualiza os detalhes de um Container, quando este possuir verificações de Supply Chain, então a interface deve exibir o status da assinatura, identity e builder, compondo uma visão integrada.
