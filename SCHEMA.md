# 🚜 Terra Dashboard - Schema de Dados (v1.0)

Este documento define a estrutura do Banco de Dados Operacional (AgroDB) para o Terra Dashboard.
Objetivo: Padronizar dados de ScadiAgro, IMEA e Clima para análise cruzada.

## 1. Tabela Mestre: `custos_operacionais`
Armazena cada linha de custo extraída dos PDFs ou inputada do IMEA.

| Coluna | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id` | UUID | Identificador único | `a1b2...` |
| `data_referencia` | DATE | Data do evento ou mês de referência | `2025-01-15` |
| `safra` | STRING | Ano safra padronizado | `24/25`, `25/26` |
| `cultura` | ENUM | Cultura agrícola | `SOJA`, `MILHO`, `ALGODAO` |
| `fonte` | ENUM | Origem do dado | `SCADI` (Real), `IMEA` (Ref) |
| `fazenda` | STRING | Local de produção | `CRISTALINA`, `SÃO CRISTÓVÃO`, `MT` (Media) |
| `categoria_macro` | STRING | Agrupamento principal | `INSUMOS`, `MÃO DE OBRA`, `MANUTENÇÃO` |
| `item` | STRING | Nome detalhado do insumo/serviço | `SEMENTE DE SOJA`, `UREIA`, `GLIFOSATO` |
| `unidade_medida` | STRING | Unidade de compra/aplicação | `KG`, `L`, `SC`, `HA` |
| `valor_total_brl` | DECIMAL | Valor monetário total | `15000.00` |
| `area_aplicada_ha` | DECIMAL | Área que recebeu o insumo | `1200.5` |
| `custo_por_ha` | DECIMAL | Indicador chave (R$/ha) | `12.50` |
| `custo_por_sc` | DECIMAL | Indicador de eficiência (sc/ha) | `0.15` |

## 2. Tabela: `produtividade_real`
Dados extraídos dos relatórios de "Colheita/Produtividade".

| Coluna | Tipo | Descrição |
|---|---|---|
| `safra` | STRING | Safra |
| `fazenda` | STRING | Fazenda |
| `talhao` | STRING | Identificação do Talhão |
| `variedade` | STRING | Variedade plantada (ex: `NEO 810`) |
| `area_ha` | DECIMAL | Área do talhão |
| `producao_kg` | DECIMAL | Total colhido líquido |
| `produtividade_sc_ha`| DECIMAL | Média final do talhão |

## 3. Tabela: `contratos_venda`
Controle de receita e "Shadow Ledger" das Holdings.

| Coluna | Tipo | Descrição |
|---|---|---|
| `contrato_id` | STRING | Número do contrato |
| `comprador` | STRING | Multinacional/Trading |
| `data_venda` | DATE | Data do fechamento |
| `volume_kg` | DECIMAL | Volume vendido |
| `valor_unitario_brl` | DECIMAL | Preço por saca/ton |
| `valor_total_brl` | DECIMAL | Receita bruta |
| `status_entrega` | STRING | `ENTREGUE`, `PENDENTE`, `PARCIAL` |
| `provisao_holding` | DECIMAL | Cálculo automático (19% do Total) |

## 4. Estrutura de Pastas (Ingestão)
O script de ingestão deve reconhecer arquivos nestes caminhos:
- `fazenda/{CULTURA}/{ANO}/CUSTO*.pdf` → Tabela `custos_operacionais`
- `fazenda/{CULTURA}/{ANO}/PRODUTIVIDADE*.pdf` → Tabela `produtividade_real`
- `fazenda/{CULTURA}/{ANO}/CONTRATO*.pdf` → Tabela `contratos_venda`
