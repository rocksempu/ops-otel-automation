import requests
import sys
import os
import urllib3

# --- CONFIGURAÇÃO PARA LAB (Ignorar SSL) ---
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

# Função auxiliar para deletar (ou fingir)
def delete_resource(url, resource_name):
    try:
        if DRY_RUN:
            # No modo simulação, apenas verificamos se existe
            check = requests.get(url, headers=HEADERS, verify=VERIFY_SSL)
            if check.status_code == 200:
                print(f"[ENCONTRADO] {resource_name} (Seria deletado)")
            else:
                print(f"[NAO ENCONTRADO] {resource_name}")
        else:
            # No modo real, deletamos
            resp = requests.delete(url, headers=HEADERS, verify=VERIFY_SSL)
            if resp.status_code == 200:
                print(f"[DELETADO] {resource_name}")
            elif resp.status_code == 404:
                print(f"[INFO] Ja nao existe: {resource_name}")
            else:
                print(f"[ERRO] Falha ao deletar {resource_name}: {resp.text}")
    except Exception as e:
        print(f"[ERRO CRITICO] Conexao falhou para {resource_name}: {str(e)}")

# 1. Buscar e Deletar Dashboards
dash_types = ["golden", "detalhes", "rum"]
for dtype in dash_types:
    uid = f"{SERVICE_NAME}-{dtype}"
    delete_resource(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", f"Dashboard ({uid})")

# 2. Buscar e Deletar Pasta de Alertas
# AQUI ESTAVA O ERRO: Adicionamos o acento de volta para bater com o Terraform
search_query = f"Alertas Automáticos (CI/CD) - {SERVICE_NAME}"

try:
    resp = requests.get(f"{GRAFANA_URL}/api/search?query={search_query}&type=dash-folder", headers=HEADERS, verify=VERIFY_SSL)

    if resp.status_code == 200 and len(resp.json()) > 0:
        folder = resp.json()[0]
        folder_uid = folder['uid']
        folder_title = folder['title']
        
        # URL especial com force=true para apagar regras dentro
        url = f"{GRAFANA_URL}/api/folders/{folder_uid}?force=true"
        
        # Tratamento para evitar erro de acento no print do Windows
        try:
            print_name = f"Pasta de Alertas ({folder_title})"
        except:
            print_name = f"Pasta de Alertas (UID: {folder_uid})"

        delete_resource(url, print_name)
    else:
        print("[INFO] Nenhuma pasta de alertas encontrada.")
except Exception as e:
    print(f"[ERRO] Falha ao buscar pasta de alertas: {str(e)}")

print(f"--- {mode_str} Fim ---")