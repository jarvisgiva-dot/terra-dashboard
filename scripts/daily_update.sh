#!/bin/bash

# Configurações de Ambiente
export GOG_KEYRING_PASSWORD="starksystems2026"
export GITHUB_TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}" # Use environment variable
PROJECT_DIR="/home/jarvis/.openclaw/workspace/projects/terra-dashboard"

echo "=========================================="
echo "🚜 TERRA DASHBOARD - DAILY UPDATE ROUTINE"
echo "Date: $(date)"
echo "=========================================="

cd $PROJECT_DIR

# 1. Sincronizar Arquivos do Drive (Novos PDFs)
echo "Step 1: Syncing from Drive..."
python3 scripts/sync_drive.py

# 2. Re-indexar Arquivos Locais
echo "Step 2: Indexing Files..."
python3 scripts/index_files.py

# 3. Extrair Métricas (ETL)
echo "Step 3: Extracting Metrics..."
python3 scripts/extract_scadi.py
python3 scripts/extract_metrics_v2.py

# 4. Construir Banco de Dados JSON
echo "Step 4: Building Database..."
python3 scripts/build_db.py

# 5. Publicar no GitHub
echo "Step 5: Deploying..."
git add data/
git commit -m "chore(auto): Daily update $(date +%Y-%m-%d)"
git push origin master

echo "✅ SUCCESS! Dashboard updated."
