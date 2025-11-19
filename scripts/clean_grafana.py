import requests
import sys
import os
import urllib3

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

# Função auxiliar genérica
def delete_resource(url, resource_name):
    try:
        if DRY_RUN:
            check = requests.get(url, headers=HEADERS, verify=VERIFY_SSL)
            if check.status_code == 200:
                print(f"[ENCONTRADO] {resource_name} (Seria deletado)")
            else:
                print(f"[NAO ENCONTRADO] {resource_name}")
        else:
            resp = requests.delete(url, headers=HEADERS, verify=VERIFY_SSL)
            if resp.status_code == 200 or resp.status_code == 202:
                print(f"[DELETADO] {resource_name}")
            elif resp.status_code == 404:
                print(f"[INFO] Ja nao existe: {resource_name}")
            else:
                print(f"[ERRO] Falha ao deletar {resource_name}: {resp.text}")
    except Exception as e:
        print(f"[ERRO CRITICO] Conexao falhou para {resource_name}: {str(e)}")

# Função específica para limpar regras de alerta dentro da pasta
def delete_alert_rules(folder_uid):
    # Na API do Grafana Ruler, o "Namespace" das regras geralmente é o UID da pasta
    ruler_url = f"{GRAFANA_URL}/api/ruler/grafana/api/v1/rules/{folder_uid}"
    
    try:
        if DRY_RUN:
            check = requests.get(ruler_url, headers=HEADERS, verify=VERIFY_SSL)
            if check.status_code == 200 and len(check.json()) > 0:
                print(f"[ENCONTRADO] Regras de Alerta na pasta {folder_uid} (Seriam deletadas)")
        else:
            # Tenta deletar o namespace de regras inteiro
            resp = requests.delete(ruler_url, headers=HEADERS, verify=VERIFY_SSL)
            if resp.status_code == 202 or resp.status_code == 200:
                print(f"[LIMPEZA] Regras de Alerta removidas da pasta {folder_uid}")
            elif resp.status_code == 404:
                print(f"[INFO] Nenhuma regra encontrada para limpar na pasta {folder_uid}")
            else:
                print(f"[AVISO] Nao foi possivel limpar regras via Ruler API: {resp.text}")
    except Exception as e:
        print(f"[ERRO] Falha ao limpar regras de alerta: {str(e)}")

# ---------------------------------------------------------
# 1. Buscar e Deletar Dashboards
# ---------------------------------------------------------
dash_types = ["golden", "detalhes", "rum"]
for dtype in dash_types:
    uid = f"{SERVICE_NAME}-{dtype}"
    delete_resource(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", f"Dashboard ({uid})")

# ---------------------------------------------------------
# 2. Buscar e Deletar Pasta de Alertas (e suas regras)
# ---------------------------------------------------------
# Tentamos com e sem acento para garantir
search_queries = [
    f"Alertas Automáticos (CI/CD) - {SERVICE_NAME}",
    f"Alertas Automaticos (CI/CD) - {SERVICE_NAME}"
]

folder_found = False

for query in search_queries:
    if folder_found: break
    
    try:
        resp = requests.get(f"{GRAFANA_URL}/api/search?query={query}&type=dash-folder", headers=HEADERS, verify=VERIFY_SSL)

        if resp.status_code == 200 and len(resp.json()) > 0:
            folder = resp.json()[0]
            folder_uid = folder['uid']
            folder_found = True
            
            # PASSO CRÍTICO: Deletar as regras antes da pasta
            delete_alert_rules(folder_uid)
            
            # Agora deleta a pasta
            url = f"{GRAFANA_URL}/api/folders/{folder_uid}"
            delete_resource(url, f"Pasta de Alertas ({folder['title']})")
            
    except Exception as e:
        print(f"[ERRO] Falha ao buscar pasta '{query}': {str(e)}")

if not folder_found:
    print("[INFO] Nenhuma pasta de alertas encontrada.")

print(f"--- {mode_str} Fim ---")