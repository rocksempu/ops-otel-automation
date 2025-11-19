# Lógica de Governança (Policy as Code)
locals {
  should_create = var.environment == "prd" || var.enable_alerts ? 1 : 0
}

# 1. Pasta para os Alertas
resource "grafana_folder" "alerts_folder" {
  count = local.should_create
  title = "Alertas Automáticos (CI/CD) - ${var.service_name}"
}

# 2. Ponto de Contato (Email da Squad)
resource "grafana_contact_point" "squad_email" {
  count = local.should_create
  name  = "${var.service_owner}-email"

  email {
    addresses = ["${var.service_owner}"]
    message   = "Alerta Crítico - Serviço: {{ service_name }} [${var.environment}]"
  }
}

# 3. Regra de Alerta: Alta Taxa de Erros (Golden Signal)
resource "grafana_rule_group" "golden_signals_alerts" {
  count = local.should_create

  name             = "Alertas - ${var.service_name}"
  folder_uid       = grafana_folder.alerts_folder[0].uid
  interval_seconds = 60
  # org_id = 1  <-- LINHA REMOVIDA (O erro estava aqui)

  rule {
    name      = "High Error Rate - ${var.service_name}"
    condition = "C"
    for       = "2m"

    # Query A: Pega a taxa de erro do Prometheus
    data {
      ref_id = "A"
      relative_time_range {
        from = 600
        to   = 0
      }
      datasource_uid = "Prometheus"
      model = jsonencode({
        expr          = "sum(rate(http_server_requests_seconds_count{service_name=\"${var.service_name}\", outcome=\"SERVER_ERROR\"}[5m])) / sum(rate(http_server_requests_seconds_count{service_name=\"${var.service_name}\"}[5m])) * 100"
        intervalMs    = 1000
        maxDataPoints = 43200
        refId         = "A"
      })
    }

    # Query B: Reduz para a média
    data {
      ref_id = "B"
      relative_time_range {
        from = 600
        to   = 0
      }
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
      relative_time_range {
        from = 600
        to   = 0
      }
      datasource_uid = "__expr__"
      model = jsonencode({
        expression = "B"
        type       = "threshold"
        refId      = "C"
        conditions = [
          {
            evaluator = { params = [5], type = "gt" }
          }
        ]
      })
    }
  }
}