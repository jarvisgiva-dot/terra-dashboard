#!/usr/bin/env python3
import json
import re
import subprocess
import os
from pathlib import Path

# Mapeamento de PDFs
PDF_MAP = {
    "18gXBDawVhOTx4eGla5yf4I8sD1NeY7UD": ("23/24", "SOJA", "PROD"),
    "1veHuej6p_1ITM6OLdHHzQ15HBXjY_-D5": ("22/23", "SOJA", "PROD"),
    "1nck3Fik8rj5NljlWGAq4lwzqIslN70kG": ("2024", "MILHO", "PROD"),
    "1GFOQfoFhCdQxEiAzD8is-bahpf7ggGI7": ("2025", "MILHO", "PROD"),
    "1X8AkK-reAIbWS_YVm4DssF8mW9xIp9gH": ("23/24", "SOJA", "CUSTO"),
    "1SQ7-8gtFYsaUnxzhv2Jb-HWuYHQZBs_y": ("24/25", "SOJA", "CUSTO"),
    "1KXx-NdE4EB9sD1q979vAkm_Cw9O4VB7I": ("2024", "MILHO", "CUSTO"),
    "1MfQ-8kCDFkKSpIHFEVfOTolQPuTgp1oA": ("2025", "MILHO", "CUSTO"),
}

DRIVE_DIR = "./data/raw/drive"

def get_pdf_path(file_id):
    for f in os.listdir(DRIVE_DIR):
        if file_id in f:
            return os.path.join(DRIVE_DIR, f)
    return None

def extract_text(pdf_path):
    result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'], 
                          capture_output=True, text=True)
    return result.stdout

def parse_produtividade(text, safra, cultura):
    prods = []
    lines = text.split('\n')
    
    current_fazenda = None
    
    for line in lines:
        # Detectar fazenda
        if 'FAZENDA' in line and '-' in line:
            match = re.search(r'FAZENDA ([A-ZÁÉÍÓÚ\s]+?)(?:\s*$|(?=\d))', line)
            if match:
                current_fazenda = match.group(1).strip()
        
        # Parse de linha de dados: TALHÃO VARIEDADE AREA ... PRODUTIVIDADE
        # Padrão: começa com texto (talhão), depois espaços, depois números
        # Procura pela última coluna: Produt. (Scs/Ha) que tem formato XXX,XX
        match = re.match(r'^\s*([A-Z0-9\s]+?)\s{2,}([A-Z0-9\s]+?)\s{2,}([\d.]+)\s+([\d.]+)\s+100', line)
        if match:
            try:
                talhao = match.group(1).strip()
                variedade = match.group(2).strip()
                area = float(match.group(3).replace(',', '.'))
                
                # Procura pela produtividade na linha (última coluna numérica antes de %Descontos)
                # Padrão: números com vírgula (formato brasileiro)
                numeros = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d+|\d+,\d+)', line)
                
                if len(numeros) >= 2:
                    # A produtividade em sc/ha é tipicamente um número menor (40-200)
                    # Procura pelo número que faz sentido como sc/ha
                    for num_str in numeros[-5:]:  # Procura nos últimos números
                        val = float(num_str.replace('.', '').replace(',', '.'))
                        if 30 < val < 250:  # Range típico de produtividade
                            prods.append({
                                'safra': safra,
                                'cultura': cultura,
                                'talhao': talhao,
                                'fazenda': current_fazenda or 'DESCONHECIDA',
                                'variedade': variedade,
                                'area': area,
                                'prod_sc_ha': val
                            })
                            break
            except:
                pass
    
    return prods

def parse_custos(text, safra, cultura):
    custos = []
    lines = text.split('\n')
    
    for line in lines:
        # Padrão: APLICAÇÃO SAFRA FAZENDA R$ XXX.XXX,XX ... R$ XXX,XX
        match = re.match(r'^\s*(\w+(?:\s+\w+)?)\s+(\d{4}/\d{4}|\d{4})\s+([A-ZÁÉÍÓÚ\s]+?)\s+R\$\s+([\d.]+,\d+)\s+', line)
        
        if match:
            try:
                categoria = match.group(1).strip()
                safra_pdf = match.group(2)
                fazenda = match.group(3).strip()
                valor_str = match.group(4)
                
                valor = float(valor_str.replace('.', '').replace(',', '.'))
                
                # Procura custo_ha (última coluna R$)
                valores = re.findall(r'R\$\s+([\d.]+,\d+)', line)
                custo_ha = 0
                if len(valores) >= 2:
                    custo_ha = float(valores[-1].replace('.', '').replace(',', '.'))
                
                custos.append({
                    'safra': safra,
                    'cultura': cultura,
                    'categoria': categoria,
                    'item': categoria,
                    'fazenda': fazenda,
                    'valor': valor,
                    'custo_ha': custo_ha
                })
            except:
                pass
    
    return custos

def main():
    all_prods = []
    all_custos = []
    
    print("Processando PDFs...")
    
    for file_id, (safra, cultura, tipo) in PDF_MAP.items():
        pdf_path = get_pdf_path(file_id)
        if not pdf_path:
            print(f"⚠️  {safra} {cultura} {tipo} - arquivo não encontrado")
            continue
        
        print(f"  Processando {safra} {cultura} ({tipo})...")
        text = extract_text(pdf_path)
        
        if tipo == "PROD":
            data = parse_produtividade(text, safra, cultura)
            all_prods.extend(data)
            print(f"    ✅ {len(data)} registros")
        elif tipo == "CUSTO":
            data = parse_custos(text, safra, cultura)
            all_custos.extend(data)
            print(f"    ✅ {len(data)} itens")
    
    # Montar banco completo
    db = {
        'custos': all_custos,
        'produtividade': all_prods,
        'referencias': [
            {'safra': '24/25', 'cultura': 'SOJA', 'ref_custo_ha': 4156.03, 'ref_prod_sc_ha': 62.0, 'detalhes': {}},
            {'safra': '23/24', 'cultura': 'SOJA', 'ref_custo_ha': 3800.0, 'ref_prod_sc_ha': 60.0, 'detalhes': {}},
            {'safra': '2025', 'cultura': 'MILHO', 'ref_custo_ha': 3558.08, 'ref_prod_sc_ha': 110.0, 'detalhes': {}},
            {'safra': '2024', 'cultura': 'MILHO', 'ref_custo_ha': 3300.0, 'ref_prod_sc_ha': 105.0, 'detalhes': {}},
        ],
        'metadata': {'updated_at': '2026-02-24', 'version': '5.0'}
    }
    
    with open('./data/database.json', 'w') as f:
        json.dump(db, f, indent=2)
    
    print(f"\n✅ Banco criado:")
    print(f"   - {len(all_custos)} custos")
    print(f"   - {len(all_prods)} produtividades")

if __name__ == "__main__":
    main()
