# Registro de decisões autônomas

Cada decisão: **contexto → decisão → alternativas → motivo**. Ordem cronológica.

## D01 — Python do projeto

- **Contexto:** o `python` do PATH é só o atalho da Microsoft Store (não instalado). Existe Python 3.12 gerenciado pelo `uv`.
- **Decisão:** `.venv` criado com `uv venv --python 3.12`; dependências instaladas só dentro do `.venv`.
- **Alternativas:** instalar Python pela Store/winget (instalação fora do projeto).
- **Motivo:** nada instalado fora do projeto; 3.12 tem wheels prontas para todas as dependências.

## D02 — Fonte dos dados: portal da ANTAQ fora do ar → espelho público de contingência

- **Contexto:** `web3.antaq.gov.br` não resolve mais no DNS (testado com o DNS local, 8.8.8.8 e 1.1.1.1). Os endereços alternativos (`web.antaq.gov.br`, `ea.antaq.gov.br`) respondem 403/502/522 via Cloudflare, e `estatistica.antaq.gov.br/ea/sense/download.html` redireciona para o aviso oficial "Painel Estatístico Aquaviário Indisponível" (publicado em 23/06/2026, previsão de volta em 10/07, ainda fora em 24/11/2026). O painel novo (`aquarela.antaq.gov.br`, Qlik Sense) não oferece download de base. O portal `dadosabertos.antaq.gov.br` também saiu do DNS e o Internet Archive estava fora do ar.
- **Decisão:** o pipeline aceita, em ordem: (1) zips oficiais colocados à mão em `data/raw/antaq_oficial/`; (2) links .zip lidos do HTML da página oficial, se ela voltar; (3) contingência: espelho público `vinicius-souza/antaq` no Hugging Face (CC-BY-4.0), revisão fixada `ff0349f` (18/04/2026), com os TXT oficiais convertidos para Parquet e os nomes de coluna originais.
- **Alternativas:** (a) montar só amostra sintética — descartado, o painel não teria valor; (b) extrair dados do painel Qlik por API interna — descartado (não é canal de distribuição de dados); (c) Base dos Dados/BigQuery — exige login no Google Cloud.
- **Motivo:** dado real e completo (2010–jan/2026), mesmo layout de colunas da ANTAQ. A integridade foi verificada de forma independente: o total anual reconcilia com os números **oficiais** publicados pela ANTAQ em notícias e anuários (diferença de −0,13% a +1,16%, ver `docs/conciliacao_antaq.md`), assim como Suape 2022 (24,7 Mt), Itaqui 2022 e as maiores mercadorias de 2024. Nenhum dado foi inventado; não foi preciso gerar amostra sintética.
- **Consequência:** o último mês disponível é **jan/2026** (o espelho foi gerado em abril/2026). Quando a ANTAQ voltar, basta colocar os zips oficiais em `data/raw/antaq_oficial/` (ou deixar o `01_download.py` achar os links) e rodar `etl/run_all.py`.

## D03 — Regra de contagem da movimentação

- **Decisão:** toneladas = soma de `VLPesoCargaBruta` das linhas de Carga com `FlagMCOperacaoCarga = 1`. Inclui baldeação/transbordo (Baldeação de Carga Nacional/Estrangeira, Longo Curso com Baldeação) e exclui Safamento, Remoção a bordo, Transferência interna, Operação intermediária e Abastecimento.
- **Alternativas:** somar tudo, sem olhar a flag (+0,9% a +2,3% acima do oficial — 2022 estouraria a tolerância); excluir também as baldeações (−0,6% a −1,8%).
- **Motivo:** é a flag que a ANTAQ usa para marcar "movimentação de carga" e é a regra que reproduz o oficial com menor erro em todos os anos.

## D04 — Período de referência = mês da desatracação

- **Decisão:** cada atracação (e sua carga e paralisações) pertence ao mês/ano da **data de desatracação**.
- **Motivo:** é a convenção da ANTAQ — a coluna `Ano` da base coincide com o ano da desatracação em 100% das 489.751 atracações.

## D05 — Tempos e limpeza

- **Decisão:** usar os tempos que a ANTAQ já calcula (`TemposAtracacao`, em horas; conferidos contra as datas com diferença < 0,000001 h). Espera = `TEsperaAtracacao`; operação = `TOperacao`; atracado = `TAtracado`; estadia = `TEstadia`. Negativos → descartados (não houve nenhum). Operação > atracado → operação descartada (nenhum caso). Valores acima do P99,5 **da natureza de carga predominante da atracação** → limitados ao P99,5 (winsorização), só em tempo, nunca em tonelagem. Paralisações seguem a mesma lógica.
- **Alternativas:** excluir outliers (perde a atracação inteira, inclusive a tonelagem dela nas pranchas); não tratar (esperas de 2 anos distorcem médias).
- **Motivo:** conservador e explícito; quantidades afetadas em `docs/data_quality.md`.

## D06 — fAtracacao só com atracações que movimentaram carga

- **Decisão:** atracações sem carga com `FlagMCOperacaoCarga = 1` (apoio, passageiros, reparo, abastecimento: ~19% das linhas) ficam fora de fAtracacao. `[Nº Atracações]` conta, portanto, atracações com movimentação de carga.
- **Motivo:** espera e prancha de navio de apoio/passageiro distorcem a análise de gargalo de carga; a contagem resultante (83.822 em 2024) é a mais próxima do "82 mil atracações" do Anuário 2024; e mantém os arquivos abaixo de 50 MB.

## D07 — Recorte "Suape" e campo de complexo portuário

- **Decisão:** "Suape" = **porto organizado de Suape** (`CDTUP = BRSUA`). dInstalacao tem `ComplexoPortuario` (complexo oficial da ANTAQ, ex.: "Suape - Recife", "Aratu - Salvador", "Pecém - Fortaleza", "Itaqui" = Itaqui + Ponta da Madeira + Alumar) para a leitura de complexo, e `PortoBenchmarkNE` para a leitura porto a porto.
- **Alternativas:** usar o complexo "Suape - Recife" como "Suape".
- **Motivo:** (1) o pedido lista Recife como par separado de Suape; (2) na base não há TUP na área de Suape — os terminais de Suape são arrendamentos dentro do porto organizado, então porto organizado = complexo de Suape na prática; (3) o complexo oficial junta dois portos com autoridades diferentes. Pares no mesmo critério: portos organizados de Itaqui, Salvador, Aratu, Recife, Natal, Cabedelo e Maceió; Pecém é um TUP (Terminal Portuário do Pecém) e entra como tal. A leitura por complexo fica disponível trocando o campo no visual.

## D08 — Dicionário de mercadorias

- **Contexto:** a tabela auxiliar oficial `Mercadoria` (nomenclatura simplificada e grupo ANTAQ) não estava no espelho nem disponível para download.
- **Decisão:** `CDMercadoria` é a posição SH4 da NCM em 93,5% da tonelagem. Descrição e capítulo vêm da **tabela SH oficial do Comex Stat (MDIC)** (`api-comexstat.mdic.gov.br/tables/hs`). Nomes curtos para ~35 mercadorias relevantes em `etl/referencias/apelidos_mercadoria.csv` (ex.: 2601 → "Minério de ferro"). Toda carga conteinerizada vira a mercadoria "Contêineres" (como no Anuário). Grupo de mercadoria simples criado pelo projeto a partir do capítulo SH2 (`etl/referencias/grupos_sh2.csv`). Códigos especiais ANTAQ sem descrição pública (SRFC, CA01, 8888 etc., 0,3% da tonelagem) aparecem como "Código ANTAQ xxxx (sem descrição)". Códigos lidos como número em alguns anos (`2601.0`, `201.0`) voltam ao formato SH4 de 4 dígitos.
- **Motivo:** fonte oficial pública; os totais por mercadoria batem com o Anuário 2024 (minério 399,5 x 398,8 Mt; petróleo 203,5 x 203,4; contêineres 153,5 x 153,3).

## D09 — Texto com acentuação corrompida

- **Decisão:** valores com padrão de UTF-8 lido como Latin-1 (`Ã§`, `Ã£` …) são corrigidos (`encode('latin-1').decode('utf-8')`) só nos valores distintos. Contagens em `docs/data_quality.md`.

## D10 — Arquivos de saída

- **Decisão:** CSV UTF-8, vírgula como separador de campo, ponto decimal, datas ISO (`aaaa-mm-dd`, `aaaa-mm-dd hh:mm`). Navegação, natureza e sentido viram códigos inteiros nas fatos (rótulos nas dimensões). fAtracacao sai em um arquivo por ano (pasta `data/processed/fAtracacao/`), combinado pelo Power Query. Total ~50 MB, maior arquivo ~11 MB.
- **Motivo:** limite de 50 MB por arquivo pedido para o GitHub e meta de 100 MB no total.

## D11 — gh CLI ausente

- **Contexto:** `gh` não está instalado (logo, não autenticado). O conector GitHub do ambiente também falhou na autenticação.
- **Decisão:** conforme a instrução, tudo fica commitado localmente e os comandos exatos ficam em `docs/PENDENCIAS.md`. Não instalei o gh: sem login interativo ele não ficaria autenticado. O card do portfólio é preparado num clone local (pasta temporária) com commit na branch `raio-x-portuario`, pronto para push + PR.

## D12 — Identidade visual do tema

- **Contexto:** o portfólio (`gorc-supply.github.io`, CSS em `index.html`) usa fundo preto, cinzas frios, dourado `#c9a96e` de destaque, rosa, verde e caramelo, fonte Onest.
- **Decisão:** tema escuro (`powerbi/tema-raio-x.json`) com a mesma paleta; **Suape sempre em dourado `#C9A96E`** (medida `[Cor Destaque Suape]`, formatação condicional por valor de campo em todas as barras/pontos), demais portos em azul frio `#8FB4D9`. Fonte Segoe UI (Onest não existe no Power BI web).
- **Alternativas:** paleta-padrão do pedido (azul-marinho/petróleo + laranja).
- **Motivo:** o pedido pedia a identidade do portfólio quando possível; contraste de texto branco/cinza-claro sobre `#0C0D10` acima de 10:1, dourado sobre o fundo ~8:1.

## D13 — Formato e versões do PBIP

- **Decisão:** relatório em PBIR e modelo em TMDL, gerados por código (`etl/gerar_pbip.py`), nas mesmas versões de schema de um PBIP público salvo pelo Desktop (report 1.3.0, page 1.4.0, visualContainer 2.0.0, definition.pbir 4.0, definition.pbism 4.1, compatibilityLevel 1601) e com o tema base oficial `CY24SU10.json` (arquivo de tema que acompanha o Desktop, copiado do repositório público `RuiRomano/pbip-demo`). Todos os 86 JSON validados com `jsonschema` contra `github.com/microsoft/json-schemas` (commit fixado).
- **Alternativas:** usar as versões mais novas (report 3.x, visualContainer 2.13) — descartado: menos exemplos reais para conferir a estrutura; o Desktop atual abre e atualiza versões anteriores.
- **Motivo:** menor risco de erro de abertura. O `run_all.py` **não** regenera o PBIP (para não apagar ajustes feitos à mão no Desktop); só o valida.

## D14 — Mapa

- **Decisão:** visual nativo Azure Maps (`azureMap`), com localização = `dInstalacao[LocalMapa]` ("Município - UF, Brasil") e tamanho = `[Toneladas]`. Latitude e Longitude oficiais (da coluna `Coordenadas` da ANTAQ) ficam no modelo com a categoria de dados certa, como alternativa.
- **Motivo:** a documentação da Microsoft confirma que o Azure Maps funciona em "Publicar na Web"; os papéis `Category` e `Size` seguem um PBIR real. O risco restante é de geocodificação (texto concatenado) — ver PENDENCIAS.

## D15 — Calendário e medidas de tempo

- **Decisão:** `dCalendario` em Power Query (M), 01/01/2021–31/12/2026, marcada como tabela de datas; `MesComDado` vem de `meta.csv`. `[Toneladas AA]` compara só os meses com dado (jan/2026 x jan/2025). Visuais de período usam `AnoMes` ordenado por `AnoMesNum`. Segmentação de Ano começa em **2025** (último ano completo) e é sincronizada entre as páginas, assim como a de Região.
- **Motivo:** sem isso, 2026 (só janeiro) apareceria com queda de 93% contra 2025.

## D16 — Benchmark do Nordeste

- **Decisão:** a média dos pares é a **média simples das medianas** dos 8 pares (cada porto pesa igual), como pedido ("média dos pares"). A página "Nordeste & Suape" tem filtro de página com Suape + 8 pares. O README avisa que Itaqui (143,9 h em 2025) puxa essa média; a mediana das medianas dos pares seria 11,0 h.
- **Alternativas:** média ponderada por atracações; mediana conjunta das atracações dos pares.
- **Motivo:** fiel ao pedido e simples de explicar; a ressalva fica explícita.

## D17 — Medidas auxiliares de formatação e Top N

- **Decisão:** Top 10 (instalações, mercadorias, motivos de paralisação) feito por medida (`IF([Ranking] <= 10, ...)`) em vez de filtro Top N do visual; cores condicionais por medida que devolve hexadecimal (mapa de calor com faixas fixas de 2 h, 6 h, 24 h e 72 h).
- **Motivo:** filtros e regras de gradiente em JSON PBIR são a parte menos documentada do formato; medida é mais simples de validar e de explicar.
