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

def parse_currency(val):
    if not val: return 0.0
    return float(val.replace("R$", "").replace(".", "").replace(",", ".").strip())

def parse_decimal(val):
    if not val: return 0.0
    return float(val.replace(".", "").replace(",", ".").strip())

def extract_productivity():
    with open(INDEX_FILE, "r") as f: index = json.load(f)
    data = []
    
    print("🚜 Extraindo Produtividade...")
    
    for entry in index['files']:
        if entry['tipo'] == "PRODUTIVIDADE":
            text = extract_text_from_pdf(entry['path'])
            # Regex simples para capturar linhas de talhão:
            # Ex: 1 CR  S NEO 810  231,91  231,91 100,00  ...
            # Padrão: Nome Talhão (Texto/Num) + Variedade (Texto) + Area (Num)
            
            lines = text.split('\n')
            for line in lines:
                # Heurística: Linha que tem numeros decimais e parece ser um talhão
                if re.search(r'\d+,\d{2}\s+\d+,\d{2}', line) and not "Total" in line:
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 4:
                        try:
                            # Tentativa de mapeamento posicional (frágil, mas funcional para v1)
                            talhao = parts[0]
                            variedade = parts[1]
                            area = parse_decimal(parts[2])
                            colhido = parse_decimal(parts[3])
                            # Tenta achar produtividade (geralmente nas ultimas colunas)
                            # Assume a penultima como sc/ha
                            prod_sc_ha = parse_decimal(parts[-2]) if "sc" not in parts[-1] else parse_decimal(parts[-1])
                            
                            data.append({
                                "safra": entry['ano_safra'] if entry['ano_safra'] != "DESCONHECIDO" else "24/25", # Fallback
                                "cultura": entry['cultura'],
                                "talhao": talhao,
                                "variedade": variedade,
                                "area_ha": area,
                                "produtividade_sc_ha": prod_sc_ha
                            })
                        except:
                            continue

    if data:
        with open(PROD_DB_FILE, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ {len(data)} registros de produtividade salvos.")

def extract_contracts():
    with open(INDEX_FILE, "r") as f: index = json.load(f)
    data = []
    
    print("💰 Extraindo Contratos...")
    
    for entry in index['files']:
        if entry['tipo'] == "CONTRATO":
            text = extract_text_from_pdf(entry['path'])
            # Ex: 509  CARGILL AGRICOLA S A  Milho  20/01/2026  60.000,00  R$ 41,04  R$ 2.462.500,00
            
            lines = text.split('\n')
            for line in lines:
                if "R$" in line:
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 5:
                        try:
                            comprador = parts[1] # Geralmente nome da trading
                            vencimento = parts[3] if "/" in parts[3] else "N/A"
                            valor_total = 0.0
                            # Acha valor total
                            for p in parts:
                                if "R$" in p:
                                    v = parse_currency(p)
                                    if v > valor_total: valor_total = v
                            
                            data.append({
                                "safra": entry['ano_safra'],
                                "cultura": entry['cultura'],
                                "comprador": comprador,
                                "vencimento": vencimento,
                                "valor_total": valor_total
                            })
                        except:
                            continue
    if data:
        with open(CONTRACT_DB_FILE, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ {len(data)} contratos salvos.")

if __name__ == "__main__":
    extract_productivity()
    extract_contracts()
