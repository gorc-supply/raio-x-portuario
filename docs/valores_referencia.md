# Valores de referência dos KPIs

> Gerado automaticamente por `etl/04_documentar.py` em 24/11/2026 17:33 a partir dos mesmos CSV de `data/processed/` que o Power BI lê.
> Último mês com dado: **01/2026** — o ano de 2026 é **parcial** (e o [Toneladas AA] de 2026 compara só os mesmos meses de 2025).

Use estas tabelas para conferir o Power BI número a número: selecione o ano na segmentação de período (e, para Suape, filtre a instalação) e compare com o cartão/tabela correspondente. As definições das medidas estão em [kpis.md](kpis.md).

Convenções: toneladas = soma de `VLPesoCargaBruta` com `FlagMCOperacaoCarga = 1`; período = mês da desatracação; medidas de eficiência calculadas sobre atracações com movimentação de carga, já com a limpeza de tempos aplicada (ver [data_quality.md](data_quality.md)).

## 1. Brasil (todas as instalações)

| Medida | Pasta | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---:|---:|---:|---:|---:|---:|
| [Toneladas] | Volume | 1.212.363.999 | 1.222.984.185 | 1.308.558.348 | 1.325.915.577 | 1.403.813.213 | 103.963.208 |
| [Toneladas AA] | Volume | — | 1.212.363.999 | 1.222.984.185 | 1.308.558.348 | 1.325.915.577 | 92.173.340 |
| [Var % Toneladas AA] | Volume | — | 0,9% | 7,0% | 1,3% | 5,9% | 12,8% |
| [TEU] | Volume | 11.809.056 | 11.698.314 | 11.627.756 | 13.907.873 | 15.242.491 | 1.254.739 |
| [Nº Atracações] | Volume | 66.484 | 70.763 | 76.482 | 83.822 | 94.118 | 6.759 |
| [Toneladas por Atracação] | Volume | 18.235 | 17.283 | 17.109 | 15.818 | 14.915 | 15.381 |
| [% Cabotagem] | Participação | 23,3% | 23,3% | 22,2% | 22,2% | 21,6% | 26,3% |
| [% Longo Curso] | Participação | 70,6% | 69,9% | 70,8% | 71,6% | 71,7% | 68,2% |
| [% Contêiner] | Participação | 11,0% | 10,5% | 9,8% | 11,6% | 11,7% | 12,7% |
| [% do Total Brasil] | Participação | 100,0% | 100,0% | 100,0% | 100,0% | 100,0% | 100,0% |
| [Espera Média (h)] | Eficiência | 42,3 | 46,7 | 47,8 | 39,5 | 39,0 | 39,7 |
| [Espera Mediana (h)] | Eficiência | 1,9 | 1,8 | 1,9 | 1,3 | 1,4 | 1,9 |
| [Tempo Atracado Médio (h)] | Eficiência | 31,1 | 31,0 | 30,0 | 28,3 | 26,8 | 27,7 |
| [Tempo de Operação Médio (h)] | Eficiência | 22,7 | 22,1 | 21,8 | 20,4 | 19,4 | 20,6 |
| [% Atracado em Operação] | Eficiência | 73,3% | 72,0% | 72,9% | 73,2% | 73,1% | 74,3% |
| [Prancha Média Operacional (t/h)] | Eficiência | 803 | 777 | 779 | 770 | 765 | 747 |
| [Prancha Média Geral (t/h)] | Eficiência | 583 | 555 | 564 | 556 | 553 | 552 |
| [Horas Paralisadas] | Eficiência | 135.264 | 131.754 | 140.033 | 178.345 | 195.717 | 13.944 |

## 2. Suape (porto organizado, IDInstalacao = BRSUA)

| Medida | Pasta | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---:|---:|---:|---:|---:|---:|
| [Toneladas] | Volume | 22.079.408 | 24.726.350 | 24.015.152 | 24.830.911 | 24.253.346 | 2.193.515 |
| [Toneladas AA] | Volume | — | 22.079.408 | 24.726.350 | 24.015.152 | 24.830.911 | 1.582.901 |
| [Var % Toneladas AA] | Volume | — | 12,0% | -2,9% | 3,4% | -2,3% | 38,6% |
| [TEU] | Volume | 518.640 | 492.216 | 527.067 | 646.808 | 698.177 | 54.883 |
| [Nº Atracações] | Volume | 1.451 | 1.506 | 1.510 | 1.626 | 1.566 | 135 |
| [Toneladas por Atracação] | Volume | 15.217 | 16.419 | 15.904 | 15.271 | 15.487 | 16.248 |
| [% Cabotagem] | Participação | 63,3% | 66,6% | 69,5% | 69,6% | 67,2% | 62,4% |
| [% Longo Curso] | Participação | 36,7% | 33,4% | 30,1% | 29,9% | 32,2% | 36,3% |
| [% Contêiner] | Participação | 26,7% | 22,8% | 24,2% | 28,3% | 31,2% | 26,5% |
| [% do Total Brasil] | Participação | 1,8% | 2,0% | 1,8% | 1,9% | 1,7% | 2,1% |
| [Espera Média (h)] | Eficiência | 23,0 | 25,1 | 30,2 | 28,3 | 34,7 | 32,9 |
| [Espera Mediana (h)] | Eficiência | 1,0 | 1,0 | 1,1 | 5,9 | 4,3 | 4,2 |
| [Tempo Atracado Médio (h)] | Eficiência | 33,3 | 34,4 | 33,2 | 34,6 | 33,7 | 35,9 |
| [Tempo de Operação Médio (h)] | Eficiência | 24,7 | 24,9 | 23,8 | 25,9 | 24,7 | 26,4 |
| [% Atracado em Operação] | Eficiência | 73,1% | 72,4% | 73,1% | 75,0% | 74,5% | 75,9% |
| [Prancha Média Operacional (t/h)] | Eficiência | 614 | 658 | 657 | 584 | 618 | 591 |
| [Prancha Média Geral (t/h)] | Eficiência | 454 | 477 | 473 | 438 | 456 | 442 |
| [Horas Paralisadas] | Eficiência | 2.152 | 3.475 | 4.255 | 4.047 | 3.299 | 267 |
| [Ranking Porto] (entre todas as instalações) | Participação | 14º | 11º | 14º | 13º | 13º | 10º |

## 3. Benchmark Nordeste (página "Nordeste & Suape")

### 2026

| Porto | Toneladas | Var % AA | Espera mediana (h) | Prancha operacional (t/h) | % Contêiner | % Atracado em operação | Nº atracações | Ranking entre os 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Suape | 2.193.515 | 38,6% | 4,2 | 591 | 26,5% | 75,9% | 135 | 1º |
| Pecém | 1.525.226 | 0,3% | 19,1 | 530 | 39,2% | 87,7% | 70 | 3º |
| Itaqui | 2.088.595 | 44,3% | 112,9 | 483 | 0,0% | 86,3% | 63 | 2º |
| Salvador | 503.584 | -5,2% | 1,7 | 594 | 91,0% | 84,8% | 44 | 4º |
| Aratu | 465.899 | -12,5% | 14,9 | 260 | 0,0% | 76,2% | 31 | 5º |
| Recife | 105.878 | -40,5% | 0,4 | 40 | 0,0% | 88,9% | 29 | 8º |
| Natal | 63.912 | 93,4% | 0,2 | 51 | 18,5% | 90,1% | 24 | 9º |
| Cabedelo | 139.626 | 182,0% | 3,7 | 297 | 0,0% | 80,9% | 8 | 7º |
| Maceió | 191.438 | -26,5% | 6,7 | 289 | 0,0% | 80,1% | 11 | 6º |

- [Espera Mediana Média Pares (h)] 2026 = **20,0 h** (média simples das medianas dos 8 pares).
- [Espera Mediana Suape (h)] 2026 = **4,2 h**; [Diferença Espera Suape vs Pares (h)] = **-15,8 h**.

### 2025

| Porto | Toneladas | Var % AA | Espera mediana (h) | Prancha operacional (t/h) | % Contêiner | % Atracado em operação | Nº atracações | Ranking entre os 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Suape | 24.253.346 | -2,3% | 4,3 | 618 | 31,2% | 74,5% | 1.566 | 2º |
| Pecém | 20.515.856 | 7,7% | 9,8 | 608 | 39,7% | 87,2% | 797 | 3º |
| Itaqui | 36.771.880 | 8,5% | 143,9 | 650 | 0,0% | 85,9% | 979 | 1º |
| Salvador | 6.020.388 | -8,8% | 2,0 | 436 | 80,8% | 85,8% | 499 | 4º |
| Aratu | 5.819.867 | -11,3% | 29,8 | 259 | 0,0% | 77,9% | 451 | 5º |
| Recife | 1.570.686 | -8,0% | 0,5 | 43 | 0,0% | 90,2% | 322 | 7º |
| Natal | 494.963 | 21,1% | 0,2 | 47 | 14,5% | 90,2% | 191 | 9º |
| Cabedelo | 1.185.078 | -14,4% | 12,2 | 286 | 0,0% | 73,3% | 84 | 8º |
| Maceió | 2.510.841 | -6,0% | 13,0 | 261 | 0,0% | 82,6% | 165 | 6º |

- [Espera Mediana Média Pares (h)] 2025 = **26,4 h** (média simples das medianas dos 8 pares).
- [Espera Mediana Suape (h)] 2025 = **4,3 h**; [Diferença Espera Suape vs Pares (h)] = **-22,1 h**.

## 4. Números citados no README, no roteiro do vídeo e no post

Fonte única dos números de texto. `tests/test_documentacao.py` confere que o README usa exatamente estes valores.

| ID | Valor | Medida | Filtro |
|---|---:|---|---|
| brasil_t | 1.403,8 milhões de t | [Toneladas] | Ano = 2025 |
| brasil_var | 5,9% | [Var % Toneladas AA] | Ano = 2025 |
| suape_t | 24,3 milhões de t | [Toneladas] | Ano = 2025; Instalação = Suape |
| suape_var | -2,3% | [Var % Toneladas AA] | Ano = 2025; Instalação = Suape |
| suape_rank | 13ª | [Ranking Suape Brasil] | Ano = 2025 |
| suape_share | 1,7% | [% do Total Brasil] | Ano = 2025; Instalação = Suape |
| suape_teu | 698 mil TEU | [TEU] | Ano = 2025; Instalação = Suape |
| suape_teu_ini | 519 mil TEU | [TEU] | Ano = 2021; Instalação = Suape |
| suape_teu_cresc | 34,6% | [TEU] (variação) | Ano = 2025 x 2021; Instalação = Suape |
| suape_cont | 31,2% | [% Contêiner] | Ano = 2025; Instalação = Suape |
| suape_cont_ini | 26,7% | [% Contêiner] | Ano = 2021; Instalação = Suape |
| suape_espera | 4,3 h | [Espera Mediana (h)] | Ano = 2025; Instalação = Suape |
| suape_espera_ant | 5,9 h | [Espera Mediana (h)] | Ano = 2024; Instalação = Suape |
| suape_espera_ini | 1,0 h | [Espera Mediana (h)] | Ano = 2021; Instalação = Suape |
| pares_espera | 26,4 h | [Espera Mediana Média Pares (h)] | Ano = 2025 |
| dif_espera | 22,1 h | [Diferença Espera Suape vs Pares (h)] | Ano = 2025 |
| itaqui_espera | 143,9 h | [Espera Mediana (h)] | Ano = 2025; Instalação = Itaqui |
| suape_espera_cont | 0,8 h | [Espera Mediana (h)] | Ano = 2025; Instalação = Suape; Natureza = Contêiner |
| suape_espera_liq | 28,8 h | [Espera Mediana (h)] | Ano = 2025; Instalação = Suape; Natureza = Granel Líquido e Gasoso |
| suape_prancha | 618 t/h | [Prancha Média Operacional (t/h)] | Ano = 2025; Instalação = Suape |
| brasil_prancha | 765 t/h | [Prancha Média Operacional (t/h)] | Ano = 2025 |
| chuva_br | 32,1% | [Horas Paralisadas] motivo Chuva ÷ total | Ano = 2025 |
| chuva_suape | 37,9% | [Horas Paralisadas] motivo Chuva ÷ total | Ano = 2025; Instalação = Suape |

### Espera mediana mensal 2025: Suape x média dos pares (visual de linha)

| Mês | Suape (h) | Média dos pares (h) |
|---|---:|---:|
| 01/2025 | 17,2 | 18,1 |
| 02/2025 | 2,7 | 28,3 |
| 03/2025 | 0,9 | 35,4 |
| 04/2025 | 1,2 | 26,1 |
| 05/2025 | 3,7 | 22,3 |
| 06/2025 | 1,5 | 28,9 |
| 07/2025 | 9,4 | 32,4 |
| 08/2025 | 1,1 | 36,3 |
| 09/2025 | 1,2 | 29,1 |
| 10/2025 | 1,3 | 20,8 |
| 11/2025 | 4,5 | 20,2 |
| 12/2025 | 9,0 | 21,0 |
