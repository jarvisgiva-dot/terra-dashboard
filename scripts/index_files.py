import os
import json
import re
from datetime import datetime

# Config
BASE_DIR = "/home/jarvis/.openclaw/workspace/fazenda"
OUTPUT_FILE = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data/file_index.json"

def classify_file(filename):
    """Identifica o tipo de documento baseado no nome."""
    name = filename.upper()
    if "CUSTO" in name:
        return "CUSTO"
    if "PRODUTIVIDADE" in name:
        return "PRODUTIVIDADE"
    if "CONTRATO" in name:
        return "CONTRATO"
    if "ESTOQUE" in name:
        return "ESTOQUE"
    return "OUTROS"

def index_files():
    index = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "root_path": BASE_DIR
        },
        "files": []
    }
    
    print(f"🔍 Iniciando varredura em: {BASE_DIR}")
    
    # Varre recursivamente
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue
                
            path = os.path.join(root, file)
            # Tenta extrair contexto do caminho (Ex: fazenda/SOJA/2025/arquivo.pdf)
            parts = path.replace(BASE_DIR, "").strip("/").split("/")
            
            cultura = "DESCONHECIDO"
            ano = "DESCONHECIDO"
            
            # Heurística simples para pasta estruturada
            if len(parts) >= 2:
                if parts[0] in ["SOJA", "MILHO"]:
                    cultura = parts[0]
                if re.match(r"20\d{2}", parts[1]): # Se parece um ano (2020-2029)
                    ano = parts[1]
            
            # Se não pegou da pasta, tenta do nome do arquivo
            if cultura == "DESCONHECIDO":
                if "SOJA" in file.upper(): cultura = "SOJA"
                if "MILHO" in file.upper(): cultura = "MILHO"
            
            doc_type = classify_file(file)
            
            entry = {
                "path": path,
                "filename": file,
                "cultura": cultura,
                "ano_safra": ano,
                "tipo": doc_type,
                "status": "PENDENTE_OCR"
            }
            
            index["files"].append(entry)
            print(f"📄 [{doc_type}] {file} ({cultura} {ano})")

    # Salva o index
    with open(OUTPUT_FILE, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Indexação concluída. {len(index['files'])} arquivos mapeados.")
    print(f"📁 Índice salvo em: {OUTPUT_FILE}")

if __name__ == "__main__":
    index_files()
