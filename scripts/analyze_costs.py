import csv
import os
from collections import defaultdict

# Config
DATA_FILE = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data/custos_operacionais.csv"

def analyze_costs():
    # Estrutura: dados[cultura][safra][categoria] = valor
    dados = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    
    try:
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cultura = row['cultura']
                safra = row['safra']
                categoria = row['categoria_macro']
                valor = float(row['valor_total_brl'])
                
                dados[cultura][safra][categoria] += valor
    except FileNotFoundError:
        print("Erro: Banco de dados não encontrado.")
        return

    # Função auxiliar para formatar moeda
    def fmt(val):
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Relatório SOJA
    print("### 🌱 SOJA: Evolução de Custos (23/24 vs 24/25)\n")
    print("| Categoria | Safra 23/24 | Safra 24/25 | Variação (%) |")
    print("|---|---|---|---|")
    
    safra_ant = "2023/2024"
    safra_atual = "2024/2025"
    
    cats_soja = set(dados['SOJA'][safra_ant].keys()) | set(dados['SOJA'][safra_atual].keys())
    
    total_ant_soja = 0
    total_atual_soja = 0

    for cat in sorted(cats_soja):
        val_ant = dados['SOJA'][safra_ant][cat]
        val_atual = dados['SOJA'][safra_atual][cat]
        
        total_ant_soja += val_ant
        total_atual_soja += val_atual
        
        diff = 0
        if val_ant > 0:
            diff = ((val_atual - val_ant) / val_ant) * 100
        
        icon = "🔺" if diff > 0 else "🔻"
        if diff == 0: icon = "➡️"
        
        print(f"| **{cat}** | {fmt(val_ant)} | {fmt(val_atual)} | {icon} {diff:+.1f}% |")

    print(f"| **TOTAL GERAL** | **{fmt(total_ant_soja)}** | **{fmt(total_atual_soja)}** | **{((total_atual_soja - total_ant_soja)/total_ant_soja)*100:+.1f}%** |")
    print("\n---\n")

    # Relatório MILHO
    print("### 🌽 MILHO: Evolução de Custos (2024 vs 2025)\n")
    print("| Categoria | Safra 2024 | Safra 2025 | Variação (%) |")
    print("|---|---|---|---|")
    
    safra_ant_milho = "2024"
    safra_atual_milho = "2025"
    
    cats_milho = set(dados['MILHO'][safra_ant_milho].keys()) | set(dados['MILHO'][safra_atual_milho].keys())
    
    total_ant_milho = 0
    total_atual_milho = 0

    for cat in sorted(cats_milho):
        val_ant = dados['MILHO'][safra_ant_milho][cat]
        val_atual = dados['MILHO'][safra_atual_milho][cat]
        
        total_ant_milho += val_ant
        total_atual_milho += val_atual
        
        diff = 0
        if val_ant > 0:
            diff = ((val_atual - val_ant) / val_ant) * 100
            
        icon = "🔺" if diff > 0 else "🔻"
        if diff == 0: icon = "➡️"

        print(f"| **{cat}** | {fmt(val_ant)} | {fmt(val_atual)} | {icon} {diff:+.1f}% |")

    if total_ant_milho > 0:
        print(f"| **TOTAL GERAL** | **{fmt(total_ant_milho)}** | **{fmt(total_atual_milho)}** | **{((total_atual_milho - total_ant_milho)/total_ant_milho)*100:+.1f}%** |")
    else:
        print(f"| **TOTAL GERAL** | **{fmt(total_ant_milho)}** | **{fmt(total_atual_milho)}** | - |")

if __name__ == "__main__":
    analyze_costs()
