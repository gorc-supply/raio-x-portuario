# Exploração dos dados

> Gerado por `etl/explorar.py` em 25/11/2026 00:32.

## 1. Fonte e layout

- **Fonte oficial**: ANTAQ — Estatístico Aquaviário, base de dados anual (`https://web3.antaq.gov.br/ea/sense/download.html`). **Fora do ar** durante todo o projeto (o host `web3.antaq.gov.br` não resolve mais no DNS; o endereço antigo redireciona para o aviso ["Painel Estatístico Aquaviário Indisponível"](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/publicacoes-off/painel-estatistico-aquaviario-indisponivel), publicado em 23/06/2026). Ver docs/DECISOES.md (D02).
- **Fonte usada**: espelho público `vinicius-souza/antaq` no Hugging Face (licença CC-BY-4.0, revisão `ff0349f` de 18/04/2026), com os arquivos TXT oficiais convertidos 1:1 para Parquet. Os **nomes das colunas são os originais da ANTAQ** (com acentos e espaços).
- **Layout do espelho**: Parquet por tabela e ano. Datas da Atracação como texto `dd/mm/aaaa hh:mm:ss`; datas da Paralisação como texto `aaaa-mm-dd hh:mm:ss.ffffff`; números como DOUBLE (ponto decimal); parte dos textos com acentuação corrompida (UTF-8 lido como Latin-1, ex.: `BaldeaÃ§Ã£o`) — corrigido no tratamento (regra R7).
- **Layout dos TXT oficiais** (aceitos pelo pipeline se colocados em `data/raw/antaq_oficial/`): separador `;`, cabeçalho na 1ª linha, vírgula decimal, datas `dd/mm/aaaa hh:mm:ss`. O leitor detecta UTF-8 ou Latin-1. **Não pôde ser conferido com arquivo oficial real** (pendência registrada).
- **Recorte**: anos completos 2021–2025. O espelho (gerado em 18/04/2026) também traz janeiro/2026, que fica fora do projeto por ser um ano incompleto (DECISOES.md, D18).

## 2. Colunas reais de cada arquivo e colunas usadas

### Atracacao

Colunas no arquivo (29): `IDAtracacao`, `CDTUP`, `IDBerco`, `Berço`, `Porto Atracação`, `Coordenadas`, `Apelido Instalação Portuária`, `Complexo Portuário`, `Tipo da Autoridade Portuária`, `Data Atracação`, `Data Chegada`, `Data Desatracação`, `Data Início Operação`, `Data Término Operação`, `Ano`, `Mes`, `Tipo de Operação`, `Tipo de Navegação da Atracação`, `Nacionalidade do Armador`, `FlagMCOperacaoAtracacao`, `Terminal`, `Município`, `UF`, `SGUF`, `Região Geográfica`, `Região Hidrográfica`, `Instalação Portuária em Rio`, `Nº da Capitania`, `Nº do IMO`

| Coluna usada | Significado |
|---|---|
| `IDAtracacao` | Identificador único da atracação (chave para Carga, Tempos e Paralisações) (✓ único) |
| `CDTUP` | Código da instalação portuária (porto organizado ou TUP) — chave de dInstalacao |
| `IDBerco` | Identificador do berço |
| `Porto Atracação` | Nome da instalação portuária onde ocorreu a atracação |
| `Complexo Portuário` | Complexo portuário definido pela ANTAQ (agrupa instalações próximas) |
| `Tipo da Autoridade Portuária` | Porto Organizado (público) ou Terminal Autorizado (TUP) |
| `Coordenadas` | Longitude,latitude da instalação (✓ ordem lon,lat conferida em Recife/Suape) |
| `Data Chegada` | Chegada da embarcação à área do porto (fundeio/barra) |
| `Data Atracação` | Atracação no berço |
| `Data Início Operação` | Início da operação de carga/descarga |
| `Data Término Operação` | Término da operação |
| `Data Desatracação` | Desatracação; define o mês/ano de referência (✓ coluna Ano = ano desta data em 100%) |
| `Ano` | Ano de referência da atracação |
| `Tipo de Operação` | Finalidade da atracação (Movimentação da Carga, Apoio, Passageiro etc.) |
| `Tipo de Navegação da Atracação` | Longo Curso, Cabotagem, Interior, Apoio Marítimo, Apoio Portuário |
| `Município` | Município da instalação |
| `UF / SGUF` | Unidade da Federação (nome / sigla) |
| `Região Geográfica` | Região do Brasil |

### Carga

Colunas no arquivo (27): `IDCarga`, `IDAtracacao`, `Origem`, `Destino`, `CDMercadoria`, `Tipo Operação da Carga`, `Carga Geral Acondicionamento`, `ConteinerEstado`, `Tipo Navegação`, `FlagAutorizacao`, `FlagCabotagem`, `FlagCabotagemMovimentacao`, `FlagConteinerTamanho`, `FlagLongoCurso`, `FlagMCOperacaoCarga`, `FlagOffshore`, `FlagTransporteViaInterioir`, `Percurso Transporte em vias Interiores`, `Percurso Transporte Interiores`, `STNaturezaCarga`, `STSH2`, `STSH4`, `Natureza da Carga`, `Sentido`, `TEU`, `QTCarga`, `VLPesoCargaBruta`

| Coluna usada | Significado |
|---|---|
| `IDCarga` | Identificador do registro de carga (✓ único) |
| `IDAtracacao` | Atracação em que a carga foi movimentada |
| `CDMercadoria` | Código da mercadoria: posição SH4 da NCM; códigos ISO 6346 para contêineres (ex.: 22G0, 45G1); alguns códigos especiais ANTAQ (ex.: SRFC, CA01) |
| `Tipo Operação da Carga` | Longo Curso Exportação/Importação, Cabotagem, Interior, Baldeação, Safamento etc. |
| `Tipo Navegação` | Tipo de navegação da carga |
| `FlagMCOperacaoCarga` | 1 = a operação conta como movimentação de carga na estatística oficial (✓ conciliação) |
| `Natureza da Carga` | Granel Sólido, Granel Líquido e Gasoso, Carga Geral, Carga Conteinerizada |
| `Sentido` | Embarcados, Desembarcados, Não Informado |
| `TEU` | Quantidade de TEU (contêineres de 20 pés equivalentes) |
| `VLPesoCargaBruta` | Peso bruto da carga em toneladas (✓ soma reconcilia com o total oficial) |

### TemposAtracacao

Colunas no arquivo (7): `IDAtracacao`, `TEsperaAtracacao`, `TEsperaInicioOp`, `TOperacao`, `TEsperaDesatracacao`, `TAtracado`, `TEstadia`

| Coluna usada | Significado |
|---|---|
| `IDAtracacao` | Chave 1:1 com Atracacao (✓) |
| `TEsperaAtracacao` | Horas entre Data Chegada e Data Atracação (✓) |
| `TEsperaInicioOp` | Horas entre Data Atracação e Data Início Operação |
| `TOperacao` | Horas entre Data Início Operação e Data Término Operação |
| `TEsperaDesatracacao` | Horas entre Data Término Operação e Data Desatracação |
| `TAtracado` | Horas entre Data Atracação e Data Desatracação (✓) |
| `TEstadia` | Horas entre Data Chegada e Data Desatracação |

### TemposAtracacaoParalisacao

Colunas no arquivo (5): `IDTemposDescontos`, `IDAtracacao`, `DescricaoTempoDesconto`, `DTInicio`, `DTTermino`

| Coluna usada | Significado |
|---|---|
| `IDTemposDescontos` | Identificador do evento de paralisação |
| `IDAtracacao` | Atracação em que ocorreu a paralisação |
| `DescricaoTempoDesconto` | Motivo da paralisação (chuva, quebra de equipamento, aguardando carga etc.) |
| `DTInicio / DTTermino` | Início e fim da paralisação (horas = diferença entre as duas) |

## 3. Chaves de ligação

```
Atracacao (IDAtracacao, PK) 1 ──── 1 TemposAtracacao (IDAtracacao)
Atracacao (IDAtracacao, PK) 1 ──── N Carga (IDAtracacao)
Atracacao (IDAtracacao, PK) 1 ──── N TemposAtracacaoParalisacao (IDAtracacao)
Atracacao (CDTUP)           N ──── 1 instalação portuária (dInstalacao no modelo)
Carga (CDMercadoria)        N ──── 1 mercadoria (dMercadoria no modelo)
```

- Atracacao: 481,304 linhas, 481,304 IDAtracacao distintos (chave única).
- TemposAtracacao: 481,304 linhas; 0 sem atracação; 0 atracações sem tempos.
- Carga: 11,733,251 linhas, 11,733,251 IDCarga distintos; 0 órfãs.
- Paralisações órfãs: 0.

## 4. Linhas por ano (ano da data de desatracação)

| Ano | Atracações | Registros de carga | Paralisações | Atracações com carga movimentada |
|---|---:|---:|---:|---:|
| 2021 | 79,238 | 2,348,365 | 104,079 | 66,484 |
| 2022 | 85,092 | 2,280,017 | 106,569 | 70,763 |
| 2023 | 93,918 | 2,200,645 | 123,567 | 76,482 |
| 2024 | 106,834 | 2,439,611 | 225,160 | 83,822 |
| 2025 | 116,222 | 2,464,613 | 228,077 | 94,118 |

## 5. % de nulos nas colunas-chave (base bruta, 2021–2025)

| Tabela | Coluna | % nulos |
|---|---|---:|
| Atracacao | `IDAtracacao` | 0.00% |
| Atracacao | `CDTUP` | 0.00% |
| Atracacao | `Data Atracação` | 0.10% |
| Atracacao | `Data Desatracação` | 0.00% |
| Atracacao | `Data Chegada` | 0.10% |
| Atracacao | `Data Início Operação` | 5.75% |
| Atracacao | `Data Término Operação` | 5.74% |
| Atracacao | `Tipo de Navegação da Atracação` | 0.10% |
| Carga | `IDCarga` | 0.00% |
| Carga | `IDAtracacao` | 0.00% |
| Carga | `CDMercadoria` | 35.78% |
| Carga | `FlagMCOperacaoCarga` | 0.00% |
| Carga | `Natureza da Carga` | 0.00% |
| Carga | `Sentido` | 0.00% |
| Carga | `VLPesoCargaBruta` | 0.00% |
| Carga | `Tipo Navegação` | 0.00% |
| TemposAtracacao | `IDAtracacao` | 0.00% |
| TemposAtracacao | `TEsperaAtracacao` | 9.98% |
| TemposAtracacao | `TOperacao` | 7.76% |
| TemposAtracacao | `TAtracado` | 2.07% |
| TemposAtracacao | `TEstadia` | 2.52% |
| TemposAtracacaoParalisacao | `IDAtracacao` | 0.00% |
| TemposAtracacaoParalisacao | `DescricaoTempoDesconto` | 0.00% |
| TemposAtracacaoParalisacao | `DTInicio` | 0.00% |
| TemposAtracacaoParalisacao | `DTTermino` | 0.00% |

## 6. Tempos: definição ANTAQ, conferência e valores negativos/absurdos

A ANTAQ já entrega os tempos calculados (tabela TemposAtracacao, em **horas**). O projeto usa esses valores e confere a definição recalculando a partir das datas:

| Tempo ANTAQ | Definição | Maior diferença vs. recalculado (h) |
|---|---|---:|
| TEsperaAtracacao | Data Atracação − Data Chegada | 0.000000 |
| TOperacao | Data Término Operação − Data Início Operação | 0.000000 |
| TAtracado | Data Desatracação − Data Atracação | 0.000000 |
| TEstadia | Data Desatracação − Data Chegada | 0.000000 |

| Métrica | Linhas | Negativos | Nulos | Mediana (h) | P99,5 (h) | Máximo (h) | > 30 dias |
|---|---:|---:|---:|---:|---:|---:|---:|
| t_espera_atracacao | 481,304 | 0 | 48,046 | 1.1 | 667.1 | 18,251.4 | 1,644 |
| t_espera_inicio_op | 481,304 | 0 | 41,740 | 0.5 | 65.7 | 2,141.9 | 97 |
| t_operacao | 481,304 | 0 | 37,342 | 7.5 | 202.8 | 2,377.0 | 55 |
| t_espera_desatracacao | 481,304 | 0 | 36,793 | 1.1 | 47.0 | 721.2 | 1 |
| t_atracado | 481,304 | 0 | 9,967 | 12.2 | 285.6 | 4,633.5 | 357 |
| t_estadia | 481,304 | 0 | 12,140 | 22.0 | 748.9 | 18,869.0 | 2,814 |

Leitura: não há tempos negativos na base; há valores absurdos (esperas de mais de 2 anos, atracações de meses) — por isso a limitação no P99,5 por natureza de carga (regra R5). A espera média é muito maior que a mediana (cauda longa): o painel destaca a **mediana**.

## 7. Regra de contagem da movimentação

| Tipo Operação da Carga | FlagMCOperacaoCarga | Registros | Toneladas (Mt) |
|---|---:|---:|---:|
| Longo Curso Exportação | 1 | 2,914,342 | 3,694.1 |
| Cabotagem | 1 | 1,475,232 | 1,357.7 |
| Longo Curso Importação | 1 | 3,677,746 | 855.0 |
| Interior | 1 | 1,104,861 | 387.3 |
| Baldeação de Carga Estrangeira de Passagem | 1 | 537,925 | 67.8 |
| Baldeação de Carga Nacional | 1 | 108,973 | 41.0 |
| Longo Curso Importação com Baldeação de Carga Estrangeira | 1 | 387,149 | 31.5 |
| Longo Curso Exportação com Baldeação de Carga Estrangeira | 1 | 256,830 | 22.8 |
| Apoio | 1 | 555,927 | 16.6 |
| Safamento | 0 | 661,561 | 30.0 |
| Operação Intermediária | 0 | 10,950 | 12.1 |
| Abastecimento | 0 | 4,664 | 11.8 |
| Transferência Interna | 0 | 17,346 | 6.2 |
| Remoção a bordo | 0 | 19,745 | 5.1 |

Somar só `FlagMCOperacaoCarga = 1` (inclui baldeação/transbordo) reproduz o total oficial dentro de ±1,2% em todos os anos — ver [conciliacao_antaq.md](conciliacao_antaq.md).
