import os
import time
# Placeholder para script de ingestão
# Futuramente integrará:
# 1. Watchdog para pasta Drive
# 2. Pipeline: PDF -> Imagem -> Vision API -> JSON -> CSV

def scan_drive_folder():
    print("Iniciando varredura da pasta fazenda/...")
    # Lógica de verificação de novos arquivos
    pass

def process_cost_pdf(filepath):
    print(f"Processando custo: {filepath}")
    # Lógica de extração
    pass

if __name__ == "__main__":
    print("TERRA Ingestion Service v0.1")
    scan_drive_folder()
