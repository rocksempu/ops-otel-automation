# 📊 Observability as Code (OaC) - Dashboards & Alertas Self-Service

> **Plataforma de Observabilidade Automatizada**
> Gerencie o ciclo de vida completo da monitoria (Criação e Remoção) seguindo as melhores práticas de SRE e Governança.

---

## 🎯 O Objetivo
Este projeto implementa uma esteira de **Observability as Code**. O objetivo é democratizar a criação de monitoramento para os times de desenvolvimento, garantindo que todo serviço novo nasça com:
1.  **Visibilidade:** Dashboards completos (Golden Signals, RUM, Infra).
2.  **Proatividade:** Alertas automáticos de erro e latência.
3.  **Governança:** Tags obrigatórias e políticas de ambiente.

---

## 🚀 Guia de Uso (Lifecycle Management)

Toda a interação é feita via **GitHub Actions**. Não altere recursos manualmente no Grafana.

### 1️⃣ Como Criar (Onboarding)
Para criar monitoria para um novo serviço:

1.  Acesse a aba **[Actions](../../actions)**.
2.  Selecione o workflow **"Criar Dashboard (Self-Service)"**.
3.  Clique em **Run workflow**.
4.  Preencha os campos obrigatórios:
    * **Modelo:** Escolha entre *Golden Signals*, *Detalhes* ou *RUM*.
    * **Service Name:** O nome exato da aplicação (ex: `pix-api`).
    * **Namespace:** O agrupador do negócio.
    * **Owner:** Squad ou Email responsável (para alertas).
    * **Ambiente:** `dev`, `hml` ou `prd`.
    * **Ativar Alertas?**: Define se os alertas serão criados (Obrigatório em PRD).
5.  Clique no botão verde **Run workflow**.

### 2️⃣ Como Remover (Decommission)
Para remover dashboards e alertas de um serviço descontinuado ou criado erroneamente:

1.  Acesse a aba **[Actions](../../actions)**.
2.  Selecione o workflow **"Decommission (Via API)"**.
3.  Clique em **Run workflow**.
4.  Preencha os campos:
    * **Service Name:** O nome exato do serviço que deseja remover (ex: `pix-api`).
    * **Confirmação:** Digite `DELETE` para autorizar.
5.  O sistema fará a limpeza automática de Dashboards e Pastas de Alerta vinculados a este serviço.

---

## ⚠️ Aviso Importante sobre Drift

> **NUNCA delete Dashboards ou Alertas manualmente pela interface do Grafana.**

Esta plataforma utiliza o conceito de **Infrastructure as Code**. O código (Terraform/Pipeline) é a "fonte da verdade".
* Se você deletar um recurso manualmente, a pipeline pode falhar na próxima execução ou recriar o recurso inesperadamente.
* Se precisar remover algo, utilize sempre o workflow de **Decommission**.

---

## 👮 Política de Governança (Policy as Code)

A pipeline aplica regras automáticas baseadas no ambiente selecionado:

| Ambiente | Regra de Alertas | Comportamento |
| :--- | :--- | :--- |
| **PRD (Produção)** | 🚨 **Obrigatório** | O sistema **ignora** o checkbox e força a criação dos alertas de erro e latência. Produção não pode ficar sem monitoria. |
| **DEV / HML** | 🔓 **Opcional** | O sistema respeita a sua escolha no checkbox `Ativar Alertas`. Útil para evitar ruído em ambientes de teste. |

---

## 📦 Catálogo de Templates

Atualmente suportamos os seguintes modelos (BTM-First):

| Modelo | Foco | Descrição |
| :--- | :--- | :--- |
| **Golden Signals** | Backend | Monitoramento de Latência, Erro, Tráfego e Saturação. |
| **Detalhes do Serviço** | Infra | Uso de CPU, Memória, Status de Pods e SLI x SLO. |
| **RUM (Web Vitals)** | Frontend | Experiência do usuário (LCP, CLS, INP) e performance por browser. |

---

## 🛠️ Detalhes Técnicos (Para Mantenedores)

### Estrutura do Projeto
```text
.
├── .github/workflows/   # Pipelines de Criação e Destruição (YAML)
├── terraform/           # Código IaC (Motor de Criação)
├── scripts/             # Scripts auxiliares (Python para limpeza via API)
└── templates/           # JSONs parametrizados do Grafana