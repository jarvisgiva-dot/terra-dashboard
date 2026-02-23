import csv
import json
import os

# Config
DATA_DIR = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data"
OUTPUT_DB = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data/database.json"

def clean_currency(val):
    if isinstance(val, str):
        return float(val.replace("R$", "").replace(".", "").replace(",", ".").strip())
    return val

def clean_decimal(val):
    if isinstance(val, str):
        return float(val.replace(".", "").replace(",", ".").strip())
    return val

def normalize_safra(val, cultura):
    """Padroniza safras para YY/YY"""
    val = str(val).strip()
    
    # Caso: 2024/2025 -> 24/25
    if "/" in val:
        parts = val.split("/")
        if len(parts[0]) == 4:
            return f"{parts[0][-2:]}/{parts[1][-2:]}"
    
    # Caso: 2023.2024 -> 23/24
    if "." in val:
        parts = val.split(".")
        if len(parts[0]) == 4:
            return f"{parts[0][-2:]}/{parts[1][-2:]}"

    # Caso: 2025 (Ano único)
    if len(val) == 4 and val.isdigit():
        if cultura == "SOJA":
            # Soja 2025 = Safra 24/25
            ano = int(val)
            return f"{str(ano-1)[-2:]}/{str(ano)[-2:]}"
        # Milho 2025 = 2025
        return val 
        
    return val

def build_bi_database():
    print("🏗️ Construindo AgroDB (JSON Relacional)...")
    
    # 1. Carregar Custos
    custos = []
    try:
        with open(os.path.join(DATA_DIR, "custos_operacionais.csv"), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                safra = normalize_safra(row['safra'], row['cultura'])
                
                custos.append({
                    "safra": safra,
                    "cultura": row['cultura'],
                    "categoria": row['categoria_macro'],
                    "item": row['item'],
                    "valor": float(row['valor_total_brl']),
                    "custo_ha": float(row['custo_por_ha'])
                })
    except Exception as e:
        print(f"Erro custos: {e}")

    # 2. Carregar Produtividade
    produtividade = []
    try:
        with open(os.path.join(DATA_DIR, "produtividade.csv"), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                safra = normalize_safra(row['safra'], row['cultura'])
                produtividade.append({
                    "safra": safra,
                    "cultura": row['cultura'],
                    "fazenda": row['fazenda'],
                    "talhao": row['talhao'],
                    "variedade": row['variedade'],
                    "area": float(row['area_ha']),
                    "prod_sc_ha": float(row['produtividade_sc_ha']),
                    "total_sc": float(row['producao_total_sc'])
                })
    except Exception as e:
        print(f"Erro produtividade: {e}")

    # 3. Consolidar IMEA (Referencia Estática por enquanto)
    # Futuramente isso virá de um CSV separado
    imea_refs = [
        {"safra": "24/25", "cultura": "SOJA", "ref_custo_ha": 4156.03, "ref_prod_sc_ha": 62.0},
        {"safra": "2025", "cultura": "MILHO", "ref_custo_ha": 3558.08, "ref_prod_sc_ha": 110.0},
    ]

    # Estrutura Final
    db = {
        "custos": custos,
        "produtividade": produtividade,
        "referencias": imea_refs,
        "metadata": {
            "updated_at": "Today",
            "version": "3.0"
        }
    }

    with open(OUTPUT_DB, "w") as f:
        json.dump(db, f, ensure_ascii=False)
    
    print(f"✅ Database gerado com sucesso: {OUTPUT_DB}")

if __name__ == "__main__":
    build_bi_database()
