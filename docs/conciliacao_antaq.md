# Conciliação com os totais oficiais da ANTAQ

> Gerado automaticamente por `etl/04_documentar.py`. Critério de aceite: total nacional anual com diferença de até ±2% (testado em `tests/test_conciliacao.py`).

Regra de contagem usada: soma de `VLPesoCargaBruta` das linhas de Carga com `FlagMCOperacaoCarga = 1` (inclui transbordo e baldeação, como a ANTAQ), por ano da data de desatracação.

## Total nacional por ano (critério de aceite)

| Ano | Pipeline (Mt) | Oficial ANTAQ (Mt) | Diferença | Status | Fonte |
|---|---:|---:|---:|---|---|
| 2021 | 1.212,4 | 1.214,0 | -0,13% | OK | [ANTAQ, notícia de 08/02/2023 (valor revisado de 2021, citado como recorde)](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2022 | 1.223,0 | 1.209,0 | 1,16% | OK | [ANTAQ, notícia de 08/02/2023 (Anuário Estatístico 2022)](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2023/setor-portuario-movimenta-mais-de-1-2-bilhao-de-toneladas-em-2022) |
| 2023 | 1.308,6 | 1.303,0 | 0,43% | OK | [ANTAQ, notícia de 07/02/2024 (Desempenho Aquaviário 2023)](https://www.gov.br/antaq/pt-br/central-de-conteudos/noticias/2024/setor-aquaviario-movimenta-mais-de-1-3-bi-de-toneladas-em-2023-e-registra-recorde-historico) |
| 2024 | 1.325,9 | 1.322,5 | 0,26% | OK | [ANTAQ, Desempenho Aquaviário 2025, p. 2 (valor de 2024 revisado)](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |
| 2025 | 1.403,8 | 1.403,1 | 0,05% | OK | [ANTAQ, Desempenho Aquaviário 2025, p. 2](https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/Anuario2025.pdf) |

2026 não entra na conciliação: só há 01/2026 na base e a ANTAQ ainda não publicou o total anual.

## Quebras publicadas (informativo, sem critério de aceite)

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

## Leitura das diferenças

- Os totais oficiais são fotografias da data de publicação; a base do Estatístico é revisada depois (ex.: 2021 foi divulgado como 1.210 Mt em fev/2022 e citado como 1.214 Mt em fev/2023). Por isso usamos sempre o valor publicado mais recente.
- Quebras por navegação e região diferem mais que o total: a ANTAQ classifica parte da carga de interior/cabotagem e algumas instalações de fronteira de forma diferente da coluna `Tipo Navegação`, e 0,2–0,3% da tonelagem está em instalação não identificada (sem região). O total não é afetado.
- Nenhum ajuste manual foi feito para aproximar os números.
