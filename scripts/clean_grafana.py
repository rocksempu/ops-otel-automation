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
    print("Erro: Credenciais do Grafana não encontradas.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json"
}

mode_str = "[SIMULAÇÃO]" if DRY_RUN else "[EXECUÇÃO]"
print(f"--- {mode_str} Limpeza para o serviço: {SERVICE_NAME} ---")

# Função auxiliar para deletar (ou fingir)
def delete_resource(url, resource_name):
    try:
        if DRY_RUN:
            # No modo simulação, apenas verificamos se existe
            check = requests.get(url, headers=HEADERS, verify=VERIFY_SSL) # <--- SSL OFF
            if check.status_code == 200:
                print(f"🔍 ENCONTRADO: {resource_name} (Seria deletado)")
            else:
                print(f"⚪ Não encontrado: {resource_name}")
        else:
            # No modo real, deletamos
            resp = requests.delete(url, headers=HEADERS, verify=VERIFY_SSL) # <--- SSL OFF
            if resp.status_code == 200:
                print(f"✅ DELETADO: {resource_name}")
            elif resp.status_code == 404:
                print(f"ℹ️ Já não existe: {resource_name}")
            else:
                print(f"❌ Erro ao deletar {resource_name}: {resp.text}")
    except Exception as e:
        print(f"❌ Erro de conexão ao tentar acessar {resource_name}: {str(e)}")

# 1. Buscar e Deletar Dashboards
dash_types = ["golden", "detalhes", "rum"]
for dtype in dash_types:
    uid = f"{SERVICE_NAME}-{dtype}"
    delete_resource(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", f"Dashboard ({uid})")

# 2. Buscar e Deletar Pasta de Alertas
search_query = f"Alertas Automáticos (CI/CD) - {SERVICE_NAME}"
try:
    resp = requests.get(f"{GRAFANA_URL}/api/search?query={search_query}&type=dash-folder", headers=HEADERS, verify=VERIFY_SSL) # <--- SSL OFF

    if resp.status_code == 200 and len(resp.json()) > 0:
        folder = resp.json()[0]
        folder_uid = folder['uid']
        # URL especial com force=true para apagar regras dentro
        url = f"{GRAFANA_URL}/api/folders/{folder_uid}?force=true"
        delete_resource(url, f"Pasta de Alertas ({folder['title']})")
    else:
        print("⚪ Nenhuma pasta de alertas encontrada.")
except Exception as e:
    print(f"❌ Erro ao buscar pasta de alertas: {str(e)}")

print(f"--- {mode_str} Fim ---")