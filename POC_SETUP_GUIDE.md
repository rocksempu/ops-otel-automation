# 🔧 Guia Técnico de Implementação (Ambiente POC)

Este documento detalha a infraestrutura técnica utilizada para viabilizar a Prova de Conceito (POC) da plataforma Observability as Code no ambiente de laboratório (IBM Fyre) com restrições de rede.

> **⚠️ Atenção:** Esta configuração é específica para o cenário de Lab. Para o ambiente produtivo, consulte a seção "Transição para Produção" no final deste documento.

---

## 1. Arquitetura da POC

Devido ao isolamento de rede (o GitHub Actions na nuvem não acessa o Grafana na VPN), utilizamos um modelo **Self-Hosted Runner**:

* **Runner:** Notebook Windows conectado via VPN.
* **Executor:** O Runner recebe os jobs do GitHub e executa localmente (PowerShell).
* **Conectividade:** O Terraform e os Scripts Python rodam direto na máquina, acessando o Grafana localmente.

---

## 2. Pré-requisitos da Máquina (Runner)

Para reproduzir este ambiente, a máquina Windows deve ter:

### A. Terraform (Instalação Manual)
Devido a bloqueios de segurança em scripts wrappers, o Terraform deve ser instalado "bare-metal":
1.  Baixar o binário **AMD64** (64-bits).
2.  Local de instalação: `C:\Terraform\terraform.exe`.
3.  **Importante:** Clicar com botão direito no `.exe` -> Propriedades -> **Desbloquear (Unblock)**.

### B. Python (Para Scripts e Linting)
1.  Versão utilizada: Python 3.13+.
2.  Local: `AppData` do usuário (ex: `C:\Users\<USER>\AppData\Local\Programs\Python\Python313\`).
3.  **Libs necessárias:** Instalar `requests` via pip (`python -m pip install requests`).

---

## 3. Configuração do Serviço (GitHub Runner)

O Runner foi instalado como um **Serviço do Windows** para rodar em background, mas exigiu ajustes de permissão:

1.  **Instalação:** `./config.cmd` com token do GitHub.
2.  **Modo de Serviço:** `Run as Service = Yes`.
3.  **Ajuste de Logon (Crítico):**
    * Por padrão, o serviço roda como `Network Service` (sem permissão em pastas de usuário).
    * **Alteração:** No `services.msc`, o serviço foi alterado para logar como **Local System Account** (Conta do Sistema Local) com permissão de interagir com a área de trabalho.

---

## 4. Adaptações no Código (Workarounds)

Para funcionar neste ambiente Windows/Lab, as seguintes adaptações foram feitas nos Workflows YAML e Scripts:

1.  **Caminhos Absolutos:** O Runner não carrega o PATH do usuário confiavelmente.
    * Chamadas do Terraform usam: `& "C:\Terraform\terraform.exe"`
    * Chamadas do Python usam: `& "C:\Users\...\python.exe"`
2.  **SSL Ignorado:**
    * Terraform: `insecure_skip_verify = true` (no provider).
    * Python: `verify=False` e `urllib3.disable_warnings` (nos scripts).
    * *Motivo:* Certificados auto-assinados do ambiente Fyre.
3.  **Sintaxe PowerShell:** Uso de crase (`` ` ``) para quebra de linha e `&` para execução de comandos.

---

## 5. 🗺️ Transição para Produção (To-Be)

Quando esta solução for implantada no ambiente produtivo corporativo, as seguintes mudanças devem ser aplicadas:

| Componente | POC (Atual) | Produção (Alvo) | Ação Necessária |
| :--- | :--- | :--- | :--- |
| **Runner** | Windows Laptop (VPN) | **Linux Pod (OpenShift)** | Alterar `runs-on` para o grupo de runners do OCP. Remover caminhos absolutos do Windows (`C:\...`). |
| **Terraform** | Binário Local | **Container Image** | Usar imagem Docker padrão com Terraform instalado. Remover a instalação manual. |
| **Autenticação** | Token Pessoal | **Vault / K8s Secret** | Injetar credenciais via Vault ou Secrets do GitHub Organization. |
| **Estado (State)** | Local (`.tfstate`) | **Remote Backend** | Configurar backend S3/Azure Blob para persistência do estado e *Locking*. |
| **Decommission** | Script Python (API) | **Terraform Destroy** | Com o Remote Backend, podemos usar o comando nativo `terraform destroy`, eliminando o script Python. |
| **Segurança** | SSL Ignorado | **SSL Válido** | Remover flags `insecure_skip_verify` e `verify=False`. |

---

**Mantenedor da POC:** Fabio Paixao
**Data:** Novembro/2025