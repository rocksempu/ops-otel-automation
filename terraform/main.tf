terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = ">= 2.9.0"
    }
  }
}

# Variáveis de Conexão (Vêm das Secrets)
variable "grafana_url" {}
variable "grafana_auth" {}

# Variáveis do Formulário (Inputs do GitHub Actions)
variable "template_type" {}
variable "service_name" {}
variable "service_namespace" {}
variable "service_version" { default = "1.0.0" }
variable "environment" {}
variable "service_owner" {}

provider "grafana" {
  url  = var.grafana_url
  auth = var.grafana_auth
  insecure_skip_verify = true
}

# Lógica: Escolhe o JSON certo baseado no input
locals {
  template_file = {
    "goldensignals"      = "goldensignals.json"
    "detalhesporservico" = "detalhesporservico.json"
    "rum"                = "rum.json"
  }

  # Lê o JSON e substitui os placeholders ${...} pelos valores reais
  dashboard_json = templatefile("${path.module}/../templates/${local.template_file[var.template_type]}", {
    service_name      = var.service_name
    service_namespace = var.service_namespace
    service_owner     = var.service_owner
    service_version   = var.service_version
    environment       = var.environment
  })
}

# Cria a Pasta no Grafana (se não existir)
resource "grafana_folder" "ci_cd_folder" {
  title = "Dashboards Automáticos (CI/CD)"
}

# Cria o Dashboard dentro da pasta
resource "grafana_dashboard" "self_service" {
  config_json = local.dashboard_json
  folder      = grafana_folder.ci_cd_folder.id
  overwrite   = true
}
