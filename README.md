# 🚜 TERRA DASHBOARD (Agro Metrics)
**Status:** Em Desenvolvimento (Fase 1 - Ingestão)
**Agente Responsável:** TERRA & NEXUS

## 🎯 Objetivo
Um painel de inteligência operacional focado exclusivamente no agronegócio (Fazendas Cristalina, São Cristóvão, Califórnia). 
**Isolado do Jarvis Dashboard pessoal.**

## 📊 Escopo de Dados
1.  **Custos Reais (ScadiAgro):** Ingestão automática dos PDFs da pasta `fazenda/`.
2.  **Benchmark (IMEA):** Comparativo de custos de mercado (Soja/Milho/Algodão).
3.  **Produtividade:** Histórico de sacas/ha por talhão.
4.  **Clima:** Monitoramento pluviométrico.

## 🛠️ Arquitetura (Planejada)
- **Ingestão:** Script Python (`scripts/ingest_scadi.py`) que monitora o Google Drive.
- **Processamento:** OCR/Vision AI para extrair tabelas complexas dos PDFs.
- **Banco de Dados:** SQLite/Postgres local para estruturar `custos_consolidados`.
- **Frontend:** (Futuro) Interface limpa para visualização de margem e custos.

## 🔄 Fluxo de Ingestão (Pipeline)
1.  Novo arquivo PDF detectado em `fazenda/CULTURA/ANO/`.
2.  Script analisa tipo (Custo, Contrato, Produtividade).
3.  Extração de dados via Vision Model (devido à complexidade do layout Scadi).
4.  Atualização do CSV/DB mestre.
