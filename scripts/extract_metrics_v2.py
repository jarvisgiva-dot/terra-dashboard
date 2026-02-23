import os
import json
import re
import csv
import subprocess

# Config
DATA_DIR = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data"
INDEX_FILE = os.path.join(DATA_DIR, "file_index.json")
PROD_DB_FILE = os.path.join(DATA_DIR, "produtividade.csv")
CONTRACT_DB_FILE = os.path.join(DATA_DIR, "contratos.csv")

def extract_text_from_pdf(pdf_path):
    try:
        result = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception:
        return ""

def parse_decimal(val):
    if not val: return 0.0
    return float(val.replace(".", "").replace(",", ".").strip())

def extract_productivity():
    with open(INDEX_FILE, "r") as f: index = json.load(f)
    data = []
    
    print("🚜 Extraindo Produtividade (Regex Avançado)...")
    
    for entry in index['files']:
        if entry['tipo'] == "PRODUTIVIDADE":
            print(f"   ↳ Lendo: {entry['filename']}")
            text = extract_text_from_pdf(entry['path'])
            lines = text.split('\n')
            
            current_lavoura = "DESCONHECIDA"
            
            for line in lines:
                # Detecta Lavoura (Ex: Lavoura : 010 - SOJA - FAZENDA CRISTALINA)
                if "Lavoura :" in line:
                    match = re.search(r'Lavoura\s*:\s*\d+\s*-\s*([^-]+)\s*-\s*(.+)', line)
                    if match:
                        current_lavoura = match.group(2).strip() # Ex: FAZENDA CRISTALINA
                    continue

                # Detecta linha de dados (Ex: 1 CR  S NEO 810  231,91 ...)
                # Regex: Começa com algo que não é espaço, tem numeros com virgula no meio
                if re.search(r'\d+,\d{2}\s+\d+,\d{2}', line) and "Totais" not in line and "Talhão" not in line:
                    parts = re.split(r'\s{2,}', line.strip())
                    
                    if len(parts) >= 8: # Precisa ter várias colunas
                        try:
                            # Mapeamento baseado no layout visualizado
                            talhao = parts[0]
                            variedade = parts[1]
                            area_plantada = parse_decimal(parts[2])
                            
                            # A produtividade liquida (sc/ha) é a última coluna
                            prod_sc_ha_liq = parse_decimal(parts[-1])
                            
                            # A produção total liquida (sc) é a antepenúltima (3a de tras pra frente)
                            prod_total_sc = parse_decimal(parts[-3])

                            data.append({
                                "safra": entry['ano_safra'] if entry['ano_safra'] != "DESCONHECIDO" else "24/25",
                                "cultura": entry['cultura'],
                                "fazenda": current_lavoura,
                                "talhao": talhao,
                                "variedade": variedade,
                                "area_ha": area_plantada,
                                "produtividade_sc_ha": prod_sc_ha_liq,
                                "producao_total_sc": prod_total_sc
                            })
                        except Exception as e:
                            # print(f"Erro parse linha: {line} -> {e}")
                            continue

    if data:
        with open(PROD_DB_FILE, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ {len(data)} registros de produtividade salvos.")
    else:
        print("⚠️ Nenhum dado de produtividade extraído.")

def extract_contracts():
    # Placeholder simplificado para contratos (foco na produtividade agora)
    pass

if __name__ == "__main__":
    extract_productivity()
