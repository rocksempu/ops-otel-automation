terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = ">= 2.9.0"
    }
  }
}

provider "grafana" {
  url                  = var.grafana_url
  auth                 = var.grafana_auth
  # Importante para o seu Lab no Fyre:
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

# 1. PASTA UNIFICADA DO PROJETO
# Agora criamos uma pasta específica para este serviço/ambiente
# Exemplo: "Pix - api-transacoes [prd]"
resource "grafana_folder" "project_folder" {
  title = "${var.service_namespace} - ${var.service_name} [${var.environment}]"
}

# 2. DASHBOARD
# O dashboard é criado dentro da pasta específica do projeto
resource "grafana_dashboard" "self_service" {
  config_json = local.dashboard_json
  folder      = grafana_folder.project_folder.id
  overwrite   = true
}