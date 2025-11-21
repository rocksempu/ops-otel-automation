# Lógica de Governança (Policy as Code)
locals {
  should_create = var.environment == "prd" || var.enable_alerts ? 1 : 0
}

# Datasource (Busca o UID do Prometheus já configurado no Grafana)
data "grafana_data_source" "prometheus" {
  name = "prometheus"
}

# --- NOTA: A criação da pasta foi movida para o main.tf para ser compartilhada ---

# 1. Ponto de Contato (Email da Squad)
resource "grafana_contact_point" "squad_email" {
  count = local.should_create
  name  = "${var.service_owner}-email"

  email {
    addresses = ["${var.service_owner}"]
    message   = "🚨 Alerta Crítico! Serviço: {{ service_name }} no ambiente [${var.environment}] está com problemas."
  }
}

# 2. Regra de Alerta: Alta Taxa de Erros (Golden Signal)
resource "grafana_rule_group" "golden_signals_alerts" {
  count = local.should_create

  name             = "Alertas - ${var.service_name}"
  # Aponta para a pasta do projeto (definida no main.tf)
  folder_uid       = grafana_folder.project_folder.uid
  interval_seconds = 60

  rule {
    name      = "High Error Rate - ${var.service_name}"
    condition = "C"
    for       = "2m"

    # Labels para Roteamento (Notification Policy usa isso)
    labels = {
      "service_name" = var.service_name
      "owner"        = var.service_owner
    }

    # Anotações (Runbook e Instruções)
    annotations = {
      summary = "Taxa de erro > 5% em ${var.service_name}"
      
      description = <<-EOT
        O serviço está apresentando alta taxa de erros.
        Checklist de Resolução:
        1. Verifique os logs no Dashboard de Detalhes.
        2. Cheque status de Circuit Breaker e dependências.
        3. Avalie rollback se houve deploy recente.
      EOT
      
      # Link para a documentação no Git
      runbook_url = "${var.runbook_base_url}/HighErrorRate.md?service=${var.service_name}"
    }

    # Query A: Taxa de Erro
    data {
      ref_id = "A"
      relative_time_range { from = 600; to = 0 }
      datasource_uid = data.grafana_data_source.prometheus.uid
      model = jsonencode({
        expr          = "sum(rate(http_server_requests_seconds_count{service_name=\"${var.service_name}\", outcome=\"SERVER_ERROR\"}[5m])) / sum(rate(http_server_requests_seconds_count{service_name=\"${var.service_name}\"}[5m])) * 100"
        intervalMs    = 1000
        maxDataPoints = 43200
        refId         = "A"
      })
    }

    # Query B: Reduce (Média)
    data {
      ref_id = "B"
      relative_time_range { from = 600; to = 0 }
      datasource_uid = "__expr__"
      model = jsonencode({
        expression = "A"
        type       = "reduce"
        reducer    = "mean"
        refId      = "B"
      })
    }

    # Query C: Threshold (> 5%)
    data {
      ref_id = "C"
      relative_time_range { from = 600; to = 0 }
      datasource_uid = "__expr__"
      model = jsonencode({
        expression = "B"
        type       = "threshold"
        refId      = "C"
        conditions = [{ evaluator = { params = [5], type = "gt" } }]
      })
    }
  }
}

# 3. Roteamento de Notificação (Liga o Alerta ao E-mail)
resource "grafana_notification_policy" "route_policy" {
  count = local.should_create

  contact_point = grafana_contact_point.squad_email[0].name
  group_by      = ["alertname", "service_name"]

  policy {
    contact_point = grafana_contact_point.squad_email[0].name
    
    matcher {
      label = "service_name"
      match = "="
      value = var.service_name
    }
  }
}