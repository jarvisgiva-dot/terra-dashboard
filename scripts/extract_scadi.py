import os
import json
import re
import csv
import subprocess
from datetime import datetime

# Config
BASE_DIR = "/home/jarvis/.openclaw/workspace/fazenda"
DATA_DIR = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data"
INDEX_FILE = os.path.join(DATA_DIR, "file_index.json")
DB_FILE = os.path.join(DATA_DIR, "custos_operacionais.csv")

def parse_currency(value_str):
    """Converte 'R$ 1.234,56' para float 1234.56"""
    if not value_str: return 0.0
    clean = value_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0

def extract_text_from_pdf(pdf_path):
    """Usa pdftotext -layout para extrair texto mantendo colunas."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao ler PDF {pdf_path}: {e}")
        return ""

def parse_custo_line(line):
    """
    Tenta extrair dados de uma linha do relatório CUSTO POR CATEGORIA.
    Exemplo de linha:
    2024/2025  SOJA  MÃO DE OBRA  Salários  R$ 1.078.965,88  R$ 214,46  1,7302 sc/ha
    """
    # Regex flexível para capturar colunas separadas por múltiplos espaços
    # Grupo 1: Safra (Ex: 2024/2025)
    # Grupo 2: Cultura (Ex: SOJA)
    # Grupo 3: Aplicação (Ex: MÃO DE OBRA)
    # Grupo 4: Categoria/Item (Ex: Salários) - Pode ter espaços
    # Grupo 5: Valor Total (Ex: R$ 1.000,00)
    
    # Estratégia: Split por múltiplos espaços (2 ou mais)
    parts = re.split(r'\s{2,}', line.strip())
    
    if len(parts) < 5:
        return None
        
    # Validação básica: primeiro campo parece ano?
    if not re.match(r'20\d{2}', parts[0]):
        return None

    try:
        safra = parts[0]
        cultura = parts[1]
        aplicacao = parts[2]
        
        # Acha o índice onde tem "R$"
        valor_idx = -1
        for i, p in enumerate(parts):
            if "R$" in p:
                valor_idx = i
                break
        
        if valor_idx == -1: return None
        
        item = " ".join(parts[3:valor_idx])
        
        # Lógica corrigida para R$ separado do valor
        # Cenário 1: "R$ 1.000,00" (junto) -> parts[valor_idx] é o valor
        # Cenário 2: "R$" ... "1.000,00" (separado) -> parts[valor_idx] é R$, valor é próximo
        
        raw_val_str = parts[valor_idx]
        custo_ha_str = "0"
        
        if raw_val_str.strip() == "R$":
            # O valor está na próxima coluna
            if len(parts) > valor_idx + 1:
                val_total = parse_currency(parts[valor_idx + 1])
                # Tenta pegar o próximo R$ (custo/ha)
                if len(parts) > valor_idx + 2:
                     # Pode ser que o próximo seja "R$" solto de novo
                     if parts[valor_idx + 2].strip() == "R$":
                         custo_ha_str = parts[valor_idx + 3] if len(parts) > valor_idx + 3 else "0"
                     else:
                         custo_ha_str = parts[valor_idx + 2]
            else:
                val_total = 0.0
        else:
            # O valor está junto (Ex: "R$1.000,00")
            val_total = parse_currency(raw_val_str)
            # Tenta pegar custo ha (pode ser a prox coluna ou R$ + prox)
            if len(parts) > valor_idx + 1:
                if "R$" in parts[valor_idx+1]:
                     if parts[valor_idx+1].strip() == "R$":
                         custo_ha_str = parts[valor_idx+2] if len(parts) > valor_idx+2 else "0"
                     else:
                         custo_ha_str = parts[valor_idx+1]
                else:
                     custo_ha_str = parts[valor_idx+1]

        custo_ha = parse_currency(custo_ha_str)
        
        return {
            "safra": safra,
            "cultura": cultura,
            "categoria_macro": aplicacao,
            "item": item,
            "valor_total_brl": val_total,
            "custo_por_ha": custo_ha,
            "fonte": "SCADI"
        }
    except Exception as e:
        # print(f"Erro parse linha: {line} -> {e}")
        return None

def run_extraction():
    # 1. Carrega Index
    with open(INDEX_FILE, "r") as f:
        index = json.load(f)
    
    extracted_data = []
    
    print(f"🚜 Iniciando extração de {len(index['files'])} arquivos...")
    
    # 2. Itera arquivos
    for entry in index['files']:
        if entry['tipo'] == "CUSTO" and "CATEGORIA" in entry['filename']:
            print(f"   ↳ Processando: {entry['filename']}")
            text = extract_text_from_pdf(entry['path'])
            
            for line in text.split('\n'):
                data = parse_custo_line(line)
                if data:
                    # Adiciona metadados extras
                    data['arquivo_origem'] = entry['filename']
                    data['fazenda'] = "CONSOLIDADO" # Assumindo consolidado por enquanto
                    extracted_data.append(data)

    # 3. Salva CSV
    if extracted_data:
        keys = extracted_data[0].keys()
        with open(DB_FILE, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(extracted_data)
        
        print(f"\n✅ Sucesso! {len(extracted_data)} registros de custo extraídos.")
        print(f"📊 Banco de dados salvo em: {DB_FILE}")
    else:
        print("\n⚠️ Nenhum dado de custo extraído. Verifique os layouts.")

if __name__ == "__main__":
    run_extraction()
