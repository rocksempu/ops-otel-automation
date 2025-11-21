import requests
import sys
import os
import urllib3
from urllib.parse import quote

# --- CONFIGURACAO (SSL Ignorado) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
VERIFY_SSL = False 
# -----------------------------------

# Configuração
GRAFANA_URL = os.environ.get("GRAFANA_URL")
GRAFANA_TOKEN = os.environ.get("GRAFANA_TOKEN")
SERVICE_NAME = sys.argv[1]

# Tenta pegar o Namespace via argumento (se nao vier, usa coringa ou busca ampla)
# Nota: Para o script ser preciso, idealmente precisariamos passar o Namespace tambem.
# Mas para manter simples, vamos buscar qualquer pasta que contenha o nome do servico.

DRY_RUN = False
if len(sys.argv) > 2 and "--dry-run" in sys.argv:
    DRY_RUN = True

if not GRAFANA_URL or not GRAFANA_TOKEN:
    print("[ERRO] Credenciais nao encontradas.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json"
}

mode_str = "[SIMULACAO]" if DRY_RUN else "[EXECUCAO]"
print(f"--- {mode_str} Decommission para: {SERVICE_NAME} ---")

def delete_request(url, description):
    try:
        if DRY_RUN:
            check = requests.get(url, headers=HEADERS, verify=VERIFY_SSL)
            if check.status_code >= 200 and check.status_code < 300:
                print(f"[ENCONTRADO] {description} (Seria deletado)")
            else:
                print(f"[NAO ENCONTRADO] {description} (URL: {url})")
        else:
            resp = requests.delete(url, headers=HEADERS, verify=VERIFY_SSL)
            if resp.status_code >= 200 and resp.status_code < 300:
                print(f"[DELETADO] {description}")
            elif resp.status_code == 404:
                print(f"[INFO] Ja nao existe: {description}")
            else:
                print(f"[ERRO] Falha ao deletar {description}: {resp.text}")
    except Exception as e:
        print(f"[ERRO CRITICO] Conexao falhou: {str(e)}")

# ==============================================================================
# Lógica Nova: Buscar a Pasta do Projeto pelo Nome do Serviço
# Como a pasta chama "Namespace - Servico [Env]", vamos buscar pelo trecho do nome.
# ==============================================================================

search_query = f"{SERVICE_NAME} ["
print(f"--- Buscando pastas contendo: '{search_query}' ---")

try:
    resp = requests.get(f"{GRAFANA_URL}/api/search?query={search_query}&type=dash-folder", headers=HEADERS, verify=VERIFY_SSL)
    folders = resp.json()
    
    if len(folders) == 0:
        print("[INFO] Nenhuma pasta de projeto encontrada.")
    
    for folder in folders:
        folder_uid = folder['uid']
        folder_title = folder['title']
        
        # Dupla checagem para garantir que nao estamos apagando pasta de outro servico com nome parecido
        if f"- {SERVICE_NAME} [" not in folder_title:
            print(f"[SKIP] Pulando pasta '{folder_title}' (Match inseguro)")
            continue

        print(f"--- Processando pasta: {folder_title} ({folder_uid}) ---")

        # 1. Deletar Regras de Alerta (Provisioning API)
        # O nome do grupo de regras padrao eh "Alertas - {SERVICE_NAME}"
        group_name = f"Alertas - {SERVICE_NAME}"
        safe_group_name = quote(group_name)
        
        rule_url = f"{GRAFANA_URL}/api/v1/provisioning/folder/{folder_uid}/rule-groups/{safe_group_name}"
        delete_request(rule_url, f"Grupo de Regras ({group_name})")

        # 2. Deletar a Pasta (Isso apaga os Dashboards dentro automaticamente)
        folder_url = f"{GRAFANA_URL}/api/folders/{folder_uid}"
        delete_request(folder_url, f"Pasta do Projeto ({folder_title})")

except Exception as e:
    print(f"[ERRO] Falha na busca/remocao: {str(e)}")

print(f"--- {mode_str} Fim ---")