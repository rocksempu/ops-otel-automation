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

# Função auxiliar genérica para delete simples
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
            if resp.status_code == 204 or resp.status_code == 200:
                print(f"[DELETADO] {resource_name}")
            elif resp.status_code == 404:
                print(f"[INFO] Ja nao existe: {resource_name}")
            else:
                print(f"[ERRO] Falha ao deletar {resource_name}: {resp.text}")
    except Exception as e:
        print(f"[ERRO CRITICO] Conexao falhou para {resource_name}: {str(e)}")

# Função BLINDADA para deletar regras provisionadas
def delete_provisioned_rules(folder_uid):
    # 1. Listar TODAS as regras provisionadas
    list_url = f"{GRAFANA_URL}/api/v1/provisioning/alert-rules"
    
    try:
        resp = requests.get(list_url, headers=HEADERS, verify=VERIFY_SSL)
        if resp.status_code != 200:
            print(f"[ERRO] Nao foi possivel listar regras: {resp.text}")
            return

        all_rules = resp.json()
        
        # 2. Filtrar regras que estao NESTA pasta
        rules_in_folder = [r for r in all_rules if r.get('folderUid') == folder_uid]
        
        if len(rules_in_folder) == 0:
            print(f"[INFO] Nenhuma regra encontrada dentro da pasta {folder_uid}")
            return

        # 3. Deletar uma por uma usando a API de Provisionamento (que ignora a trava)
        for rule in rules_in_folder:
            rule_uid = rule['uid']
            rule_title = rule['title']
            del_url = f"{GRAFANA_URL}/api/v1/provisioning/alert-rules/{rule_uid}"

            if DRY_RUN:
                print(f"[ENCONTRADO] Regra Provisionada '{rule_title}' (Seria deletada)")
            else:
                del_resp = requests.delete(del_url, headers=HEADERS, verify=VERIFY_SSL)
                if del_resp.status_code == 204:
                    print(f"[DELETADO] Regra Provisionada: {rule_title}")
                else:
                    print(f"[ERRO] Falha ao deletar regra {rule_title}: {del_resp.text}")

    except Exception as e:
        print(f"[ERRO] Falha na logica de regras provisionadas: {str(e)}")

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
            
            # PASSO CRÍTICO: Usar a nova função de Provisionamento
            delete_provisioned_rules(folder_uid)
            
            # Agora deleta a pasta vazia
            url = f"{GRAFANA_URL}/api/folders/{folder_uid}"
            delete_resource(url, f"Pasta de Alertas ({folder['title']})")
            
    except Exception as e:
        print(f"[ERRO] Falha ao buscar pasta '{query}': {str(e)}")

if not folder_found:
    print("[INFO] Nenhuma pasta de alertas encontrada.")

print(f"--- {mode_str} Fim ---")