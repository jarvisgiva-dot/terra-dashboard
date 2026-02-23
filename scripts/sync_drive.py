import os
import subprocess
import json

# Config
LOCAL_DIR = "/home/jarvis/.openclaw/workspace/fazenda"
DRIVE_ROOT_ID = "1M5Zka3lEBXWrBM2T7YEYnin00oeCNBim" # ID da pasta 'fazenda'

def run_gog(args):
    """Executa comando GOG CLI e retorna JSON"""
    cmd = ["gog", "drive"] + args + ["--json"]
    # Garante que a senha está no env (o shell script wrapper vai cuidar disso, mas por segurança)
    env = os.environ.copy()
    if "GOG_KEYRING_PASSWORD" not in env:
        env["GOG_KEYRING_PASSWORD"] = "starksystems2026"
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Erro GOG: {e}")
        return []

def sync_folder(drive_id, local_path):
    """Recursivamente sincroniza pastas e baixa arquivos faltantes"""
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        
    print(f"📂 Verificando: {local_path}...")
    
    # Lista arquivos remotos
    # O comando 'ls --json' retorna uma lista de dicionários
    # Se retornar string (erro), pode causar o problema de índices
    
    items = run_gog(["ls", "--parent", drive_id])
    
    if not isinstance(items, list):
        print(f"⚠️ Erro ao listar pasta {drive_id}. Retorno inesperado.")
        return

    for item in items:
        if not isinstance(item, dict): continue
        
        name = item.get('name', 'UNKNOWN')
        fid = item.get('id')
        
        # 'type' field varies by version/output
        is_folder = (item.get('type') == 'folder') or \
                    (item.get('mimeType') == 'application/vnd.google-apps.folder')
        
        if is_folder:
            # Recursão para subpastas (ex: SOJA/2025)
            sync_folder(fid, item_local_path)
        else:
            # Arquivo: Baixa se não existir ou tamanho diferente (simplificado: se não existir)
            if not os.path.exists(item_local_path) and name.lower().endswith(".pdf"):
                print(f"⬇️ Baixando novo arquivo: {name}")
                subprocess.run(
                    ["gog", "drive", "download", fid, "--out", item_local_path],
                    env=os.environ, check=False
                )

if __name__ == "__main__":
    print("🔄 TERRA SYNC: Iniciando sincronização com Google Drive...")
    sync_folder(DRIVE_ROOT_ID, LOCAL_DIR)
    print("✅ Sincronização concluída.")
