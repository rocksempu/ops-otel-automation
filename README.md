# 📊 Observability as Code (OaC) - Dashboards & Alertas Self-Service

> **Plataforma de Observabilidade Automatizada**
> Gerencie o ciclo de vida completo da monitoria (Criação e Remoção) seguindo as melhores práticas de SRE e Governança.

---

## 🎯 O Objetivo
Este projeto implementa uma esteira de **Observability as Code**. O objetivo é democratizar a criação de monitoramento para os times de desenvolvimento, garantindo que todo serviço novo nasça com:
1.  **Visibilidade:** Dashboards completos (Golden Signals, RUM, Infra).
2.  **Proatividade:** Alertas automáticos com link direto para Runbooks de resolução.
3.  **Organização:** Recursos estruturados automaticamente em pastas unificadas por Projeto e Ambiente.

---

## 🛡️ Quality Assurance (Quality Gates)
Para garantir a integridade da plataforma, a pipeline executa validações automáticas antes de qualquer alteração:

* **JSON Linting:** Todos os templates na pasta `/templates` são validados sintaticamente antes do Terraform iniciar. Se um arquivo estiver quebrado, a esteira falha imediatamente (Fail Fast), impedindo erros no Grafana.

---

## 🚀 Guia de Uso (Lifecycle Management)

Toda a interação é feita via **GitHub Actions**.

### 1️⃣ Como Criar (Onboarding)
Para criar monitoria para um novo serviço:

1.  Acesse a aba **[Actions](../../actions)** deste repositório.
2.  Selecione o workflow **"Criar Dashboard (Self-Service)"**.
3.  Clique em **Run workflow**.
4.  Preencha os campos:
    * **Ação:** Escolha entre `SIMULAR` (Plan) ou `CRIAR DE VERDADE` (Apply).
    * **Modelo:** Escolha entre *Golden Signals*, *Detalhes* ou *RUM*.
    * **Service Name:** O nome exato da aplicação (ex: `pix-api`).
    * **Namespace:** O agrupador do negócio (ex: `pagamentos`).
    * **Owner:** Squad ou Email responsável (para alertas).
    * **Ambiente:** `dev`, `hml` ou `prd`.
    * **GMUD (Change Ticket):** Obrigatório se for `prd` (Ex: CHG00123).
5.  Clique no botão verde **Run workflow**.

✅ **Resultado:**
O sistema criará uma **Pasta Unificada** no Grafana seguindo o padrão:
> 📂 **Namespace - Service Name [Ambiente]**
> * 📊 Dashboard (Golden Signals/RUM)
> * 🔔 Grupo de Alertas (Com link para Runbooks)

### 2️⃣ Como Remover (Decommission)
Para remover dashboards e alertas de um serviço descontinuado ou criado erroneamente:

1.  Acesse a aba **[Actions](../../actions)**.
2.  Selecione o workflow **"Decommission (Simples)"**.
3.  Clique em **Run workflow**.
4.  Preencha os campos:
    * **Service Name:** O nome exato do serviço (Encontrado no título do Dashboard).
    * **Ação:**
        * `SIMULAR (Dry Run)`: Verifica o que será apagado sem executar.
        * `DESTRUIR DE VERDADE (Execute)`: Executa a exclusão definitiva dos recursos.
    * **GMUD:** Obrigatório para destruir recursos de `prd`.
5.  Clique no botão verde **Run workflow**.

---

## ⚠️ Aviso Importante sobre Drift

> **⛔ NUNCA delete Dashboards ou Alertas manualmente pela interface do Grafana.**

Esta plataforma utiliza o conceito de **Infrastructure as Code**. O código é a "fonte da verdade".
* Se você deletar um recurso manualmente, a pipeline pode falhar na próxima execução ou recriar o recurso inesperadamente (Drift de Configuração).
* Se precisar remover algo, utilize sempre o workflow de **Decommission**.

---

## 👮 Política de Governança (Policy as Code)

### Regras de Ambiente
A pipeline aplica regras automáticas baseadas no ambiente selecionado:

| Ambiente | Regra de Alertas | Regra de Mudança (ITSM) |
| :--- | :--- | :--- |
| **PRD** | 🚨 **Obrigatório** (Sempre Ativado) | 🛑 **Exige GMUD (CHG)** válida para Criar ou Destruir. |
| **DEV / HML** | 🔓 **Opcional** (Checkbox) | ✅ Livre (Self-Service puro). |

### 📖 Runbooks Inteligentes (Docs as Code)
Todo alerta criado pela plataforma (ex: "High Error Rate") já nasce com um campo **Runbook URL** configurado.
* Ao receber um alerta, o operador clica no link e é direcionado para o arquivo Markdown de documentação (`/runbooks`) dentro deste repositório, garantindo que a documentação de troubleshooting acompanhe a versão do código.

---

## 📦 Catálogo de Templates

Atualmente suportamos os seguintes modelos (BTM-First):

| Modelo | Foco | Descrição |
| :--- | :--- | :--- |
| **Golden Signals** | Backend | Monitoramento de Latência, Erro, Tráfego e Saturação. |
| **Detalhes do Serviço** | Infra | Uso de CPU, Memória, Status de Pods e SLI x SLO. |
| **RUM (Web Vitals)** | Frontend | Experiência do usuário (LCP, CLS, INP) e performance por browser. |

---

## 🏗️ Considerações de Arquitetura (MVP vs Produção)

### Estado do Terraform (State Management)
Nesta versão **MVP**, o arquivo de estado do Terraform (`terraform.tfstate`) é gerenciado **localmente** no Runner (Ephemeral).

* **Implicação:** O Terraform não mantém histórico persistente entre execuções de diferentes serviços.
* **Solução de Decommission:** Para garantir a destruição confiável, o workflow de *Decommission* utiliza um script auxiliar (Python) que interage diretamente com a API do Grafana, localizando e removendo a **Pasta do Projeto** inteira baseada no nome do serviço.

### Infraestrutura (Self-Hosted Runner)
Devido a restrições de rede (Lab IBM Fyre/VPN), a pipeline roda em um **Windows Self-Hosted Runner** dentro da rede privada.

* **Requisitos:** Terraform instalado (`C:\Terraform\terraform.exe`) e Python (v3.13+) no PATH.
* **Segurança:** O serviço do Windows roda como `Local System` para garantir permissões.

### 🔮 Roadmap
1.  **Remote Backend:** Migrar o armazenamento do `tfstate` para um object storage centralizado (AWS S3, Azure Blob Storage ou Terraform Cloud).
2.  **Notification Policies:** Centralizar a árvore de roteamento de alertas em um repositório dedicado.

---

## 🛠️ Detalhes Técnicos (Para Mantenedores)

### Estrutura do Projeto
```text
.
├── .github/workflows/   # Pipelines de Criação, Validação e Destruição (YAML)
├── terraform/           # Código IaC (Motor de Criação)
├── scripts/             # Scripts auxiliares (Python para limpeza via API)
├── templates/           # JSONs parametrizados do Grafana
└── runbooks/            # Documentação de Troubleshooting (Markdown)