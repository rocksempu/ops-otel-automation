import requests
import sys
import os
import urllib3
from urllib.parse import quote

# --- CONFIGURACAO PARA LAB (Ignorar SSL) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
VERIFY_SSL = False 
# -------------------------------------------

# Configuração
GRAFANA_URL = os.environ.get("GRAFANA_URL")
GRAFANA_TOKEN = os.environ.get("GRAFANA_TOKEN")
SERVICE_NAME = sys.argv[1]

# Verifica se é Dry Run (Simulação)
DRY_RUN = False
if len(sys.argv) > 2 and sys.argv[2] == "--dry-run":
    DRY_RUN = True

if not GRAFANA_URL or not GRAFANA_TOKEN:
    print("[ERRO] Credenciais do Grafana nao encontradas.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json"
}

mode_str = "[SIMULACAO]" if DRY_RUN else "[EXECUCAO]"
print(f"--- {mode_str} Limpeza para o servico: {SERVICE_NAME} ---")

def delete_request(url, description):
    try:
        if DRY_RUN:
            check = requests.get(url, headers=HEADERS, verify=VERIFY_SSL)
            if check.status_code >= 200 and check.status_code < 300:
                print(f"[ENCONTRADO] {description} (Seria deletado)")
            elif check.status_code == 404:
                print(f"[NAO ENCONTRADO] {description}")
            else:
                # Se nao da pra fazer GET (ex: endpoint de delete only), assumimos que existe para teste
                print(f"[VERIFICAR] {description} (Endpoint nao permite checagem simples)")
        else:
            resp = requests.delete(url, headers=HEADERS, verify=VERIFY_SSL)
            if resp.status_code >= 200 and resp.status_code < 300:
                print(f"[DELETADO] {description}")
            elif resp.status_code == 404:
                print(f"[INFO] Ja nao existe: {description}")
            else:
                print(f"[ERRO] Falha ao deletar {description}: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[ERRO CRITICO] Conexao falhou: {str(e)}")

# 1. Deletar Dashboards (Mantido igual, pois funciona)
dash_types = ["golden", "detalhes", "rum"]
for dtype in dash_types:
    uid = f"{SERVICE_NAME}-{dtype}"
    delete_request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", f"Dashboard ({uid})")

# 2. Deletar Grupo de Alertas e Pasta
# Primeiro, precisamos achar o UID da pasta
search_query = f"Alertas Automáticos (CI/CD) - {SERVICE_NAME}"
# Fallback para sem acento se necessario
search_query_no_accent = f"Alertas Automaticos (CI/CD) - {SERVICE_NAME}"

folder_uid = None
folder_title = None

try:
    # Tenta com acento
    resp = requests.get(f"{GRAFANA_URL}/api/search?query={search_query}&type=dash-folder", headers=HEADERS, verify=VERIFY_SSL)
    data = resp.json()
    
    if len(data) == 0:
        # Tenta sem acento
        resp = requests.get(f"{GRAFANA_URL}/api/search?query={search_query_no_accent}&type=dash-folder", headers=HEADERS, verify=VERIFY_SSL)
        data = resp.json()

    if len(data) > 0:
        folder_uid = data[0]['uid']
        folder_title = data[0]['title']
        print(f"[INFO] Pasta de Alertas encontrada: {folder_title} ({folder_uid})")
    else:
        print("[INFO] Nenhuma pasta de alertas encontrada.")

except Exception as e:
    print(f"[ERRO] Falha ao buscar pasta: {str(e)}")

if folder_uid:
    # Definir o nome do grupo de regras (Padrão do Terraform)
    group_name = f"Alertas - {SERVICE_NAME}"
    safe_group_name = quote(group_name) # Codifica espaços para URL (%20)

    # Tenta deletar o GRUPO DE REGRAS via API de Provisionamento (Ignora travas)
    # Endpoint: DELETE /api/v1/provisioning/folder/{folder_uid}/rule-groups/{group_name}
    rule_url = f"{GRAFANA_URL}/api/v1/provisioning/folder/{folder_uid}/rule-groups/{safe_group_name}"
    
    print(f"[TENTATIVA] Deletando grupo de regras: {group_name}...")
    delete_request(rule_url, "Grupo de Regras de Alerta")

    # Agora deleta a pasta
    folder_url = f"{GRAFANA_URL}/api/folders/{folder_uid}"
    delete_request(folder_url, "Pasta de Alertas")

print(f"--- {mode_str} Fim ---")