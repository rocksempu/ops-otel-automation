# 📊 Observability as Code (OaC) - Dashboards & Alertas Self-Service

> **Plataforma de Observabilidade Automatizada**
> Gerencie o ciclo de vida completo da monitoria (Criação e Remoção) seguindo as melhores práticas de SRE e Governança.

---

## 🎯 O Objetivo
Este projeto implementa uma esteira de **Observability as Code**. O objetivo é democratizar a criação de monitoramento para os times de desenvolvimento, garantindo que todo serviço novo nasça com:
1.  **Visibilidade:** Dashboards completos (Golden Signals, RUM, Infra).
2.  **Proatividade:** Alertas automáticos com link direto para Runbooks de resolução.
3.  **Governança:** Tags obrigatórias e políticas de ambiente.

---

## 🛡️ Quality Assurance (Quality Gates)
Para garantir a integridade da plataforma, a pipeline executa validações automáticas antes de qualquer alteração:

* **JSON Linting:** Todos os templates na pasta `/templates` são validados sintaticamente antes do Terraform iniciar. Se um arquivo estiver quebrado, a esteira falha imediatamente (Fail Fast).

---

## 🚀 Guia de Uso (Lifecycle Management)

Toda a interação é feita via **GitHub Actions**.

### 1️⃣ Como Criar (Onboarding)
Para criar monitoria para um novo serviço:

1.  Acesse a aba **[Actions](../../actions)** deste repositório.
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

✅ **Pronto!** Em menos de 1 minuto:
* Seu dashboard estará na pasta `Dashboards Automáticos (CI/CD)`.
* Seus alertas estarão ativos e roteados para o e-mail do Owner.

### 2️⃣ Como Remover (Decommission)
Para remover dashboards e alertas de um serviço descontinuado ou criado erroneamente:

1.  Acesse a aba **[Actions](../../actions)**.
2.  Selecione o workflow **"Decommission (Simples)"**.
3.  Clique em **Run workflow**.
4.  Preencha os campos:
    * **Service Name:** O nome exato do serviço (Você pode encontrar no título do Dashboard no Grafana).
    * **Ação:**
        * `🔍 APENAS SIMULAR`: Verifica o que será apagado sem executar (Dry Run).
        * `💥 DESTRUIR DE VERDADE`: Executa a exclusão dos recursos via API.
5.  Clique no botão verde **Run workflow**.

---

## ⚠️ Aviso Importante sobre Drift

> **⛔ NUNCA delete Dashboards ou Alertas manualmente pela interface do Grafana.**

Esta plataforma utiliza o conceito de **Infrastructure as Code**. O código e a automação são a "fonte da verdade".
* Se você deletar um recurso manualmente, a pipeline pode falhar na próxima execução ou recriar o recurso inesperadamente (Drift de Configuração).
* Se precisar remover algo, utilize sempre o workflow de **Decommission** descrito acima.

---

## 👮 Política de Governança (Policy as Code)

### Regras de Ambiente
A pipeline aplica regras automáticas baseadas no ambiente selecionado:

| Ambiente | Regra de Alertas | Comportamento |
| :--- | :--- | :--- |
| **PRD (Produção)** | 🚨 **Obrigatório** | O sistema **ignora** o checkbox e força a criação dos alertas. Produção não pode ficar sem monitoria. |
| **DEV / HML** | 🔓 **Opcional** | O sistema respeita a escolha do usuário. Útil para evitar ruído em testes. |

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
* **Solução de Decommission:** Para garantir a destruição confiável, o workflow de *Decommission* utiliza um script auxiliar (Python) que interage diretamente com a API do Grafana, localizando e removendo recursos baseados no `Service Name`.

### 🔮 Roadmap (Próximos Passos)
Para evoluir esta solução para um cenário **Enterprise/Produção**, recomenda-se:

1.  **Remote Backend:** Migrar o armazenamento do `tfstate` para um object storage centralizado (AWS S3, Azure Blob Storage ou Terraform Cloud). Isso permitirá o uso nativo do comando `terraform destroy` com state locking.
2.  **Notification Policies:** Centralizar a árvore de roteamento de alertas em um repositório dedicado para evitar sobrescrita por múltiplos serviços.

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