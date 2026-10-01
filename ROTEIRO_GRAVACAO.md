# Roteiro Completo de Gravação: PRIDE Vision AI 🎬

Este roteiro vai guiar você para mostrar **todos os módulos da plataforma** operando juntos. Vamos simular a jornada completa de uma vulnerabilidade, desde a ingestão via CI/CD, passando pelo motor de IA, até a geração de ticket no Jira e a visão consolidada de Cloud e Runtime.

---

## 🛠️ PASSO 1: Preparando o Palco (Antes de Gravar)

1. **Inicie o Backend e Frontend** normalmente nos seus terminais.
2. Abra um terminal extra e rode o nosso gerador de dados (isso preenche gráficos e cria as 4 aplicações iniciais para o Dashboard não ficar vazio):
   ```powershell
   python backend/popular_demo.py
   ```
3. Abra a documentação interativa da API (Swagger) em uma aba separada do navegador: `http://localhost:8000/docs`
4. Na aba do Swagger, clique no botão verde **"Authorize"** e faça login com:
   * **Username:** `admin@pride.com`
   * **Password:** `admin`
   *(Deixe essa aba aberta, usaremos ela no meio do vídeo).*

---

## 🎥 INICIANDO A GRAVAÇÃO

### Cena 1: A Visão Geral (Dashboard e Multi-Tenancy)
* **Ação:** Abra o frontend em `http://localhost:5173`, faça login com `admin@pride.com` / `admin`.
* **Narração Sugerida:** *"Bem-vindos ao PRIDE Vision AI. Esta é a visão consolidada de ASPM (Application Security Posture Management). Ao invés de olhar dezenas de ferramentas diferentes, a liderança vê a postura de risco de todas as aplicações e infraestrutura na nuvem num só lugar."*
* **Destaque:** Mostre o menu no canto superior direito alterando o **Workspace (Tenant)**. Mostre que a plataforma é 100% pronta para empresas SaaS B2B ou grandes corporações com múltiplas filiais.

### Cena 2: CI/CD Security & Ingestão (O Coração da Plataforma)
* **Ação:** Clique no menu esquerdo **"Aplicações"** e depois em **"CI/CD Security"**.
* **Narração Sugerida:** *"Como os dados chegam aqui? O PRIDE não clona o seu código. Ele se conecta via Webhook na sua esteira (como GitHub Actions). Quando um desenvolvedor faz um Push, as ferramentas open-source rodam lá no GitHub e mandam os dados pra cá. Além disso, o PRIDE atua como um 'Security Gate', decidindo se o Pull Request pode ser aprovado ou não baseado nas políticas que definimos aqui."*

### Cena 3: O Fluxo de Correção (Vulnerabilidades, Risco e IA)
* **Ação:** Clique no menu **"Vulnerabilidades"** e abra qualquer vulnerabilidade que esteja na lista (Ex: uma SQL Injection ou falha de container).
* **Narração Sugerida:** *"A maior dor das equipes de AppSec é a triagem. O PRIDE cruza a gravidade técnica com o Contexto do Negócio (Exposição à internet, Importância da Aplicação) para calcular o Risco Priorizado. É isso que nos diz o que consertar primeiro."*
* **Ação:** Clique na aba **"Explicação da IA"**.
* **Narração Sugerida:** *"Para facilitar a vida do desenvolvedor, o PRIDE usa IA Generativa integrada. Ele lê o payload bruto do scanner e mastiga para o desenvolvedor como ele corrige aquele erro específico na linguagem dele."*
* **Ação:** Vá no menu de Status (no topo direito) e mude para **"Em Correção"**. Mostre o relógio do SLA atualizando.

### Cena 4: Integração de Ticketing (Jira)
* **Ação:** Na mesma tela da vulnerabilidade, clique em **"Criar Ticket"** (Na aba lateral de Integrações).
* **Narração Sugerida:** *"O fluxo não morre no AppSec. A plataforma tem integração OAuth com o Jira para mandar essa falha formatada para a sprint do time de desenvolvimento, com tracking bidirecional."*

### Cena 5: Expandindo para Cloud (CSPM)
* **Ação:** Mude de aba no navegador para aquela tela do **Swagger** (`http://localhost:8000/docs`).
* Vá até a seção **Ingestion**, abra o endpoint `POST /api/v1/ingestion/cspm` e clique em **Try it out**.
* Cole exatamente este JSON na caixa de texto e clique em **Execute**:
  ```json
  {
    "provider": "aws",
    "account_id": "123456789012",
    "resource_id": "arn:aws:s3:::meu-bucket-financeiro",
    "resource_type": "aws_s3_bucket",
    "region": "us-east-1",
    "severity": "CRITICAL",
    "title": "S3 Bucket Publicamente Acessível",
    "description": "O bucket possui ACL que permite acesso irrestrito da internet."
  }
  ```
* **Ação:** Volte para a aba do **Frontend**, clique em **"Cloud Security"** no menu.
* **Narração Sugerida:** *"O PRIDE unifica as verticais. Nós acabamos de simular um scanner de nuvem reportando um Bucket S3 exposto. Ele aparece em tempo real aqui, unindo a visão de código com a visão de nuvem (Code to Cloud)."*

### Cena 6: Expandindo para Runtime Security
* **Ação:** Volte para a aba do **Swagger**. Abra o endpoint `POST /api/v1/ingestion/runtime/` e clique em **Try it out**.
* Cole este JSON e clique em **Execute**:
  ```json
  {
    "rule": "Terminal shell in container",
    "priority": "CRITICAL",
    "output": "A shell was spawned in a container with an attached terminal (user=root container_id=abc123def456)",
    "time": "2026-10-01T15:00:00Z",
    "output_fields": {
      "container.id": "abc123def456",
      "proc.name": "bash",
      "evt.type": "execve"
    }
  }
  ```
* **Ação:** Vá no **Frontend** em **"Runtime Security"**. Mostre o alerta de "Terminal shell in container" listado na tabela!
* **Narração Sugerida:** *"E se o atacante passar pelas defesas estáticas? Temos a visão de Runtime integrada. O PRIDE intercepta eventos a nível de Kernel via ferramentas como o Falco para que o SOC aja imediatamente."*

### Cena 7: Compliance, Auditoria e Saúde
* **Ação:** Clique em **"Auditoria"**. Mostre os logs imutáveis gerados de todas as ações que você fez no vídeo (Login, mudança de status).
* **Ação:** Por fim, clique em **"System Health" (Observabilidade)**. Mostre os gráficos de telemetria rodando liso.
* **Narração Sugerida:** *"Toda ação na plataforma é rastreada na trilha de auditoria para compliance. E a própria plataforma é instrumentada com telemetria corporativa para provar sua estabilidade. PRIDE Vision AI: a plataforma definitiva de AppSec."*
