# Lógica de Governança
locals {
  should_create = var.environment == "prd" || var.enable_alerts ? 1 : 0
}

# Datasource
data "grafana_data_source" "prometheus" {
  name = "prometheus"
}

# 1. Pasta
resource "grafana_folder" "alerts_folder" {
  count = local.should_create
  title = "Alertas Automáticos (CI/CD) - ${var.service_name}"
}

# 2. Ponto de Contato (Email)
resource "grafana_contact_point" "squad_email" {
  count = local.should_create
  name  = "${var.service_owner}-email"

  email {
    addresses = ["${var.service_owner}"]
    message   = "🚨 Alerta Crítico! Serviço: {{ service_name }} no ambiente [${var.environment}] está com problemas."
  }
}

# 3. Regra de Alerta
resource "grafana_rule_group" "golden_signals_alerts" {
  count = local.should_create

  name             = "Alertas - ${var.service_name}"
  folder_uid       = grafana_folder.alerts_folder[0].uid
  interval_seconds = 60

  rule {
    name      = "High Error Rate - ${var.service_name}"
    condition = "C"
    for       = "2m"

    # --- NOVO: Labels para Roteamento ---
    # Isso permite que a Notification Policy saiba para quem mandar
    labels = {
      "service_name" = var.service_name
      "owner"        = var.service_owner
    }
    # ------------------------------------

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

# 4. --- NOVO: Roteamento de Notificação ---
# CUIDADO: Em produção, isso deve ser gerenciado em um repo central.
# Aqui, estamos definindo a política raiz para a POC.
resource "grafana_notification_policy" "route_policy" {
  count = local.should_create

  # Se nenhum filtro der match, manda para o email da squad (Fallback)
  contact_point = grafana_contact_point.squad_email[0].name
  
  group_by      = ["alertname", "service_name"]

  # Rota Específica: Se o alerta tiver a label service_name igual a este serviço
  policy {
    contact_point = grafana_contact_point.squad_email[0].name
    
    matcher {
      label = "service_name"
      match = "="
      value = var.service_name
    }
  }
}