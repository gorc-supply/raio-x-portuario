# Conciliação com os totais oficiais da ANTAQ

> Gerado automaticamente por `etl/04_documentar.py`. Critério de aceite: total nacional anual com diferença de até ±2% (testado em `tests/test_conciliacao.py`).

Regra de contagem usada: soma de `VLPesoCargaBruta` das linhas de Carga com `FlagMCOperacaoCarga = 1` (inclui transbordo e baldeação, como a ANTAQ), por ano da data de desatracação. Recorte: 2021–2025.

## 1. Total nacional por ano (critério de aceite)

| Ano | Pipeline (Mt) | Oficial ANTAQ (Mt) | Diferença | Status | Fonte |
|---|---:|---:|---:|---|---|
| 2021 | 1.212,4 | 1.214,0 | -0,13% | OK | [ANTAQ, notícia de 08/02/2023 (valor revisado de 2021, citado como recorde)](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2022 | 1.223,0 | 1.209,0 | 1,16% | OK | [ANTAQ, notícia de 08/02/2023 (Anuário Estatístico 2022)](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2023 | 1.308,6 | 1.303,0 | 0,43% | OK | [ANTAQ, notícia de 07/02/2024 (Desempenho Aquaviário 2023)](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2024/setor-aquaviario-movimenta-mais-de-1-3-bi-de-toneladas-em-2023-e-registra-recorde-historico) |
| 2024 | 1.325,9 | 1.322,5 | 0,26% | OK | [ANTAQ, Desempenho Aquaviário 2025, p. 2 (valor de 2024 revisado)](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| 2025 | 1.403,8 | 1.403,1 | 0,05% | OK | [ANTAQ, Desempenho Aquaviário 2025, p. 2](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |

## 2. Por que o painel mostra 5,9% em 2025 e o Anuário 6,1%

O Anuário "Desempenho Aquaviário 2025" publica 1.403,1 Mt em 2025 e 1.322,5 Mt em 2024: variação de **6,09%** (o Anuário arredonda para +6,1%). O pipeline tem 1.403,8 Mt e 1.325,9 Mt: variação de **5,88%**.

| Componente | Efeito na variação |
|---|---:|
| 2025 do pipeline 0,05% acima do oficial (numerador maior) | 0,05 p.p. |
| 2024 do pipeline 0,26% acima do oficial (base maior) | -0,27 p.p. |
| **Total** | **-0,22 p.p.** |

Leitura: os dois totais estão dentro do critério de ±2%, mas a base de 2024 do pipeline está 3,4 Mt acima do número do Anuário, enquanto 2025 está só 0,7 Mt acima. A base mais alta reduz a variação. Hipótese: o espelho foi gerado em 18/04/2026, depois do fechamento do Anuário, e incorpora retificações de 2024 feitas pelos terminais no SDP (a ANTAQ revisa a base continuamente — ver o caso de 2021 na seção 4). O painel mostra a variação calculada com a base que ele carrega; nenhum número foi ajustado para bater com o Anuário.

## 3. Reforço 2025: Anuário e Boletins Estatísticos trimestrais

| Período | Recorte | Pipeline (Mt) | Oficial (Mt) | Diferença | Var. pipeline | Var. oficial | Fonte |
|---|---|---:|---:|---:|---:|---:|---|
| ano | natureza: Granel Sólido | 840,8 | 839,7 | 0,1% | — | — | [ANTAQ, Desempenho Aquaviário 2025, p. 3](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | natureza: Granel Líquido e Gasoso | 333,0 | 333,0 | 0,0% | — | — | [ANTAQ, Desempenho Aquaviário 2025, p. 3](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | natureza: Contêiner | 163,8 | 164,6 | -0,5% | — | — | [ANTAQ, Desempenho Aquaviário 2025, p. 3](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | natureza: Carga Geral | 66,2 | 65,8 | 0,6% | — | — | [ANTAQ, Desempenho Aquaviário 2025, p. 3 (carga geral solta)](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | regiao: Norte | 163,4 | 163,3 | 0,1% | 10,4% | 10,0% | [ANTAQ, Desempenho Aquaviário 2025, p. 4](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | regiao: Nordeste | 329,7 | 329,7 | 0,0% | -0,1% | 0,0% | [ANTAQ, Desempenho Aquaviário 2025, p. 4](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | regiao: Sudeste | 700,2 | 699,8 | 0,1% | 7,6% | 8,0% | [ANTAQ, Desempenho Aquaviário 2025, p. 4](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | regiao: Sul | 198,9 | 199,7 | -0,4% | 5,0% | 5,0% | [ANTAQ, Desempenho Aquaviário 2025, p. 4](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| ano | regiao: Centro-Oeste | 10,6 | 10,6 | -0,1% | 147,3% | 147,0% | [ANTAQ, Desempenho Aquaviário 2025, p. 4](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| 1T/2025 | tipo: Porto Organizado | 109,2 | 108,6 | 0,6% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 1º tri/2025, tabela 1](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/boletim-1o-trimestre-2025.pdf) |
| 1T/2025 | tipo: TUP (Terminal Autorizado) | 196,7 | 195,2 | 0,8% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 1º tri/2025, tabela 2](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/boletim-1o-trimestre-2025.pdf) |
| 1T/2025 | instalacao: Suape | 5,0 | 5,1 | -1,1% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 1º tri/2025, tabela 1 (*)](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/boletim-1o-trimestre-2025.pdf) |
| 1T/2025 | instalacao: Itaqui | 6,9 | 6,8 | 0,8% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 1º tri/2025, tabela 1 (*)](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/boletim-1o-trimestre-2025.pdf) |
| 2T/2025 | tipo: Porto Organizado | 123,8 | 122,3 | 1,3% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 2º tri/2025, tabela 1](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/Boletim2Trimestre2025v1.2.pdf) |
| 2T/2025 | tipo: TUP (Terminal Autorizado) | 228,6 | 226,3 | 1,0% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 2º tri/2025, tabela 2](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/Boletim2Trimestre2025v1.2.pdf) |
| 2T/2025 | instalacao: Suape | 5,9 | 5,9 | -0,2% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 2º tri/2025, tabela 1 (*)](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/Boletim2Trimestre2025v1.2.pdf) |
| 2T/2025 | instalacao: Itaqui | 10,4 | 10,4 | -0,0% | — | — | [ANTAQ, Boletim Estatístico Aquaviário 2º tri/2025, tabela 1 (*)](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/Boletim2Trimestre2025v1.2.pdf) |
| 3T/2025 | tipo: Porto Organizado | 137,5 | 135,3 | 1,6% | 4,7% | 3,2% | [ANTAQ, Boletim Estatístico Aquaviário 3º tri/2025, tabela 1](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/BoletimEstatstico3T2025v1.0.pdf) |
| 3T/2025 | tipo: TUP (Terminal Autorizado) | 245,3 | 245,0 | 0,1% | 8,7% | 8,5% | [ANTAQ, Boletim Estatístico Aquaviário 3º tri/2025, tabela 2](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/BoletimEstatstico3T2025v1.0.pdf) |
| 3T/2025 | instalacao: Suape | 6,6 | 6,6 | -0,5% | -5,0% | -5,0% | [ANTAQ, Boletim Estatístico Aquaviário 3º tri/2025, tabela 1](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/BoletimEstatstico3T2025v1.0.pdf) |
| 3T/2025 | instalacao: Itaqui | 11,1 | 11,1 | -0,3% | 6,1% | 6,1% | [ANTAQ, Boletim Estatístico Aquaviário 3º tri/2025, tabela 1](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/BoletimEstatstico3T2025v1.0.pdf) |
| 3T/2025 | instalacao: Terminal Portuário do Pecém | 5,1 | 4,9 | 3,1% | 4,8% | 2,1% | [ANTAQ, Boletim Estatístico Aquaviário 3º tri/2025, tabela 2](https://www.gov.br/antaq/pt-br/central-de-conteudos/estudos-e-pesquisas-da-antaq-1/BoletimEstatstico3T2025v1.0.pdf) |

(*) As tabelas dos boletins do 1º e do 2º trimestre perdem o alinhamento na extração de texto do PDF; os valores foram lidos na ordem de aparição e conferem com a do 3º trimestre, que é legível.
Var. = mesmo período do ano anterior. Brasil por trimestre = Porto Organizado + TUP.
Salvador, Aratu, Recife, Natal, Cabedelo e Maceió não aparecem nos rankings dos boletins (top 10), por isso a conferência por porto usa Suape, Itaqui e Pecém.

## 4. Quebras publicadas em anos anteriores (informativo)

| Ano | Recorte | Pipeline (Mt) | Oficial (Mt) | Diferença | Fonte |
|---|---|---:|---:|---:|---|
| 2021 | navegacao: Longo Curso | 855,9 | 853,4 | 0,3% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2021 | navegacao: Cabotagem | 282,1 | 288,3 | -2,2% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2021 | navegacao: Interior | 70,9 | 65,2 | 8,7% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2022 | navegacao: Longo Curso | 855,2 | 849,6 | 0,7% | [ANTAQ, notícia de 08/02/2023](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2022 | navegacao: Cabotagem | 285,5 | 283,3 | 0,8% | [ANTAQ, notícia de 08/02/2023](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2022 | navegacao: Interior | 79,1 | 73,1 | 8,2% | [ANTAQ, notícia de 08/02/2023](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2021 | regiao: Norte | 124,1 | 122,5 | 1,3% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2021 | regiao: Nordeste | 331,5 | 330,6 | 0,3% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2021 | regiao: Centro-Oeste | 3,9 | 3,9 | 1,2% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2021 | regiao: Sudeste | 567,6 | 565,5 | 0,4% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2021 | regiao: Sul | 182,0 | 187,7 | -3,1% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2022 | instalacao: Suape | 24,7 | 24,7 | 0,1% | [ANTAQ, notícia de 08/02/2023](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2022 | instalacao: Itaqui | 33,6 | 33,6 | -0,1% | [ANTAQ, notícia de 08/02/2023](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2021 | instalacao: Terminal Portuário do Pecém | 22,4 | 21,9 | 2,3% | [ANTAQ, notícia de 02/02/2022](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2022/setor-portuario-movimenta-1-2-bilhao-de-toneladas-de-cargas-em-2021) |
| 2024 | mercadoria: Minério de ferro | 399,5 | 398,8 | 0,2% | [ANTAQ, Anuário 2024, p. 5](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anurio2024.pdf) |
| 2024 | mercadoria: Petróleo bruto | 203,5 | 203,4 | 0,0% | [ANTAQ, Anuário 2024, p. 5](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anurio2024.pdf) |
| 2024 | mercadoria: Contêineres | 153,5 | 153,3 | 0,2% | [ANTAQ, Anuário 2024, p. 5](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anurio2024.pdf) |
| 2024 | mercadoria: Soja | 123,8 | 122,5 | 1,1% | [ANTAQ, Anuário 2024, p. 5](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anurio2024.pdf) |
| 2024 | mercadoria: Milho | 57,8 | 56,4 | 2,4% | [ANTAQ, Anuário 2024, p. 5](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anurio2024.pdf) |

## 5. Leitura das diferenças

- Os totais oficiais são fotografias da data de publicação; a base do Estatístico é revisada depois (ex.: 2021 foi divulgado como 1.210 Mt em fev/2022 e citado como 1.214 Mt em fev/2023). Por isso usamos sempre o valor publicado mais recente.
- Quebras por navegação e região diferem mais que o total: a ANTAQ classifica parte da carga de interior/cabotagem de forma diferente da coluna `Tipo Navegação`, e uma pequena parcela da tonelagem está em instalação não identificada (sem região). O total não é afetado.
- Nenhum ajuste manual foi feito para aproximar os números.
