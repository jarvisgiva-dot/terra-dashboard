import csv
import json
import os
from collections import defaultdict

# Config
DATA_FILE = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data/custos_operacionais.csv"
OUTPUT_HTML = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/dashboard.html"

def generate_dashboard():
    # 1. Processar Dados
    data_structure = {
        "SOJA": {"labels": [], "manutencao": [], "mao_obra": [], "total": []},
        "MILHO": {"labels": [], "manutencao": [], "mao_obra": [], "total": []}
    }
    
    raw_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    
    try:
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cultura = row['cultura']
                safra = row['safra']
                cat = row['categoria_macro']
                val = float(row['valor_total_brl'])
                raw_data[cultura][safra][cat] += val
    except Exception as e:
        print(f"Erro ao ler dados: {e}")
        return

    # Formatar para Chart.js
    for cultura in ["SOJA", "MILHO"]:
        safras = sorted(raw_data[cultura].keys())
        data_structure[cultura]["labels"] = safras
        for s in safras:
            man = raw_data[cultura][s]["MANUTENÇÃO"]
            mob = raw_data[cultura][s]["MÃO DE OBRA"]
            data_structure[cultura]["manutencao"].append(man)
            data_structure[cultura]["mao_obra"].append(mob)
            data_structure[cultura]["total"].append(man + mob)

    json_data = json.dumps(data_structure)

    # 2. Template HTML (Modern Dark Theme + Security Gate)
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terra Dashboard v1.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Inter', sans-serif; }}
        .card {{ background-color: #1e293b; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
    </style>
</head>
<body class="p-6">

    <!-- Security Gate -->
    <div id="login-gate" class="fixed inset-0 bg-slate-900 flex items-center justify-center z-50">
        <div class="card w-96 text-center">
            <h2 class="text-xl font-bold text-emerald-400 mb-4">🔒 STARK SYSTEMS</h2>
            <p class="text-slate-400 mb-4 text-sm">Acesso Restrito. Identifique-se.</p>
            <input type="password" id="pass-input" class="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white mb-4" placeholder="Senha de Acesso">
            <button onclick="checkPass()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-4 rounded">ACESSAR</button>
            <p id="error-msg" class="text-red-500 text-xs mt-2 hidden">Acesso Negado.</p>
        </div>
    </div>

    <div id="main-content" class="hidden">
        <!-- Header -->
        <header class="flex justify-between items-center mb-8">
            <div>
                <h1 class="text-3xl font-bold text-emerald-400">🚜 TERRA DASHBOARD</h1>
                <p class="text-slate-400">Inteligência Operacional - Grupo Brunetta</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-slate-500">Atualizado em: <span id="date"></span></p>
                <span class="bg-emerald-900 text-emerald-300 text-xs font-medium mr-2 px-2.5 py-0.5 rounded">ONLINE</span>
            </div>
        </header>

        <!-- KPIs Row -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="card border-l-4 border-emerald-500">
                <h3 class="text-slate-400 text-sm font-medium">Custo Total Soja (24/25)</h3>
                <p class="text-2xl font-bold text-white mt-1">R$ 5.55 Mi</p>
                <p class="text-emerald-400 text-sm mt-2">🔻 -19.7% vs Safra Anterior</p>
            </div>
            <div class="card border-l-4 border-yellow-500">
                <h3 class="text-slate-400 text-sm font-medium">Custo Total Milho (2025)</h3>
                <p class="text-2xl font-bold text-white mt-1">R$ 2.69 Mi</p>
                <p class="text-red-400 text-sm mt-2">🔺 +23.0% vs Safra Anterior</p>
            </div>
            <div class="card border-l-4 border-blue-500">
                <h3 class="text-slate-400 text-sm font-medium">Eficiência Mão de Obra (Soja)</h3>
                <p class="text-2xl font-bold text-white mt-1">R$ 2.45 Mi</p>
                <p class="text-emerald-400 text-sm mt-2">📉 Redução de 25% no custo</p>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <!-- Soja Chart -->
            <div class="card">
                <h2 class="text-xl font-semibold mb-4 text-emerald-100">🌱 Evolução de Custos: SOJA</h2>
                <canvas id="chartSoja"></canvas>
            </div>
            <!-- Milho Chart -->
            <div class="card">
                <h2 class="text-xl font-semibold mb-4 text-yellow-100">🌽 Evolução de Custos: MILHO</h2>
                <canvas id="chartMilho"></canvas>
            </div>
        </div>
    </div>

    <!-- Data Logic -->
    <script>
        function checkPass() {{
            const pass = document.getElementById('pass-input').value;
            if (pass === 'jarvis4.0') {{
                document.getElementById('login-gate').classList.add('hidden');
                document.getElementById('main-content').classList.remove('hidden');
            }} else {{
                document.getElementById('error-msg').classList.remove('hidden');
            }}
        }}

        document.getElementById('date').innerText = new Date().toLocaleDateString();
        
        const RAW_DATA = {json_data};

        // Configuração Comum
        const commonOptions = {{
            responsive: true,
            plugins: {{
                legend: {{ position: 'bottom', labels: {{ color: '#cbd5e1' }} }}
            }},
            scales: {{
                y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }}
            }}
        }};

        // Gráfico Soja
        new Chart(document.getElementById('chartSoja'), {{
            type: 'bar',
            data: {{
                labels: RAW_DATA.SOJA.labels,
                datasets: [
                    {{ label: 'Manutenção', data: RAW_DATA.SOJA.manutencao, backgroundColor: '#34d399' }},
                    {{ label: 'Mão de Obra', data: RAW_DATA.SOJA.mao_obra, backgroundColor: '#0ea5e9' }}
                ]
            }},
            options: commonOptions
        }});

        // Gráfico Milho
        new Chart(document.getElementById('chartMilho'), {{
            type: 'bar',
            data: {{
                labels: RAW_DATA.MILHO.labels,
                datasets: [
                    {{ label: 'Manutenção', data: RAW_DATA.MILHO.manutencao, backgroundColor: '#facc15' }},
                    {{ label: 'Mão de Obra', data: RAW_DATA.MILHO.mao_obra, backgroundColor: '#f97316' }}
                ]
            }},
            options: commonOptions
        }});
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, "w") as f:
        f.write(html_content)
    
    print(f"✅ Dashboard gerado: {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_dashboard()
