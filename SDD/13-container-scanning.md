# 13. Container Scanning

O PRIDE Vision AI integra achados de seguranca de containers de ferramentas como Trivy, diferenciando imagens de vulnerabilidades SCA e consolidando riscos.

## 13.1. Ingestao de Relatorios (Trivy Container)

- **AC-CONT-01** — Parser diferencia SCA e Container. **Dado** um relatorio do Trivy, **Quando** o ArtifactType for `container_image`, **Entao** o parser deve definir o tipo do achado como `container_vulnerability`.
- **AC-CONT-02** — Parser extrai detalhes do container. **Dado** um relatorio do Trivy de container, **Quando** for parseado, **Entao** o parser deve extrair digest, tags, OS, base image e pacote e guarda-los no `AchadoNormalizado`.
- **AC-CONT-03** — Ingestao cria entidade de container. **Dado** um upload de Trivy com informacoes de imagem, **Quando** os achados forem salvos, **Entao** uma `ContainerImage` unica baseada no digest ou nome deve ser gerada ou reaproveitada.
- **AC-CONT-04** — Endpoint baseado no digest. **Dado** um achado de container, **Quando** normalizado, **Entao** o endpoint deve usar o digest da imagem para evitar duplicatas erroneas.

