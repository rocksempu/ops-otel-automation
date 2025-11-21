# 📊 Observability as Code (OaC) - Dashboards & Alertas Self-Service

> **Plataforma de Observabilidade Automatizada**
> Gerencie o ciclo de vida completo da monitoria (Criação e Remoção) seguindo as melhores práticas de SRE e Governança Corporativa.

---

## 🎯 O Objetivo
Este projeto implementa uma esteira de **Observability as Code**. O objetivo é democratizar a criação de monitoramento para os times de desenvolvimento, garantindo que todo serviço novo nasça com:
1.  **Visibilidade:** Dashboards completos (Golden Signals, RUM, Infra).
2.  **Proatividade:** Alertas automáticos com link direto para Runbooks.
3.  **Governança:** Tags obrigatórias, integração com ITSM (ServiceNow) e políticas de ambiente.

---

## 🛡️ Quality Assurance (Quality Gates)
Para garantir a integridade da plataforma, a pipeline executa validações automáticas:
* **JSON Linting:** Validação sintática de templates antes do deploy.
* **ServiceNow Gate:** Verificação mandatória de tickets de mudança (GMUD) para ações em Produção.

---

## 🚀 Guia de Uso (Lifecycle Management)

### 1️⃣ Como Criar (Onboarding)
1.  Acesse a aba **[Actions](../../actions)** > **"Criar Dashboard (Self-Service)"**.
2.  Clique em **Run workflow** e preencha:
    * **Modelo, Service Name, Namespace, Owner.**
    * **Ambiente:** `dev`, `hml` ou `prd`.
    * **Ativar Alertas?**: (Obrigatório em PRD).
    * **GMUD (Change Ticket):** Obrigatório se Ambiente for `prd` (Ex: CHG00123).
3.  Clique no botão verde **Run workflow**.

### 2️⃣ Como Remover (Decommission)
1.  Acesse a aba **[Actions](../../actions)** > **"Decommission (Simples)"**.
2.  Clique em **Run workflow** e preencha:
    * **Service Name:** O nome exato do serviço.
    * **Ambiente:** `dev`, `hml` ou `prd`.
    * **Ação:**
        * `🔍 APENAS SIMULAR`: Dry Run (Seguro).
        * `💥 DESTRUIR DE VERDADE`: Executa a exclusão.
    * **GMUD (Change Ticket):** Obrigatório se for destruir em `prd`.
3.  Clique no botão verde **Run workflow**.

---

## 👮 Política de Governança (Policy as Code)

A plataforma aplica regras rígidas dependendo do ambiente selecionado:

| Ambiente | Regra de Alertas | Regra de Mudança (ITSM) |
| :--- | :--- | :--- |
| **PRD** | 🚨 **Obrigatório** | 🛑 **Exige GMUD (CHG)** válida para Criar ou Destruir. |
| **DEV / HML** | 🔓 **Opcional** | ✅ Livre (Self-Service puro). |

---

## 📦 Catálogo de Templates (BTM-First)

| Modelo | Foco | Descrição |
| :--- | :--- | :--- |
| **Golden Signals** | Backend | Latência, Erro, Tráfego e Saturação. |
| **Detalhes do Serviço** | Infra | CPU, Memória, Pods e SLI x SLO. |
| **RUM (Web Vitals)** | Frontend | Experiência do usuário (LCP, CLS, INP). |

---

## 🏗️ Considerações de Arquitetura (MVP vs Produção)

### Estado do Terraform
Nesta versão **MVP**, o arquivo de estado (`terraform.tfstate`) é local e efêmero.
* **Decommission:** Utilizamos scripts Python via API do Grafana para garantir a limpeza dos recursos baseados no nome, contornando a dependência do estado.

### Infraestrutura (Self-Hosted Runner)
Devido a restrições de rede (Lab IBM Fyre/VPN), a pipeline roda em um **Windows Self-Hosted Runner** dentro da rede privada.

* **Requisitos:** Terraform (`C:\Terraform\terraform.exe`) e Python (v3.13+) instalados manualmente.
* **Segurança:** O serviço do Windows roda como `Local System` para garantir permissões.

### 🔮 Roadmap
1.  **Remote Backend:** Migrar o estado para S3/Azure Blob.
2.  **Notification Policies:** Centralizar roteamento de alertas.