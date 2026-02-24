#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path

# PDFs to download from Google Drive
FILES_TO_DOWNLOAD = {
    "CUSTO SOJA - SAFRA 2023.2024.pdf": "1X8AkK-reAIbWS_YVm4DssF8mW9xIp9gH",
    "CUSTO SOJA - SAFRA 2024.2025.pdf": "1SQ7-8gtFYsaUnxzhv2Jb-HWuYHQZBs_y",
    "CUSTO MILHO - SAFRINHA 2024.pdf": "1KXx-NdE4EB9sD1q979vAkm_Cw9O4VB7I",
    "CUSTO MILHO - SAFRINHA 2025.pdf": "1MfQ-8kCDFkKSpIHFEVfOTolQPuTgp1oA",
}

def download_from_drive(file_id, filename):
    """Download PDF from Google Drive using gog"""
    print(f"Downloading {filename}...")
    os.system(f'export GOG_KEYRING_PASSWORD="starksystems2026" && gog drive download {file_id} --out ./data/raw/{filename}')

def main():
    Path("./data/raw").mkdir(parents=True, exist_ok=True)
    
    for filename, file_id in FILES_TO_DOWNLOAD.items():
        filepath = f"./data/raw/{filename}"
        if not Path(filepath).exists():
            download_from_drive(file_id, filename)
        else:
            print(f"✅ {filename} already exists")

if __name__ == "__main__":
    main()
