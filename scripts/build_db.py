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

def build_bi_database():
    print("🏗️ Construindo AgroDB (JSON Relacional)...")
    
    # 1. Carregar Custos
    custos = []
    try:
        with open(os.path.join(DATA_DIR, "custos_operacionais.csv"), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalização
                safra = row['safra'].replace(".", "/") # 2024.2025 -> 2024/2025
                if len(safra) == 4: safra = f"{safra}/{int(safra)+1}" # 2025 -> 2025/2026 (aprox)
                
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
                produtividade.append({
                    "safra": row['safra'],
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
