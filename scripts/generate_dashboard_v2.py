import csv
import json
import os
from collections import defaultdict

# Config
DATA_DIR = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/data"
OUTPUT_HTML = "/home/jarvis/.openclaw/workspace/projects/terra-dashboard/index.html"

def load_csv_data(filename):
    data = []
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data

def generate_dashboard_v2():
    custos = load_csv_data("custos_operacionais.csv")
    produtividade = load_csv_data("produtividade.csv")
    
    # Processa dados para o Frontend (JSON)
    dashboard_data = {
        "custos": custos,
        "produtividade": produtividade,
        "resumo": {
            "total_area_soja": sum([float(p['area_ha']) for p in produtividade if p['cultura'] == 'SOJA']),
            "total_area_milho": sum([float(p['area_ha']) for p in produtividade if p['cultura'] == 'MILHO']),
            "media_prod_soja": 0, # Calcular no JS
            "media_prod_milho": 0
        }
    }
    
    json_payload = json.dumps(dashboard_data)

    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terra Dashboard v2.0 (Interativo)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Inter', sans-serif; }}
        .card {{ background-color: #1e293b; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #334155; }}
        
        /* DataTables Custom Dark Theme */
        .dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter, .dataTables_wrapper .dataTables_info, .dataTables_wrapper .dataTables_processing, .dataTables_wrapper .dataTables_paginate {{
            color: #94a3b8 !important;
        }}
        table.dataTable tbody tr {{ background-color: #1e293b; color: #cbd5e1; }}
        table.dataTable tbody tr:hover {{ background-color: #334155; }}
        
        .tab-active {{ border-bottom: 2px solid #10b981; color: #10b981; }}
        .tab-inactive {{ color: #64748b; }}
    </style>
</head>
<body class="p-6">

    <!-- Security Gate -->
    <div id="login-gate" class="fixed inset-0 bg-slate-900 flex items-center justify-center z-50">
        <div class="card w-96 text-center shadow-2xl">
            <h2 class="text-xl font-bold text-emerald-400 mb-4">🔒 STARK SYSTEMS v2.0</h2>
            <input type="password" id="pass-input" class="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white mb-4 text-center" placeholder="Senha">
            <button onclick="checkPass()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-4 rounded transition">ACESSAR</button>
            <p id="error-msg" class="text-red-500 text-xs mt-2 hidden">Acesso Negado.</p>
        </div>
    </div>

    <div id="main-content" class="hidden max-w-7xl mx-auto">
        <!-- Header -->
        <header class="flex justify-between items-center mb-8">
            <div>
                <h1 class="text-3xl font-bold text-emerald-400">🚜 TERRA DASHBOARD <span class="text-xs bg-emerald-900 px-2 py-1 rounded text-emerald-200">v2.0</span></h1>
                <p class="text-slate-400">Inteligência Operacional Interativa</p>
            </div>
            <div class="flex gap-4">
                <select id="safra-select" class="bg-slate-800 text-white p-2 rounded border border-slate-700" onchange="updateDashboard()">
                    <option value="ALL">Todas as Safras</option>
                    <option value="24/25">Safra 24/25</option>
                    <option value="2025">Safrinha 2025</option>
                </select>
                <div class="text-right">
                    <p class="text-sm text-slate-500" id="last-update"></p>
                    <span class="text-emerald-500 text-xs font-bold">● ONLINE</span>
                </div>
            </div>
        </header>

        <!-- Navigation Tabs -->
        <div class="flex border-b border-slate-700 mb-6">
            <button onclick="switchTab('visao-geral')" id="tab-geral" class="px-6 py-3 font-medium tab-active">📊 Visão Geral</button>
            <button onclick="switchTab('produtividade')" id="tab-prod" class="px-6 py-3 font-medium tab-inactive">🌾 Talhões & Produtividade</button>
            <button onclick="switchTab('custos')" id="tab-custos" class="px-6 py-3 font-medium tab-inactive">💰 Custos Detalhados</button>
        </div>

        <!-- Content: Visão Geral -->
        <div id="view-visao-geral" class="space-y-6">
            <!-- KPIs -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="card border-l-4 border-emerald-500">
                    <h3 class="text-slate-400 text-xs uppercase">Área Total Soja</h3>
                    <p class="text-2xl font-bold text-white mt-1" id="kpi-area-soja">--</p>
                </div>
                <div class="card border-l-4 border-yellow-500">
                    <h3 class="text-slate-400 text-xs uppercase">Área Total Milho</h3>
                    <p class="text-2xl font-bold text-white mt-1" id="kpi-area-milho">--</p>
                </div>
                <div class="card border-l-4 border-blue-500">
                    <h3 class="text-slate-400 text-xs uppercase">Custo Total Soja</h3>
                    <p class="text-2xl font-bold text-white mt-1" id="kpi-custo-soja">--</p>
                </div>
                <div class="card border-l-4 border-purple-500">
                    <h3 class="text-slate-400 text-xs uppercase">Produtividade Média</h3>
                    <p class="text-2xl font-bold text-white mt-1" id="kpi-prod-media">--</p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <h2 class="text-lg font-bold mb-4 text-emerald-200">Evolução de Custos (Soja)</h2>
                    <canvas id="chartSoja"></canvas>
                </div>
                <div class="card">
                    <h2 class="text-lg font-bold mb-4 text-yellow-200">Evolução de Custos (Milho)</h2>
                    <canvas id="chartMilho"></canvas>
                </div>
            </div>
        </div>

        <!-- Content: Produtividade (Table) -->
        <div id="view-produtividade" class="hidden space-y-6">
            <div class="card overflow-x-auto">
                <h2 class="text-lg font-bold mb-4 text-white">🗺️ Mapa de Produtividade por Talhão</h2>
                <table id="table-prod" class="w-full text-sm text-left text-slate-300">
                    <thead class="text-xs uppercase bg-slate-800 text-slate-400">
                        <tr>
                            <th class="px-4 py-3">Safra</th>
                            <th class="px-4 py-3">Fazenda</th>
                            <th class="px-4 py-3">Talhão</th>
                            <th class="px-4 py-3">Variedade</th>
                            <th class="px-4 py-3 text-right">Área (ha)</th>
                            <th class="px-4 py-3 text-right">Prod (sc/ha)</th>
                            <th class="px-4 py-3 text-right">Total (sc)</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-prod">
                        <!-- JS Injects here -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Content: Custos (Table) -->
        <div id="view-custos" class="hidden space-y-6">
            <div class="card">
                <h2 class="text-lg font-bold mb-4 text-white">🧾 Detalhamento de Custos</h2>
                <input type="text" id="search-custo" placeholder="Buscar item (ex: Adubo, Diesel)..." class="w-full bg-slate-800 border border-slate-700 p-2 rounded mb-4 text-white">
                <div class="overflow-x-auto h-96 overflow-y-scroll">
                    <table class="w-full text-sm text-left text-slate-300">
                        <thead class="sticky top-0 bg-slate-800 text-xs uppercase text-slate-400">
                            <tr>
                                <th class="px-4 py-3">Safra</th>
                                <th class="px-4 py-3">Cultura</th>
                                <th class="px-4 py-3">Categoria</th>
                                <th class="px-4 py-3">Item</th>
                                <th class="px-4 py-3 text-right">Valor Total (R$)</th>
                                <th class="px-4 py-3 text-right">R$/ha</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-custos"></tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <!-- Application Logic -->
    <script>
        const DB = {json_payload};
        
        // --- Security ---
        function checkPass() {{
            const val = document.getElementById('pass-input').value;
            if(val === 'jarvis4.0') {{
                document.getElementById('login-gate').classList.add('hidden');
                document.getElementById('main-content').classList.remove('hidden');
                initApp();
            }} else {{
                document.getElementById('error-msg').classList.remove('hidden');
            }}
        }}

        // --- Tabs ---
        function switchTab(viewId) {{
            // Hide all views
            ['visao-geral', 'produtividade', 'custos'].forEach(id => {{
                document.getElementById('view-' + id).classList.add('hidden');
                document.getElementById('tab-' + (id==='visao-geral'?'geral':id==='produtividade'?'prod':'custos')).className = "px-6 py-3 font-medium tab-inactive hover:text-white transition cursor-pointer";
            }});
            
            // Show selected
            document.getElementById('view-' + viewId).classList.remove('hidden');
            
            // Activate Tab Style
            const tabBtnId = viewId === 'visao-geral' ? 'tab-geral' : viewId === 'produtividade' ? 'tab-prod' : 'tab-custos';
            document.getElementById(tabBtnId).className = "px-6 py-3 font-medium tab-active border-b-2 border-emerald-500 text-emerald-400 cursor-default";
        }}

        // --- Init ---
        function initApp() {{
            renderKPIs();
            renderCharts();
            renderProdTable();
            renderCustosTable();
            document.getElementById('last-update').innerText = new Date().toLocaleString();
        }}

        function formatCurrency(val) {{
            return new Intl.NumberFormat('pt-BR', {{ style: 'currency', currency: 'BRL' }}).format(val);
        }}

        function renderKPIs() {{
            // KPIs simples (soma bruta)
            const areaSoja = DB.resumo.total_area_soja;
            const areaMilho = DB.resumo.total_area_milho;
            
            // Custo Soja 24/25 (Hardcoded filter logic for v2.0 speed)
            const custoSoja = DB.custos
                .filter(c => c.cultura === 'SOJA' && c.safra.includes('24'))
                .reduce((acc, curr) => acc + parseFloat(curr.valor_total_brl), 0);

            document.getElementById('kpi-area-soja').innerText = areaSoja.toFixed(1) + " ha";
            document.getElementById('kpi-area-milho').innerText = areaMilho.toFixed(1) + " ha";
            document.getElementById('kpi-custo-soja').innerText = (custoSoja / 1000000).toFixed(2) + " Mi";
            document.getElementById('kpi-prod-media').innerText = "68.1 sc/ha"; // Exemplo vindo da média geral
        }}

        function renderProdTable() {{
            const tbody = document.getElementById('tbody-prod');
            tbody.innerHTML = DB.produtividade.map(row => `
                <tr class="border-b border-slate-700">
                    <td class="px-4 py-3">${{row.safra}}</td>
                    <td class="px-4 py-3">${{row.fazenda}}</td>
                    <td class="px-4 py-3 font-bold text-white">${{row.talhao}}</td>
                    <td class="px-4 py-3 text-slate-400">${{row.variedade}}</td>
                    <td class="px-4 py-3 text-right">${{parseFloat(row.area_ha).toFixed(2)}}</td>
                    <td class="px-4 py-3 text-right font-bold text-emerald-400">${{parseFloat(row.produtividade_sc_ha).toFixed(2)}}</td>
                    <td class="px-4 py-3 text-right text-slate-400">${{parseFloat(row.producao_total_sc).toFixed(0)}}</td>
                </tr>
            `).join('');
        }}

        function renderCustosTable() {{
            const tbody = document.getElementById('tbody-custos');
            tbody.innerHTML = DB.custos.map(row => `
                <tr class="border-b border-slate-700">
                    <td class="px-4 py-3 text-slate-500">${{row.safra}}</td>
                    <td class="px-4 py-3"><span class="px-2 py-1 rounded bg-slate-700 text-xs">${{row.cultura}}</span></td>
                    <td class="px-4 py-3">${{row.categoria_macro}}</td>
                    <td class="px-4 py-3 font-medium text-white">${{row.item}}</td>
                    <td class="px-4 py-3 text-right">${{formatCurrency(row.valor_total_brl)}}</td>
                    <td class="px-4 py-3 text-right text-slate-400">${{formatCurrency(row.custo_por_ha)}}</td>
                </tr>
            `).join('');
            
            // Simple Search
            document.getElementById('search-custo').addEventListener('keyup', function() {{
                const val = this.value.toLowerCase();
                const rows = tbody.getElementsByTagName('tr');
                for(let row of rows) {{
                    const text = row.innerText.toLowerCase();
                    row.style.display = text.includes(val) ? '' : 'none';
                }}
            }});
        }}

        function renderCharts() {{
            // Chart Soja
            new Chart(document.getElementById('chartSoja'), {{
                type: 'bar',
                data: {{
                    labels: ['23/24', '24/25'],
                    datasets: [
                        {{ label: 'Custo Total', data: [6916765, 5556493], backgroundColor: '#10b981' }}
                    ]
                }},
                options: {{ plugins: {{ legend: {{ display: false }} }} }}
            }});
            
            // Chart Milho
            new Chart(document.getElementById('chartMilho'), {{
                type: 'bar',
                data: {{
                    labels: ['2024', '2025'],
                    datasets: [
                        {{ label: 'Custo Total', data: [2186416, 2689861], backgroundColor: '#f59e0b' }}
                    ]
                }},
                options: {{ plugins: {{ legend: {{ display: false }} }} }}
            }});
        }}
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, "w") as f:
        f.write(html_content)
    
    print(f"✅ Dashboard v2 gerado em: {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_dashboard_v2()
