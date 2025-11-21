# 🔧 Guia Técnico de Implementação (Ambiente POC)

Este documento detalha a infraestrutura técnica utilizada para viabilizar a Prova de Conceito (POC) da plataforma **Observability as Code** no ambiente de laboratório (IBM Fyre) com restrições de rede.

> **⚠️ Atenção:** Esta configuração é específica para o cenário de Lab/VPN. Para o ambiente produtivo, consulte a seção "Transição para Produção" no final deste documento.

---

## 1. Arquitetura da POC

Devido ao isolamento de rede (o GitHub Actions na nuvem não acessa o Grafana na VPN interna), utilizamos um modelo **Self-Hosted Runner**:

* **Runner:** Notebook/VM Windows conectado via VPN.
* **Executor:** O Runner recebe os jobs do GitHub e executa localmente (PowerShell).
* **Conectividade:** O Terraform e os Scripts Python rodam direto na máquina, acessando o Grafana localmente (`https://grafana-grafana...`).

---

## 2. Pré-requisitos da Máquina (Runner)

Para reproduzir este ambiente, a máquina Windows deve ter:

### A. Terraform (Instalação Manual)
Devido a bloqueios de segurança em scripts wrappers do GitHub Actions, o Terraform deve ser instalado "bare-metal":
1.  Baixar o binário **AMD64** (64-bits) do site oficial.
2.  Extrair em: `C:\Terraform\terraform.exe`.
3.  **Importante:** Clicar com botão direito no `.exe` -> Propriedades -> Marcar **Desbloquear (Unblock)**.

### B. Python (Para Scripts de Decommission e Linting)
1.  Versão utilizada: Python 3.13+.
2.  Local: Geralmente em `AppData` do usuário (ex: `C:\Users\<USER>\AppData\Local\Programs\Python\Python313\`).
3.  **Bibliotecas:** Instalar `requests` via pip:
    ```powershell
    python -m pip install requests
    ```

---

## 3. Configuração do Serviço (GitHub Runner)

O Runner foi instalado como um **Serviço do Windows** para rodar em background, mas exigiu ajustes críticos de permissão:

1.  **Instalação:** `./config.cmd` usando o token do GitHub.
2.  **Modo de Serviço:** Selecionar `Run as Service = Yes`.
3.  **Ajuste de Logon (Crítico):**
    * Por padrão, o serviço roda como `Network Service` (que não tem permissão total em pastas de usuário ou rede em alguns casos).
    * **Ação:** No `services.msc`, o serviço `actions.runner.*` foi alterado para logar como **Local System Account** (Conta do Sistema Local) com a opção "Permitir que o serviço interaja com a área de trabalho" marcada.

---

## 4. Adaptações no Código (Workarounds & Soluções)

Para funcionar neste ambiente Windows/Lab e contornar travas do Grafana, as seguintes adaptações foram feitas nos Workflows e Scripts:

1.  **Caminhos Absolutos (YAML):**
    * O Runner do Windows nem sempre carrega o PATH do usuário corretamente.
    * **Solução:** Chamadas de sistema no `create-dashboard.yaml` e `destroy-dashboard.yaml` utilizam caminhos completos.
    * Exemplo: `& "C:\Users\FabioPaixao\...\python.exe" ...`

2.  **SSL Ignorado (Ambiente de Lab):**
    * O Grafana roda sobre HTTPS com certificado auto-assinado.
    * **Terraform:** Configurado `insecure_skip_verify = true` no provider.
    * **Python:** Configurado `verify=False` nas requisições e `urllib3.disable_warnings` para limpar o log.

3.  **Bypass de Travas de Provisionamento (Decommission):**
    * **Problema:** O Grafana bloqueia a deleção manual ou via API comum de recursos criados via Terraform (Status: *Provisioned*).
    * **Solução:** O script `clean_grafana.py` utiliza a **Provisioning API** (`DELETE /api/v1/provisioning/folder/{uid}/rule-groups/{group}`) em vez da Ruler API padrão. Isso força a remoção das regras de alerta, permitindo que a pasta seja excluída posteriormente.

4.  **Compatibilidade de Terminal (Encoding):**
    * O script Python evita o uso de Emojis ou caracteres especiais nos logs para prevenir erros de `UnicodeEncodeError` no console padrão do Windows (CP1252).

---

## 5. 🗺️ Transição para Produção (To-Be)

Quando esta solução for implantada no ambiente produtivo corporativo, as seguintes mudanças devem ser aplicadas para garantir segurança e escalabilidade:

| Componente | POC (Atual) | Produção (Alvo) | Ação Necessária |
| :--- | :--- | :--- | :--- |
| **Runner** | Windows Laptop (VPN) | **Linux Pod (OpenShift)** | Alterar `runs-on` para o grupo de runners do OCP. Remover caminhos absolutos do Windows (`C:\...`). |
| **Terraform** | Binário Local | **Container Image** | Usar imagem Docker padrão com Terraform instalado. Remover a instalação manual. |
| **Autenticação** | Token Pessoal | **Vault / K8s Secret** | Injetar credenciais via Vault ou Secrets do GitHub Organization. |
| **Estado (State)** | Local (`.tfstate`) | **Remote Backend** | Configurar backend S3/Azure Blob para persistência do estado e *Locking*. |
| **Decommission** | Script Python (API) | **Terraform Destroy** | Com o Remote Backend configurado, podemos usar o comando nativo `terraform destroy`, eliminando a necessidade do script Python auxiliar. |
| **Segurança** | SSL Ignorado | **SSL Válido** | Remover flags `insecure_skip_verify` e `verify=False`. |

---

**Mantenedor da POC:** Fabio Paixao
**Data:** Novembro/2025