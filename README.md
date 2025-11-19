# 📊 Observability as Code (OaC) - Dashboards & Alertas Self-Service

> **Plataforma de Observabilidade Automatizada**
> Crie dashboards ricos e alertas padronizados no Grafana em segundos, seguindo as melhores práticas de SRE e Governança, sem abrir tickets.

---

## 🎯 O Objetivo
Este projeto implementa uma esteira de **Observability as Code**. O objetivo é democratizar a criação de monitoramento para os times de desenvolvimento, garantindo que todo serviço novo nasça com:
1.  **Visibilidade:** Dashboards completos (Golden Signals, RUM, Infra).
2.  **Proatividade:** Alertas automáticos de erro e latência.
3.  **Governança:** Tags obrigatórias e políticas de ambiente (Alertas mandatórios em Produção).

---

## 🚀 Como Usar (Guia para Desenvolvedores)

Você não precisa instalar nada na sua máquina. Todo o processo é feito via GitHub Actions.

1.  Acesse a aba **[Actions](../../actions)** deste repositório.
2.  Selecione o workflow **"Criar Dashboard (Self-Service)"** no menu lateral.
3.  Clique em **Run workflow**.
4.  Preencha o formulário:
    * **Modelo:** Escolha o tipo de visualização (veja o catálogo abaixo).
    * **Service Name:** O nome exato da aplicação (ex: `pix-api`).
    * **Namespace:** O agrupador do negócio (ex: `meios-de-pagamento`).
    * **Owner:** Squad ou Email responsável (usado para envio de alertas).
    * **Ambiente:** `dev`, `hml` ou `prd`.
    * **Ativar Alertas?**: (Checkbox) Define se os alertas serão criados.
5.  Clique no botão verde **Run workflow**.

✅ **Pronto!** Em menos de 1 minuto, seu dashboard estará na pasta `Dashboards Automáticos (CI/CD)` e seus alertas na área de `Alerting` do Grafana.

---

## 👮 Política de Governança (Policy as Code)

A pipeline aplica regras automáticas baseadas no ambiente selecionado:

| Ambiente | Regra de Alertas | Comportamento |
| :--- | :--- | :--- |
| **PRD (Produção)** | 🚨 **Obrigatório** | O Terraform **ignora** o checkbox e força a criação dos alertas de erro e latência. Produção não pode ficar sem monitoria. |
| **DEV / HML** | 🔓 **Opcional** | O Terraform respeita a sua escolha no checkbox `Ativar Alertas`. Útil para evitar ruído em ambientes de teste. |

---

## 📦 Catálogo de Templates

Atualmente suportamos os seguintes modelos (BTM-First):

### 1. 🥇 Golden Signals (`goldensignals`)
* **Foco:** Saúde da Aplicação (Backend/API).
* **Painéis:** Taxa de Erros, Latência p95, RPS (Throughput), Saturação.
* **Extras:** Tabela de Logs de Erro recentes e Traces (Tempo) filtrados pelo serviço.

### 2. 🔍 Detalhes do Serviço (`detalhesporservico`)
* **Foco:** Infraestrutura e Recursos (SRE/Ops).
* **Painéis:** Uso de CPU e Memória (Pod/Container), Status de disponibilidade, SLI x SLO e Burn Rate.

### 3. 🌐 RUM - Web Vitals (`rum`)
* **Foco:** Experiência do Usuário Final (Frontend).
* **Painéis:** LCP (Largest Contentful Paint), CLS (Cumulative Layout Shift), INP, performance por Browser e Página.

---

## 🏗️ Arquitetura e Detalhes Técnicos (Para Mantenedores)

### Estrutura do Projeto
```text
.
├── .github/workflows/   # Pipeline de execução (Formulário)
├── terraform/           # Código IaC (Motor)
│   ├── main.tf          # Provider Grafana e Lógica de Templates
│   ├── alerts.tf        # Regras de Alerta e Contact Points
│   └── variables.tf     # Definição de Inputs e Variáveis
└── templates/           # JSONs parametrizados do Grafana