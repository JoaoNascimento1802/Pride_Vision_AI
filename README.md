# 🛡️ PRIDE Vision AI - ASPM Platform

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC?style=for-the-badge&logo=tailwind-css)
![AI](https://img.shields.io/badge/AI_Powered-Gemini-orange?style=for-the-badge&logo=google)

**PRIDE Vision AI** é uma plataforma inovadora de **ASPM (Application Security Posture Management)** projetada para revolucionar o DevSecOps. O sistema unifica os resultados de diversas ferramentas de segurança (SAST, DAST, SCA, Secrets) em um único painel, aplicando regras de negócio para calcular o risco real e utilizando Inteligência Artificial para orientar os desenvolvedores na correção das vulnerabilidades.

---

## 🎯 Funcionalidades Principais

A plataforma atende a todas as necessidades do ciclo de vida de segurança de software, desde a varredura na esteira até a resolução pela equipe de desenvolvimento.

### 🔍 Ingestão e Correlação (Visão Única)
- ✅ **Centralização:** Recebe relatórios JSON de ferramentas líderes de mercado (Semgrep, Trivy, Gitleaks, Nuclei, Checkov).
- ✅ **Desduplicação Inteligente:** Evita a "fadiga de alertas" agrupando falhas idênticas reportadas em diferentes momentos.
- ✅ **Correlação SAST + DAST:** Confirma automaticamente falhas encontradas no código fonte que estão ativamente exploráveis em tempo de execução.

### 🧠 Motor de Risco (Risk Engine)
- ✅ **Contexto de Negócio:** Não depende apenas do "High/Critical" padrão das ferramentas. O sistema eleva ou rebaixa a gravidade da falha com base na importância da aplicação (Alta/Média/Baixa) e no nível de exposição (Internet/Interna).
- ✅ **Tradução Universal:** Ferramentas falam línguas diferentes (ex: o Semgrep usa `ERROR`, o Trivy usa `CRITICAL`). O PRIDE normaliza tudo em 4 níveis claros: Crítico, Alto, Médio e Baixo.

### 🤖 Assistente de IA Generativa
- ✅ **Remediação Guiada:** Integração com LLMs (Google Gemini / OpenAI) para analisar a vulnerabilidade e explicar, em português claro, como o desenvolvedor deve alterar o código.
- ✅ **Data Masking:** Mascaramento inteligente de dados antes de enviar códigos para a IA, garantindo que senhas, tokens e IPs internos jamais vazem para provedores externos.

### 🚧 CI/CD Security Gates
- ✅ **Integração com Pipelines:** Envio automático de relatórios via GitHub Actions.
- ✅ **Políticas de Tolerância Zero:** Capacidade de criar regras que bloqueiam (BLOCK) automaticamente o pipeline de CI/CD se falhas inaceitáveis (como chaves da AWS vazadas) forem encontradas.
- ✅ **Histórico de Decisões:** Rastreabilidade completa de todas as execuções, commits e branches aprovadas ou bloqueadas.

---

## 🏗️ Arquitetura e Padrões

O projeto foi desenhado sob o conceito de "Spec-Driven Development", garantindo máxima qualidade, testabilidade e separação de responsabilidades.

- **Backend FastAPI:** Alta performance e tipagem rigorosa no backend utilizando Python moderno.
- **Frontend SPA:** Interface reativa, limpa e veloz utilizando React, Vite e Tailwind CSS.
- **Banco de Dados Relacional:** SQLAlchemy gerenciando as entidades, com suporte a SQLite (desenvolvimento) e PostgreSQL/Neon (produção).
- **Máquina de Estados (Lifecycle):** O status das vulnerabilidades obedece um ciclo de vida estrito (Nova ➔ Em Análise ➔ Em Correção ➔ Corrigida), garantindo conformidade.
- **Observabilidade:** Monitoramento da saúde do sistema, taxa de erros e banco de dados via endpoints prontos para integração com Prometheus e Grafana (`/api/metrics`).

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Linguagem:** Python 3.11+
- **Framework REST:** FastAPI
- **ORM & Banco de Dados:** SQLAlchemy (PostgreSQL / SQLite)
- **Integração de IA:** Google Gemini / OpenAI API
- **Testes:** Pytest

### Frontend
- **Linguagem:** TypeScript
- **Biblioteca UI:** React 18
- **Build Tool:** Vite
- **Estilização:** Tailwind CSS + Radix UI (Componentes acessíveis)
- **Roteamento:** React Router DOM

---

## ⚙️ Como Executar Localmente

### Pré-requisitos
- Python 3.11 ou superior
- Node.js 18+ (para o Frontend)

### 1. Configurando o Backend
```bash
# Entre na pasta do backend
cd backend

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/Scripts/activate  # (No Windows) ou source .venv/bin/activate (Linux/Mac)

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente (Crie um arquivo .env)
# Exemplo de .env:
# AI_DEFAULT_PROVIDER=gemini
# GEMINI_API_KEY=sua_chave_aqui

# Rode o servidor
uvicorn app.main:app --reload
```
A API estará disponível em `http://localhost:8000`. Acesse a documentação Swagger em `http://localhost:8000/docs`.

### 2. Configurando o Frontend
Abra um novo terminal e execute:
```bash
# Entre na pasta do frontend
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```
A interface gráfica estará disponível em `http://localhost:5173`.

---

## 👨‍💻 Equipe de Engenharia (Autores)

Este projeto foi desenvolvido e configurado por:

- **João Emanuel Pessoa do Nascimento** - RM: 571612
- **Karina Aparecida Bezerra** (@Karina-Bezerra) - RM: 569500
- **Davi Freire de França** - RM: 569659
- **Thales Samuel Paulino** - RM: 571762
- **Yanuska Monalisa Antunes Yabiku** - RM: 571686

---

## 📄 Licença

Este projeto é licenciado sob a **BSD 3-Clause License**. Consulte o arquivo `LICENSE.md` no repositório para mais detalhes. Todos os direitos reservados à equipe PRIDE Vision AI.
