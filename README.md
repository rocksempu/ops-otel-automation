# 📊 Observability as Code (OaC) - Dashboards Self-Service

> **Plataforma de Observabilidade Automatizada**
> Crie dashboards padronizados no Grafana em segundos, seguindo as melhores práticas de SRE e Governança, sem abrir tickets.

---

## 🎯 O Objetivo
Este projeto implementa uma esteira de **Dashboards as Code**. O objetivo é democratizar a criação de monitoramento para os times de desenvolvimento, garantindo que todo serviço novo nasça com visibilidade mínima (Golden Signals) e governança (Tags, Owners e Padrões).

### Principais Benefícios
* **Autonomia:** O desenvolvedor não depende do time de Plataforma/SRE para criar a monitoria básica.
* **Padronização:** Todos os dashboards seguem o mesmo layout visual e convenções de métricas.
* **Governança:** Tags de `Owner`, `Namespace` e `Environment` são obrigatórias e aplicadas automaticamente.
* **Idempotência:** O código é a fonte da verdade. Alterações manuais no Grafana podem ser sobrescritas, garantindo consistência.

---

## 🏗️ Arquitetura da Solução

A solução utiliza uma abordagem **GitOps** híbrida para orquestrar a criação de recursos em um ambiente privado (On-Premise/Lab) a partir da nuvem pública.



1.  **Interface (GitHub Actions):** O usuário preenche um formulário "Workflow Dispatch" com os dados do serviço.
2.  **Orquestração (Self-Hosted Runner):** Um agente roda dentro da infraestrutura privada (VPN/Lab) para ter acesso direto ao Grafana.
3.  **Motor (Terraform):** O Terraform recebe os inputs, processa os templates JSON e aplica o estado desejado via API do Grafana.
4.  **Visualização (Grafana):** O dashboard é criado na pasta `Dashboards Automáticos (CI/CD)`.

---

## 📦 Catálogo de Templates

Atualmente, a plataforma suporta os seguintes modelos de observabilidade (BTM-First):

| Modelo | Descrição | Público Alvo |
| :--- | :--- | :--- |
| **Golden Signals** | Monitoramento essencial de **Latência, Erro, Tráfego e Saturação**. Baseado nas práticas do Google SRE. | Backend / APIs |
| **Detalhes do Serviço** | Visão infraestrutural detalhada: Consumo de CPU, Memória e status dos Pods/Containers. | SRE / Ops |
| **RUM (Web Vitals)** | Monitoramento da experiência do usuário final (Frontend). Focado em métricas como LCP e CLS. | Frontend / Mobile |

---

## 🚀 Como Usar (Guia para Desenvolvedores)

Não é necessário instalar nada na sua máquina. Siga os passos:

1.  Acesse a aba **[Actions](../../actions)** deste repositório.
2.  Selecione o workflow **"Criar Dashboard (Self-Service)"** no menu lateral.
3.  Clique em **Run workflow**.
4.  Preencha os campos obrigatórios:
    * **Modelo:** Escolha entre *Golden Signals*, *Detalhes* ou *RUM*.
    * **Service Name:** O nome exato da sua aplicação (ex: `pix-api`).
    * **Namespace:** O agrupador do negócio (ex: `meios-de-pagamento`).
    * **Owner:** Squad ou Email responsável.
    * **Ambiente:** `dev`, `hml` ou `prd`.
5.  Clique no botão verde **Run workflow**.

✅ **Pronto!** Em menos de 1 minuto, seu dashboard estará disponível no Grafana dentro da pasta **"Dashboards Automáticos (CI/CD)"**.

---

## 🛠️ Detalhes Técnicos (Para Mantenedores)

Se você precisa evoluir esta plataforma, aqui está como ela funciona "por baixo do capô":

### Estrutura do Repositório
```text
.
├── .github/workflows/   # Definição do Formulário e Pipeline (YAML)
├── terraform/           # Código IaC que conversa com o Grafana
│   ├── main.tf          # Lógica principal e Provider
│   └── ...
└── templates/           # Modelos JSON parametrizados
    ├── goldensignals.json
    └── ...