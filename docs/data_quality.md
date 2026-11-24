# Qualidade dos dados

> Gerado automaticamente por `etl/04_documentar.py` a partir do log de `etl/02_transform.py`.

## Origem dos dados por tabela e ano

| Tabela | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| Atracacao | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência |
| TemposAtracacao | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência |
| Carga | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência |
| TemposAtracacaoParalisacao | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência | espelho de contingência |

## Regras e linhas afetadas

| Regra | O que faz |
|---|---|
| R1 | Linhas de carga com `FlagMCOperacaoCarga` ≠ 1 (safamento, remoção a bordo, transferência interna, operação intermediária, abastecimento) ficam fora da tonelagem — metodologia ANTAQ. |
| R2 | Atracação sem data de desatracação ou fora de 2021–2026 é excluída. |
| R3 | Tempo negativo é descartado (vira nulo). Tonelagem nunca é descartada. |
| R4 | Tempo ausente na base (falta a data de chegada/início/fim de operação): fica nulo e é ignorado nas médias/medianas daquela métrica. |
| R5 | Tempo acima do percentil 99,5 da natureza de carga predominante da atracação é limitado ao percentil (winsorização). Só tempos. |
| R6 / R6b | Paralisação com duração negativa ou sem data é descartada; acima do P99,5 da natureza é limitada. |
| R7 | Texto com acentuação corrompida (UTF-8 lido como Latin-1, ex.: `BaldeaÃ§Ã£o`) é corrigido. |
| R8 | Toda carga conteinerizada é agrupada na mercadoria "Contêineres" (como no Anuário ANTAQ). |
| R9 | Carga sem atracação correspondente (órfã) é excluída. |
| R10 | Tempo de operação maior que o tempo atracado (inconsistente) é descartado. |
| R11 | Atracação sem movimentação de carga (apoio, passageiros, reparo etc.) não entra em fAtracacao — não participa de nenhuma métrica de eficiência. |

### Linhas afetadas por ano

| Regra (métrica) | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|
| R1 | 108.092 | 137.005 | 123.514 | 172.385 | 173.270 | 12.621 |
| R11 | 12.754 | 14.329 | 17.436 | 23.012 | 22.104 | 1.688 |
| R4 atracado | 1.124 | 1.528 | 1.217 | 1.366 | 1.316 | 129 |
| R4 espera | 8.636 | 8.580 | 5.789 | 2.543 | 1.923 | 191 |
| R4 estadia | 1.858 | 2.404 | 1.601 | 1.472 | 1.317 | 203 |
| R4 operacao | 1.289 | 1.403 | 1.283 | 1.694 | 1.759 | 177 |
| R5 atracado | 335 | 309 | 336 | 483 | 463 | 29 |
| R5 espera | 232 | 321 | 394 | 429 | 441 | 39 |
| R5 estadia | 282 | 413 | 390 | 438 | 396 | 32 |
| R5 operacao | 370 | 333 | 353 | 478 | 401 | 21 |
| R6b | 768 | 754 | 574 | 736 | 1.079 | 92 |

Toneladas fora da movimentação pela R1: 2021: 16,24 Mt; 2022: 14,38 Mt; 2023: 9,50 Mt; 2024: 13,50 Mt; 2025: 11,62 Mt; 2026: 0,93 Mt.

Regras sem nenhuma ocorrência no recorte (0 linhas em todos os anos): R3, R6, R10. A base já vem sem tempos negativos e sem operação maior que o tempo atracado; as regras continuam no código para proteger cargas futuras.

### Regras sem quebra por ano

| Regra | Tabela/coluna | Valores distintos | Linhas |
|---|---|---:|---:|
| R7 texto com encoding corrompido corrigido | stg_atracacao.berco | 226 | 203.251 |
| R7 texto com encoding corrompido corrigido | stg_atracacao.porto_atracacao | 127 | 265.127 |
| R7 texto com encoding corrompido corrigido | stg_atracacao.complexo_portuario | 24 | 245.867 |
| R7 texto com encoding corrompido corrigido | stg_atracacao.tipo_operacao | 3 | 368.355 |
| R7 texto com encoding corrompido corrigido | stg_atracacao.navegacao_atracacao | 2 | 58.810 |
| R7 texto com encoding corrompido corrigido | stg_atracacao.municipio | 35 | 212.511 |
| R7 texto com encoding corrompido corrigido | stg_atracacao.uf_nome | 10 | 240.607 |
| R7 texto com encoding corrompido corrigido | stg_carga.tipo_operacao_carga | 9 | 8.061.120 |
| R7 texto com encoding corrompido corrigido | stg_carga.navegacao | 3 | 1.298.276 |
| R7 texto com encoding corrompido corrigido | stg_carga.natureza_orig | 2 | 439.723 |
| R7 texto com encoding corrompido corrigido | stg_carga.sentido_orig | 1 | 698.539 |
| R7 texto com encoding corrompido corrigido | stg_paralisacao.motivo | 22 | 567.290 |
| R2 atracação fora do recorte ou sem data de desatracação (excluída) | — | — | 0 |
| R9 carga sem atracação correspondente (órfã, excluída) | — | — | 0 |
| R8 carga conteinerizada agrupada na mercadoria 'Contêineres' | — | — | 9.122.255 |
