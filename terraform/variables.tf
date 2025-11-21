# --- Credenciais (Secrets) ---
variable "grafana_url" {
  description = "URL do Grafana (ex: https://grafana.lab.com)"
  type        = string
}

variable "grafana_auth" {
  description = "API Token ou Service Account Token do Grafana"
  type        = string
  sensitive   = true
}

# --- Inputs do Formulário (GitHub Actions) ---
variable "template_type" {
  description = "Qual modelo de dashboard usar (goldensignals, rum, etc)"
  type        = string
}

variable "service_name" {
  description = "Nome único do serviço"
  type        = string
}

variable "service_namespace" {
  description = "Namespace ou agrupador do serviço"
  type        = string
}

variable "service_version" {
  description = "Versão do serviço"
  type        = string
  default     = "1.0.0"
}

variable "environment" {
  description = "Ambiente (dev, hml, prd)"
  type        = string
}

variable "service_owner" {
  description = "Dono do serviço (Squad ou Email)"
  type        = string
}

# --- Lógica de Controle (Policy as Code) ---
variable "enable_alerts" {
  description = "Flag para ativar ou desativar a criação de alertas (Ignorado em PRD)"
  type        = bool
  default     = true
}

# --- Configuração de Runbooks ---
variable "runbook_base_url" {
  description = "URL base onde ficam os documentos de troubleshooting"
  type        = string
  # Pode ser uma Wiki, Confluence ou uma pasta no GitHub
  default     = "https://github.com/rocksempu/ops-otel-automation/wiki/Runbooks"
}