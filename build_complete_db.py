#!/usr/bin/env python3
import json
import re
import subprocess
import os
from pathlib import Path

# Mapeamento: ID Drive -> (safra, tipo)
PDF_MAP = {
    # SOJA
    "18gXBDawVhOTx4eGla5yf4I8sD1NeY7UD": ("23/24", "SOJA", "PRODUTIVIDADE"),
    "1veHuej6p_1ITM6OLdHHzQ15HBXjY_-D5": ("22/23", "SOJA", "PRODUTIVIDADE"),
    "1SQ7-8gtFYsaUnxzhv2Jb-HWuYHQZBs_y": ("24/25", "SOJA", "CUSTO"),
    
    # MILHO
    "1nck3Fik8rj5NljlWGAq4lwzqIslN70kG": ("2024", "MILHO", "PRODUTIVIDADE"),
    "1GFOQfoFhCdQxEiAzD8is-bahpf7ggGI7": ("2025", "MILHO", "PRODUTIVIDADE"),
    "1MfQ-8kCDFkKSpIHFEVfOTolQPuTgp1oA": ("2025", "MILHO", "CUSTO"),
}

DOWNLOAD_DIR = "./data/raw/drive"

def get_local_file(file_id):
    """Encontra arquivo local pelo ID"""
    for f in os.listdir(DOWNLOAD_DIR):
        if file_id in f:
            return os.path.join(DOWNLOAD_DIR, f)
    return None

def extract_text(pdf_path):
    """Extrai texto do PDF"""
    result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'], 
                          capture_output=True, text=True)
    return result.stdout

def parse_produtividade(text, safra, cultura):
    """Parse produtividade do PDF"""
    prods = []
    lines = text.split('\n')
    
    for line in lines:
        # Padrão típico: TALHÃO  FAZENDA  VARIEDADE  AREA  PRODUTIVIDADE
        # Procura por padrões de números
        if 'ha' in line.lower() and 'sc' in line.lower():
            # Tenta extrair dados
            parts = line.split()
            try:
                # Simplificado: pega padrão com números
                for i, p in enumerate(parts):
                    if re.match(r'^\d+\.?\d*$', p):
                        # Pode ser área
                        if i + 1 < len(parts):
                            try:
                                area = float(p)
                                # Próximo número é produtividade?
                                for j in range(i+1, min(i+5, len(parts))):
                                    if re.match(r'^\d+\.?\d*$', parts[j]):
                                        prod = float(parts[j])
                                        if 50 < prod < 250:  # Filtro sanidade
                                            prods.append({
                                                'safra': safra,
                                                'cultura': cultura,
                                                'talhao': 'TALHAO',
                                                'area': area,
                                                'prod_sc_ha': prod
                                            })
                                        break
                            except:
                                pass
            except:
                pass
    
    return prods

def main():
    print("Processando PDFs do Drive...")
    
    all_prods = []
    
    for file_id, (safra, cultura, tipo) in PDF_MAP.items():
        pdf_path = get_local_file(file_id)
        if not pdf_path:
            print(f"⚠️  {safra} {cultura} {tipo} não encontrado")
            continue
        
        print(f"Processando {safra} {cultura} ({tipo})...")
        
        if tipo == "PRODUTIVIDADE":
            text = extract_text(pdf_path)
            prods = parse_produtividade(text, safra, cultura)
            all_prods.extend(prods)
            print(f"  ✅ {len(prods)} registros")
    
    print(f"\n✅ Total: {len(all_prods)} produtividades extraídas")
    
    # Salvar
    with open('./data/produtividade_novo.json', 'w') as f:
        json.dump(all_prods, f, indent=2)

if __name__ == "__main__":
    main()
