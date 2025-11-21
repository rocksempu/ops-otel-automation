# 🚨 Runbook: High Error Rate (Taxa de Erro Elevada)

> **Severidade:** Crítica
> **Sintoma:** O percentual de falhas (HTTP 5xx) ultrapassou o limiar de 5%.

---

## 1. Entendendo o Alerta
Este alerta dispara quando a taxa de erros `(requests_error / total_requests)` é maior que 5% numa janela de 5 minutos. Isso indica que o usuário final está enfrentando falhas.

**Serviço Afetado:** Verifique o parâmetro `service` na URL ou no título do alerta.

## 2. Diagnóstico Rápido (Triage)

### A. Verifique os Logs
1. Vá ao Dashboard de **Detalhes do Serviço** no Grafana.
2. Filtre pelo nome do serviço afetado.
3. Olhe o painel **"Logs Recentes"**. Procure por `Exception`, `Connection Refused` ou `Timeout`.

### B. Verifique Dependências
O erro é interno ou de uma dependência?
* Se os logs mostram erro de conexão com banco de dados -> O problema é no DB.
* Se os logs mostram erro chamando outra API -> O problema é no *downstream*.

### C. Verifique Mudanças Recentes
* Houve deploy nos últimos 30 minutos?
* Se sim, considere o **Rollback** imediato.

---

## 3. Ações de Mitigação

| Cenário | Ação Recomendada |
| :--- | :--- |
| **Bug no Código (Deploy recente)** | Execute o comando de Rollback via CI/CD. |
| **Banco de Dados Lento** | Verifique se há *Slow Queries* ou travamento de tabela. |
| **Dependência Fora** | Ative o *Circuit Breaker* ou página de manutenção parcial. |
| **Tráfego Anômalo (DDoS)** | Verifique o WAF e considere bloquear IPs ofensores. |

---

## 4. Escalation Policy
Se não resolver em 15 minutos:
* Acione o time de SRE no canal `#sre-war-room`.
* Abra incidente no ServiceNow com prioridade P1.