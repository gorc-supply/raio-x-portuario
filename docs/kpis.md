# Dicionário de KPIs

> Gerado por `etl/kpis_doc.py` a partir das mesmas definições usadas no TMDL (`etl/pbip_modelo.py`). Exemplos numéricos de [valores_referencia.md](valores_referencia.md), ano **2025** (último ano completo), sem outros filtros.

Regras gerais: toneladas vêm de `fCarga` (regra oficial ANTAQ, `FlagMCOperacaoCarga = 1`); tempos e pranchas vêm de `fAtracacao` (uma linha por atracação com carga, tempos já limpos); o período é o mês da desatracação. Todas as razões são **razão de somas**, o que deixa os totais corretos em qualquer nível (porto, região, Brasil).

## Volume

### [Toneladas]

**Definição:** Toneladas movimentadas (peso bruto) — soma de VLPesoCargaBruta com FlagMCOperacaoCarga = 1 (regra ANTAQ).

**Na operação do porto:** Volume físico que passou pelo cais: dimensiona receita de tarifa portuária, uso de berço, armazenagem e fluxo de caminhão/trem.

**Média, mediana ou razão:** Soma — volume é aditivo.

**Exemplo (2025):** Brasil: **1.403.813.213** · Suape: **24.253.346**.

```dax
SUM ( fCarga[Toneladas] )
```
Formato: `#,0` · Pasta: `Volume`

### [Toneladas AA]

**Definição:** Toneladas do mesmo período do ano anterior, considerando só os meses que têm dado no período atual (ex.: 2026 parcial compara jan/2026 com jan/2025).

**Na operação do porto:** Base de comparação para separar crescimento real de sazonalidade.

**Média, mediana ou razão:** Soma no mesmo recorte de meses do ano anterior (evita comparar mês parcial com ano cheio).

**Exemplo (2025):** Brasil: **1.325.915.577** · Suape: **24.830.911**.

```dax
// meses do contexto atual que já têm dado publicado
VAR DatasComDado =
    CALCULATETABLE ( VALUES ( dCalendario[Data] ), dCalendario[MesComDado] = TRUE () )
RETURN
    IF (
        NOT ISEMPTY ( DatasComDado ),
        CALCULATE ( [Toneladas], SAMEPERIODLASTYEAR ( DatasComDado ) )
    )
```
Formato: `#,0` · Pasta: `Volume`

### [Var % Toneladas AA]

**Definição:** Variação percentual das toneladas contra o mesmo período do ano anterior.

**Na operação do porto:** Mostra se o porto ganha ou perde carga; num porto, crescimento sustentado pressiona berço, pátio e acesso terrestre.

**Média, mediana ou razão:** Razão entre somas (não média de variações mensais).

**Exemplo (2025):** Brasil: **5,9%** · Suape: **-2,3%**.

```dax
VAR Atual = [Toneladas]
VAR AnoAnterior = [Toneladas AA]
RETURN
    IF ( NOT ISBLANK ( AnoAnterior ), DIVIDE ( Atual - AnoAnterior, AnoAnterior ) )
```
Formato: `+0.0%;-0.0%;0.0%` · Pasta: `Volume`

### [TEU]

**Definição:** Contêineres movimentados em TEU (unidade equivalente a um contêiner de 20 pés).

**Na operação do porto:** Escala do terminal de contêiner — o produto de maior valor agregado e mais disputado entre portos.

**Média, mediana ou razão:** Soma.

**Exemplo (2025):** Brasil: **15.242.491** · Suape: **698.177**.

```dax
SUM ( fCarga[TEU] )
```
Formato: `#,0` · Pasta: `Volume`

### [Nº Atracações]

**Definição:** Número de atracações com movimentação de carga no período (mês da desatracação).

**Na operação do porto:** Quantas vezes um navio ocupou um berço para operar carga: proxy de demanda de berço, praticagem e rebocador.

**Média, mediana ou razão:** Contagem.

**Exemplo (2025):** Brasil: **94.118** · Suape: **1.566**.

```dax
COUNTROWS ( fAtracacao )
```
Formato: `#,0` · Pasta: `Volume`

### [Toneladas por Atracação]

**Definição:** Toneladas médias por atracação = soma das toneladas das atracações ÷ nº de atracações (razão de somas).

**Na operação do porto:** Tamanho médio da consignação: navios maiores diluem custo fixo de atracação.

**Média, mediana ou razão:** Razão de somas (total de toneladas ÷ total de atracações).

**Exemplo (2025):** Brasil: **14.915** · Suape: **15.487**.

```dax
DIVIDE ( SUM ( fAtracacao[Toneladas] ), [Nº Atracações] )
```
Formato: `#,0` · Pasta: `Volume`

## Participação

### [% do Total Brasil]

**Definição:** Participação das toneladas no total do Brasil do mesmo período (ignora filtros de instalação/região).

**Na operação do porto:** Peso do porto no sistema nacional.

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** Brasil: **100,0%** · Suape: **1,7%**.

```dax
DIVIDE ( [Toneladas], CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ) ) )
```
Formato: `0.0%` · Pasta: `Participação`

### [% Cabotagem]

**Definição:** Fatia das toneladas movimentada em navegação de cabotagem (entre portos brasileiros).

**Na operação do porto:** Dependência da navegação entre portos brasileiros (petróleo de plataforma, contêiner doméstico).

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** Brasil: **21,6%** · Suape: **67,2%**.

```dax
DIVIDE (
    CALCULATE ( [Toneladas], dNavegacao[Navegacao] = "Cabotagem" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)
```
Formato: `0.0%` · Pasta: `Participação`

### [% Longo Curso]

**Definição:** Fatia das toneladas movimentada em navegação de longo curso (comércio exterior).

**Na operação do porto:** Exposição ao comércio exterior.

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** Brasil: **71,7%** · Suape: **32,2%**.

```dax
DIVIDE (
    CALCULATE ( [Toneladas], dNavegacao[Navegacao] = "Longo Curso" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)
```
Formato: `0.0%` · Pasta: `Participação`

### [% Contêiner]

**Definição:** Fatia das toneladas movimentada em contêiner.

**Na operação do porto:** Quanto da carga é conteinerizada — perfil de porto concentrador de carga geral de maior valor.

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** Brasil: **11,7%** · Suape: **31,2%**.

```dax
DIVIDE (
    CALCULATE ( [Toneladas], dNaturezaCarga[NaturezaCarga] = "Contêiner" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNaturezaCarga ) )
)
```
Formato: `0.0%` · Pasta: `Participação`

### [Ranking Porto]

**Definição:** Posição por toneladas entre as instalações (ou complexos) visíveis no visual — 1 = maior.

**Na operação do porto:** Posição relativa entre os portos visíveis.

**Média, mediana ou razão:** Ranking denso por toneladas.

**Exemplo (2025):** Suape aparece em 13º num ranking com todas as instalações.

```dax
VAR T = [Toneladas]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( T ), BLANK (),
        ISINSCOPE ( dInstalacao[Instalacao] ) || ISINSCOPE ( dInstalacao[PortoBenchmarkNE] ),
            RANKX (
                ALLSELECTED ( dInstalacao[Instalacao], dInstalacao[PortoBenchmarkNE] ),
                [Toneladas], , DESC, DENSE
            ),
        ISINSCOPE ( dInstalacao[ComplexoPortuario] ),
            RANKX ( ALLSELECTED ( dInstalacao[ComplexoPortuario] ), [Toneladas], , DESC, DENSE )
    )
```
Formato: `0` · Pasta: `Participação`

### [Ranking Suape Brasil]

**Definição:** Posição de Suape entre todas as instalações do Brasil por toneladas no período.

**Na operação do porto:** Posição de Suape no país.

**Média, mediana ou razão:** Contagem de instalações com mais toneladas + 1.

**Exemplo (2025):** **13º**.

```dax
VAR ToneladasSuape =
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
VAR Todas =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[Instalacao] ), "@t", [Toneladas] ),
        REMOVEFILTERS ( dInstalacao )
    )
RETURN
    IF ( NOT ISBLANK ( ToneladasSuape ), COUNTROWS ( FILTER ( Todas, [@t] > ToneladasSuape ) ) + 1 )
```
Formato: `0` · Pasta: `Participação`

## Eficiência

### [Espera Média (h)]

**Definição:** Média das horas entre a chegada do navio e a atracação. Sensível a filas longas.

**Na operação do porto:** Custo de fila: horas de navio parado esperando berço (sobre-estadia/demurrage).

**Média, mediana ou razão:** Média — útil para custo total de fila, mas puxada por poucos navios que esperam semanas.

**Exemplo (2025):** Brasil: **39,0 h** · Suape: **34,7 h**.

```dax
AVERAGE ( fAtracacao[EsperaAtracacao_h] )
```
Formato: `#,0.0` · Pasta: `Eficiência`

### [Espera Mediana (h)]

**Definição:** Mediana das horas entre chegada e atracação: a espera do navio 'típico', sem distorção das filas extremas.

**Na operação do porto:** A espera do navio típico. É o indicador de gargalo usado no painel.

**Média, mediana ou razão:** Mediana — a distribuição da espera tem cauda longa (mediana nacional ~1–2 h, média ~40 h); a mediana não é distorcida pelas filas extremas.

**Exemplo (2025):** Brasil: **1,4 h** · Suape: **4,3 h**.

```dax
MEDIAN ( fAtracacao[EsperaAtracacao_h] )
```
Formato: `#,0.0` · Pasta: `Eficiência`

### [Tempo Atracado Médio (h)]

**Definição:** Média das horas entre atracação e desatracação (ocupação do berço por navio).

**Na operação do porto:** Quanto tempo cada navio ocupa o berço — define a capacidade de berço.

**Média, mediana ou razão:** Média — o tempo atracado é mais simétrico e somável (ocupação total = média × nº).

**Exemplo (2025):** Brasil: **26,8 h** · Suape: **33,7 h**.

```dax
AVERAGE ( fAtracacao[Atracado_h] )
```
Formato: `#,0.0` · Pasta: `Eficiência`

### [Tempo de Operação Médio (h)]

**Definição:** Média das horas entre o início e o fim da operação de carga/descarga.

**Na operação do porto:** Tempo efetivo de carga/descarga por navio.

**Média, mediana ou razão:** Média, pelo mesmo motivo.

**Exemplo (2025):** Brasil: **19,4 h** · Suape: **24,7 h**.

```dax
AVERAGE ( fAtracacao[Operacao_h] )
```
Formato: `#,0.0` · Pasta: `Eficiência`

### [% Atracado em Operação]

**Definição:** Horas de operação ÷ horas atracado (só atracações com os dois tempos). Quanto do tempo no berço é operação de fato.

**Na operação do porto:** Eficiência do uso do berço: o restante do tempo atracado é espera de início, paralisações, documentação e espera de desatracação.

**Média, mediana ou razão:** Razão de somas (horas de operação ÷ horas atracado), não média de percentuais.

**Exemplo (2025):** Brasil: **73,1%** · Suape: **74,5%**.

```dax
VAR HorasOperacao =
    CALCULATE (
        SUM ( fAtracacao[Operacao_h] ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Operacao_h] ) ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Atracado_h] ) )
    )
VAR HorasAtracado =
    CALCULATE (
        SUM ( fAtracacao[Atracado_h] ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Operacao_h] ) ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Atracado_h] ) )
    )
RETURN
    DIVIDE ( HorasOperacao, HorasAtracado )
```
Formato: `0.0%` · Pasta: `Eficiência`

### [Prancha Média Operacional (t/h)]

**Definição:** Toneladas ÷ horas de operação (razão de somas, só atracações com tempo de operação > 0).

**Na operação do porto:** Produtividade dos equipamentos/terno durante a operação.

**Média, mediana ou razão:** Razão de somas: toneladas ÷ horas de operação. Média de pranchas por navio daria o mesmo peso a uma barcaça e a um capesize.

**Exemplo (2025):** Brasil: **765 t/h** · Suape: **618 t/h**.

```dax
DIVIDE (
    CALCULATE ( SUM ( fAtracacao[Toneladas] ), KEEPFILTERS ( fAtracacao[Operacao_h] > 0 ) ),
    CALCULATE ( SUM ( fAtracacao[Operacao_h] ), KEEPFILTERS ( fAtracacao[Operacao_h] > 0 ) )
)
```
Formato: `#,0` · Pasta: `Eficiência`

### [Prancha Média Geral (t/h)]

**Definição:** Toneladas ÷ horas atracado (razão de somas): produtividade considerando todo o tempo no berço.

**Na operação do porto:** Produtividade do berço considerando todo o tempo atracado.

**Média, mediana ou razão:** Razão de somas: toneladas ÷ horas atracado.

**Exemplo (2025):** Brasil: **553 t/h** · Suape: **456 t/h**.

```dax
DIVIDE (
    CALCULATE ( SUM ( fAtracacao[Toneladas] ), KEEPFILTERS ( fAtracacao[Atracado_h] > 0 ) ),
    CALCULATE ( SUM ( fAtracacao[Atracado_h] ), KEEPFILTERS ( fAtracacao[Atracado_h] > 0 ) )
)
```
Formato: `#,0` · Pasta: `Eficiência`

### [Horas Paralisadas]

**Definição:** Soma das horas de paralisação registradas durante as atracações (chuva, quebra, espera de carga etc.).

**Na operação do porto:** Horas perdidas por chuva, quebra, falta de carga etc. — mostra onde agir.

**Média, mediana ou razão:** Soma.

**Exemplo (2025):** Brasil: **195.736** · Suape: **3.299**.

```dax
SUM ( fParalisacao[HorasParalisadas] )
```
Formato: `#,0` · Pasta: `Eficiência`

### [Espera Mediana Suape (h)]

**Definição:** Espera mediana de Suape no período, independentemente do porto filtrado.

**Na operação do porto:** Espera do navio típico em Suape.

**Média, mediana ou razão:** Mediana (ver Espera Mediana).

**Exemplo (2025):** **4,3 h**.

```dax
CALCULATE ( [Espera Mediana (h)], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
```
Formato: `#,0.0` · Pasta: `Eficiência\Benchmark Nordeste`

### [Espera Mediana Média Pares (h)]

**Definição:** Média simples das esperas medianas dos 8 pares do Nordeste (Pecém, Itaqui, Salvador, Aratu, Recife, Natal, Cabedelo, Maceió).

**Na operação do porto:** Referência regional para Suape.

**Média, mediana ou razão:** Média simples das medianas dos 8 pares (cada porto pesa igual). Atenção: Itaqui, com filas de granel de vários dias, puxa essa média para cima.

**Exemplo (2025):** **26,4 h**.

```dax
VAR Pares =
    CALCULATETABLE (
        VALUES ( dInstalacao[PortoBenchmarkNE] ),
        REMOVEFILTERS ( dInstalacao ),
        dInstalacao[GrupoBenchmark] = "Pares do Nordeste"
    )
RETURN
    AVERAGEX (
        Pares,
        VAR Porto = dInstalacao[PortoBenchmarkNE]
        RETURN
            CALCULATE (
                [Espera Mediana (h)],
                REMOVEFILTERS ( dInstalacao ),
                dInstalacao[PortoBenchmarkNE] = Porto
            )
    )
```
Formato: `#,0.0` · Pasta: `Eficiência\Benchmark Nordeste`

### [Diferença Espera Suape vs Pares (h)]

**Definição:** Espera mediana de Suape menos a média dos pares (negativo = Suape espera menos).

**Na operação do porto:** Vantagem (negativa) ou desvantagem (positiva) de Suape.

**Média, mediana ou razão:** Diferença simples.

**Exemplo (2025):** **-22,1 h**.

```dax
[Espera Mediana Suape (h)] - [Espera Mediana Média Pares (h)]
```
Formato: `+#,0.0;-#,0.0;0.0` · Pasta: `Eficiência\Benchmark Nordeste`

## Volume

### [Toneladas Suape]

**Definição:** Toneladas de Suape no período.

**Na operação do porto:** Volume de Suape.

**Média, mediana ou razão:** Soma.

**Exemplo (2025):** **24.253.346**.

```dax
CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
```
Formato: `#,0` · Pasta: `Volume\Suape`

### [TEU Suape]

**Definição:** TEU movimentados em Suape no período.

**Na operação do porto:** Contêineres de Suape.

**Média, mediana ou razão:** Soma.

**Exemplo (2025):** **698.177**.

```dax
CALCULATE ( [TEU], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
```
Formato: `#,0` · Pasta: `Volume\Suape`

### [Var % Toneladas Suape AA]

**Definição:** Variação de toneladas de Suape vs. ano anterior.

**Na operação do porto:** Crescimento de Suape.

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** **-2,3%**.

```dax
CALCULATE ( [Var % Toneladas AA], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
```
Formato: `+0.0%;-0.0%;0.0%` · Pasta: `Volume\Suape`

## Participação

### [% Contêiner Suape]

**Definição:** Fatia de contêiner nas toneladas de Suape.

**Na operação do porto:** Perfil de carga de Suape.

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** **31,2%**.

```dax
CALCULATE ( [% Contêiner], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
```
Formato: `0.0%` · Pasta: `Participação`

## Auxiliares

### [Última Atualização]

**Definição:** Texto com o último mês de dado da ANTAQ e a data de processamento do pipeline.

```dax
"Dados ANTAQ até " & FORMAT ( MAX ( Meta[UltimoMesDisponivel] ), "mm/yyyy" )
    & " · processado em " & FORMAT ( MAX ( Meta[DataProcessamento] ), "dd/mm/yyyy" )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Título Dinâmico Período]

**Definição:** Texto do período filtrado com dado (ex.: 'em 2025', 'de 2021 a 2025', 'em jan/2026').

```dax
VAR DataIni = CALCULATE ( MIN ( dCalendario[Data] ), dCalendario[MesComDado] = TRUE () )
VAR DataFim = CALCULATE ( MAX ( dCalendario[Data] ), dCalendario[MesComDado] = TRUE () )
VAR AnoIni = YEAR ( DataIni )
VAR AnoFim = YEAR ( DataFim )
VAR AnoCompleto = MONTH ( DataIni ) = 1 && MONTH ( DataFim ) = 12
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( DataIni ), "no período sem dados",
        AnoIni = AnoFim && AnoCompleto, "em " & AnoIni,
        AnoIni = AnoFim && MONTH ( DataIni ) = MONTH ( DataFim ), "em " & FORMAT ( DataFim, "mmm/yyyy" ),
        AnoIni = AnoFim, "de " & FORMAT ( DataIni, "mmm" ) & " a " & FORMAT ( DataFim, "mmm/yyyy" ),
        "de " & AnoIni & " a " & FORMAT ( DataFim, IF ( MONTH ( DataFim ) = 12, "yyyy", "mmm/yyyy" ) )
    )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Toneladas (Top 10)]

**Definição:** Toneladas só das 10 maiores instalações visíveis (para o gráfico de ranking).

```dax
IF ( [Ranking Porto] <= 10, [Toneladas] )
```
Formato: `#,0` · Pasta: `Auxiliares`

### [Toneladas (Top 10 mercadorias)]

**Definição:** Toneladas só das 10 maiores mercadorias visíveis.

```dax
VAR Posicao =
    IF (
        ISINSCOPE ( dMercadoria[Mercadoria] ),
        RANKX ( ALLSELECTED ( dMercadoria[Mercadoria] ), [Toneladas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 10, [Toneladas] )
```
Formato: `#,0` · Pasta: `Auxiliares`

### [Horas Paralisadas (Top 10 motivos)]

**Definição:** Horas paralisadas só dos 10 motivos com mais horas no contexto.

```dax
VAR Posicao =
    IF (
        ISINSCOPE ( fParalisacao[MotivoParalisacao] ),
        RANKX ( ALLSELECTED ( fParalisacao[MotivoParalisacao] ), [Horas Paralisadas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 10, [Horas Paralisadas] )
```
Formato: `#,0` · Pasta: `Auxiliares`

### [Cor Destaque Suape]

**Definição:** Cor das barras/pontos: dourado para Suape, azul para as demais (formatação condicional por valor de campo).

```dax
IF ( SELECTEDVALUE ( dInstalacao[EhSuape], 0 ) = 1, "#C9A96E", "#8FB4D9" )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Cor Texto Suape]

**Definição:** Cor do texto: dourado na linha de Suape, branco nas demais.

```dax
IF ( SELECTEDVALUE ( dInstalacao[EhSuape], 0 ) = 1, "#C9A96E", "#FFFFFF" )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Cor Calor Espera]

**Definição:** Cor do mapa de calor da espera mediana: até 2 h, 6 h, 24 h, 72 h e acima de 72 h.

```dax
VAR Espera = [Espera Mediana (h)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( Espera ), BLANK (),
        Espera <= 2, "#1E3A2F",
        Espera <= 6, "#2F5D46",
        Espera <= 24, "#7A6A3A",
        Espera <= 72, "#A0522D",
        "#8B1E2D"
    )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Cor Benchmark Espera]

**Definição:** Verde se a espera mediana do porto é menor ou igual à média dos pares; vermelho se maior.

```dax
VAR Espera = [Espera Mediana (h)]
RETURN
    IF (
        NOT ISBLANK ( Espera ),
        IF ( Espera <= [Espera Mediana Média Pares (h)], "#1E3A2F", "#4A1C14" )
    )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Título KPI Brasil]

**Definição:** Título da página Visão Geral.

```dax
VAR Mt = [Toneladas] / 1000000
VAR Variacao = [Var % Toneladas AA]
RETURN
    "Portos brasileiros movimentaram " & FORMAT ( Mt, "#,0.0" ) & " milhões de t " & [Título Dinâmico Período]
        & IF ( NOT ISBLANK ( Variacao ), " (" & FORMAT ( Variacao, "+0.0%;-0.0%" ) & " vs. ano anterior)" )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Linha Mensal]

**Definição:** Título do gráfico de linha mensal.

```dax
"Toneladas por mês " & [Título Dinâmico Período] & " x mesmo mês do ano anterior"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Região]

**Definição:** Título do gráfico por região.

```dax
VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Regiao] ), "@t", [Toneladas] ), [@t], DESC )
VAR Nome = MAXX ( Top, dInstalacao[Regiao] )
VAR Fatia = DIVIDE ( MAXX ( Top, [@t] ), [Toneladas] )
RETURN
    Nome & " concentra " & FORMAT ( Fatia, "0%" ) & " da carga " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Top 10]

**Definição:** Título do ranking de instalações.

```dax
VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Instalacao] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Top, dInstalacao[Instalacao] ) & " lidera com " & FORMAT ( MAXX ( Top, [@t] ) / 1000000, "#,0.0" )
        & " milhões de t " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Benchmark Espera]

**Definição:** Título da página Nordeste & Suape: conclusão sobre a espera de Suape vs. pares.

```dax
VAR Dif = [Diferença Espera Suape vs Pares (h)]
RETURN
    IF (
        ISBLANK ( Dif ), "Espera mediana: Suape x média dos pares",
        "Suape opera com espera mediana " & FORMAT ( ABS ( Dif ), "#,0.0" ) & " h "
            & IF ( Dif <= 0, "menor", "maior" ) & " que a média dos pares " & [Título Dinâmico Período]
    )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Crescimento Pares]

**Definição:** Título das barras de crescimento.

```dax
VAR Pares =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[PortoBenchmarkNE] ), "@v", [Var % Toneladas AA] ),
        NOT ISBLANK ( dInstalacao[PortoBenchmarkNE] )
    )
VAR Top = TOPN ( 1, FILTER ( Pares, NOT ISBLANK ( [@v] ) ), [@v], DESC )
RETURN
    IF (
        ISEMPTY ( Top ), "Crescimento vs. ano anterior",
        "Maior crescimento " & [Título Dinâmico Período] & ": " & MAXX ( Top, dInstalacao[PortoBenchmarkNE] )
            & " (" & FORMAT ( MAXX ( Top, [@v] ), "+0.0%;-0.0%" ) & ")"
    )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Ranking Suape]

**Definição:** Texto do cartão de ranking de Suape.

```dax
"Suape é a " & [Ranking Suape Brasil] & "ª maior instalação do Brasil " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Mapa de Calor]

**Definição:** Título do mapa de calor.

```dax
VAR Top =
    TOPN (
        1,
        CALCULATETABLE (
            ADDCOLUMNS ( VALUES ( dInstalacao[PortoBenchmarkNE] ), "@e", [Espera Mediana (h)] ),
            NOT ISBLANK ( dInstalacao[PortoBenchmarkNE] )
        ),
        [@e], DESC
    )
RETURN
    "Maior espera mediana entre os pares " & [Título Dinâmico Período] & ": " & MAXX ( Top, dInstalacao[PortoBenchmarkNE] )
        & " (" & FORMAT ( MAXX ( Top, [@e] ), "#,0" ) & " h)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Operação]

**Definição:** Título das barras de % atracado em operação.

```dax
"Suape usa " & FORMAT ( CALCULATE ( [% Atracado em Operação], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 ), "0%" )
    & " do tempo atracado operando " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Paralisação]

**Definição:** Título das horas paralisadas por motivo.

```dax
VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( fParalisacao[MotivoParalisacao] ), "@h", [Horas Paralisadas] ), [@h], DESC )
RETURN
    IF (
        ISEMPTY ( Top ), "Horas paralisadas por motivo",
        "Principal causa de paralisação: " & MAXX ( Top, fParalisacao[MotivoParalisacao] ) & " ("
            & FORMAT ( DIVIDE ( MAXX ( Top, [@h] ), [Horas Paralisadas] ), "0%" ) & " das horas)"
    )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Dispersão]

**Definição:** Título da dispersão espera x prancha.

```dax
"Portos públicos " & [Título Dinâmico Período] & ": espera mediana (h) x prancha operacional (t/h)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Natureza]

**Definição:** Título da composição por natureza de carga.

```dax
VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dNaturezaCarga[NaturezaCarga] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Top, dNaturezaCarga[NaturezaCarga] ) & " responde por " & FORMAT ( DIVIDE ( MAXX ( Top, [@t] ), [Toneladas] ), "0%" )
        & " da carga " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Mercadorias]

**Definição:** Título do top mercadorias.

```dax
VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dMercadoria[Mercadoria] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Top, dMercadoria[Mercadoria] ) & " é a principal mercadoria: " & FORMAT ( DIVIDE ( MAXX ( Top, [@t] ), [Toneladas] ), "0%" )
        & " das toneladas"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Sentido]

**Definição:** Título do embarque x desembarque.

```dax
VAR Emb = CALCULATE ( [Toneladas], dSentido[Sentido] = "Embarque" )
RETURN
    FORMAT ( DIVIDE ( Emb, CALCULATE ( [Toneladas], REMOVEFILTERS ( dSentido ) ) ), "0%" ) & " das toneladas são embarque"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Navegação]

**Definição:** Título da movimentação por navegação.

```dax
"Longo curso: " & FORMAT ( [% Longo Curso], "0%" ) & " · cabotagem: " & FORMAT ( [% Cabotagem], "0%" )
    & " das toneladas"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

