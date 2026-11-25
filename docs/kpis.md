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

### [Toneladas (Mi t)]

**Definição:** Toneladas em milhões, para eixos e rótulos de gráfico.

```dax
DIVIDE ( [Toneladas], 1000000 )
```
Formato: `#,0.0" Mi t"` · Pasta: `Volume`

### [Toneladas AA]

**Definição:** Toneladas do mesmo período do ano anterior, só nos meses que têm dado no período atual.

**Na operação do porto:** Base de comparação para separar crescimento real de sazonalidade.

**Média, mediana ou razão:** Soma no mesmo recorte de meses do ano anterior (evita comparar mês parcial com ano cheio).

**Exemplo (2025):** Brasil: **1.325.915.577** · Suape: **24.830.911**.

```dax
// meses do contexto atual que têm dado publicado
VAR DatasComDado =
    CALCULATETABLE ( VALUES ( dCalendario[Data] ), dCalendario[Mês com Dado] = TRUE () )
RETURN
    IF (
        NOT ISEMPTY ( DatasComDado ),
        CALCULATE ( [Toneladas], SAMEPERIODLASTYEAR ( DatasComDado ) )
    )
```
Formato: `#,0` · Pasta: `Volume`

### [Toneladas AA (Mi t)]

**Definição:** Toneladas do ano anterior em milhões.

```dax
DIVIDE ( [Toneladas AA], 1000000 )
```
Formato: `#,0.0" Mi t"` · Pasta: `Volume`

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
Formato: `+0.0%;"−"0.0%;0.0%` · Pasta: `Volume`

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
    CALCULATE ( [Toneladas], dNavegacao[Navegação] = "Cabotagem" ),
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
    CALCULATE ( [Toneladas], dNavegacao[Navegação] = "Longo Curso" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)
```
Formato: `0.0%` · Pasta: `Participação`

### [% Contêiner]

**Definição:** Fatia das toneladas movimentada em contêiner (0% quando o porto não movimenta contêiner).

**Na operação do porto:** Quanto da carga é conteinerizada — perfil de porto concentrador de carga geral de maior valor.

**Média, mediana ou razão:** Razão de somas.

**Exemplo (2025):** Brasil: **11,7%** · Suape: **31,2%**.

```dax
IF (
    NOT ISBLANK ( [Toneladas] ),
    DIVIDE (
        CALCULATE ( [Toneladas], dNaturezaCarga[Natureza da Carga] = "Contêiner" ),
        CALCULATE ( [Toneladas], REMOVEFILTERS ( dNaturezaCarga ) )
    ) + 0
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
        // a coluna Porto é ordenada por OrdemBenchmark: o visual agrupa pelas duas, então o RANKX itera o par
        ISINSCOPE ( dInstalacao[Porto (benchmark NE)] ),
            RANKX (
                ALLSELECTED ( dInstalacao[Porto (benchmark NE)], dInstalacao[OrdemBenchmark] ),
                [Toneladas], , DESC, DENSE
            ),
        ISINSCOPE ( dInstalacao[Instalação] ),
            RANKX ( ALLSELECTED ( dInstalacao[Instalação] ), [Toneladas], , DESC, DENSE ),
        ISINSCOPE ( dInstalacao[Complexo Portuário] ),
            RANKX ( ALLSELECTED ( dInstalacao[Complexo Portuário] ), [Toneladas], , DESC, DENSE )
    )
```
Formato: `#,0` · Pasta: `Participação`

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
        ADDCOLUMNS ( VALUES ( dInstalacao[Instalação] ), "@t", [Toneladas] ),
        REMOVEFILTERS ( dInstalacao )
    )
RETURN
    IF ( NOT ISBLANK ( ToneladasSuape ), COUNTROWS ( FILTER ( Todas, [@t] > ToneladasSuape ) ) + 1 )
```
Formato: `#,0` · Pasta: `Participação`

## Eficiência

### [Espera Média (h)]

**Definição:** Média das horas entre a chegada do navio e a atracação. Sensível a filas longas.

**Na operação do porto:** Custo de fila: horas de navio parado esperando berço (sobre-estadia/demurrage).

**Média, mediana ou razão:** Média — útil para custo total de fila, mas puxada por poucos navios que esperam semanas.

**Exemplo (2025):** Brasil: **39,0 h** · Suape: **34,7 h**.

```dax
AVERAGE ( fAtracacao[EsperaAtracacao_h] )
```
Formato: `#,0.0" h"` · Pasta: `Eficiência`

### [Espera Mediana (h)]

**Definição:** Mediana das horas entre chegada e atracação: a espera do navio típico, sem distorção das filas extremas.

**Na operação do porto:** A espera do navio típico. É o indicador de gargalo usado no painel.

**Média, mediana ou razão:** Mediana — a distribuição da espera tem cauda longa (mediana nacional ~1–2 h, média ~40 h); a mediana não é distorcida pelas filas extremas.

**Exemplo (2025):** Brasil: **1,4 h** · Suape: **4,3 h**.

```dax
MEDIAN ( fAtracacao[EsperaAtracacao_h] )
```
Formato: `#,0.0" h"` · Pasta: `Eficiência`

### [Tempo Atracado Médio (h)]

**Definição:** Média das horas entre atracação e desatracação (ocupação do berço por navio).

**Na operação do porto:** Quanto tempo cada navio ocupa o berço — define a capacidade de berço.

**Média, mediana ou razão:** Média — o tempo atracado é mais simétrico e somável (ocupação total = média × nº).

**Exemplo (2025):** Brasil: **26,8 h** · Suape: **33,7 h**.

```dax
AVERAGE ( fAtracacao[Atracado_h] )
```
Formato: `#,0.0" h"` · Pasta: `Eficiência`

### [Tempo de Operação Médio (h)]

**Definição:** Média das horas entre o início e o fim da operação de carga/descarga.

**Na operação do porto:** Tempo efetivo de carga/descarga por navio.

**Média, mediana ou razão:** Média, pelo mesmo motivo.

**Exemplo (2025):** Brasil: **19,4 h** · Suape: **24,7 h**.

```dax
AVERAGE ( fAtracacao[Operacao_h] )
```
Formato: `#,0.0" h"` · Pasta: `Eficiência`

### [% Atracado em Operação]

**Definição:** Horas de operação ÷ horas atracado (só atracações com os dois tempos): quanto do tempo no berço é operação.

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
Formato: `#,0" t/h"` · Pasta: `Eficiência`

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
Formato: `#,0" t/h"` · Pasta: `Eficiência`

### [Horas Paralisadas]

**Definição:** Soma das horas de paralisação registradas durante as atracações (chuva, quebra, espera de carga etc.).

**Na operação do porto:** Horas perdidas por chuva, quebra, falta de carga etc. — mostra onde agir.

**Média, mediana ou razão:** Soma.

**Exemplo (2025):** Brasil: **195.736** · Suape: **3.299**.

```dax
SUM ( fParalisacao[HorasParalisadas] )
```
Formato: `#,0" h"` · Pasta: `Eficiência`

### [Espera Mediana Suape (h)]

**Definição:** Espera mediana de Suape no período, independentemente do porto filtrado.

**Na operação do porto:** Espera do navio típico em Suape.

**Média, mediana ou razão:** Mediana (ver Espera Mediana).

**Exemplo (2025):** **4,3 h**.

```dax
CALCULATE ( [Espera Mediana (h)], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
```
Formato: `#,0.0" h"` · Pasta: `Eficiência\Benchmark Nordeste`

### [Espera Mediana Média Pares (h)]

**Definição:** Média simples das esperas medianas dos 8 pares do Nordeste (Pecém, Itaqui, Salvador, Aratu, Recife, Natal, Cabedelo, Maceió).

**Na operação do porto:** Referência regional para Suape.

**Média, mediana ou razão:** Média simples das medianas dos 8 pares (cada porto pesa igual). Atenção: Itaqui, com filas de granel de vários dias, puxa essa média para cima.

**Exemplo (2025):** **26,4 h**.

```dax
VAR Pares =
    CALCULATETABLE (
        VALUES ( dInstalacao[Porto (benchmark NE)] ),
        REMOVEFILTERS ( dInstalacao ),
        dInstalacao[Grupo do Benchmark] = "Pares do Nordeste"
    )
RETURN
    AVERAGEX (
        Pares,
        VAR Porto = dInstalacao[Porto (benchmark NE)]
        RETURN
            CALCULATE (
                [Espera Mediana (h)],
                REMOVEFILTERS ( dInstalacao ),
                dInstalacao[Porto (benchmark NE)] = Porto
            )
    )
```
Formato: `#,0.0" h"` · Pasta: `Eficiência\Benchmark Nordeste`

### [Diferença Espera Suape vs Pares (h)]

**Definição:** Espera mediana de Suape menos a média dos pares (negativo = Suape espera menos).

**Na operação do porto:** Vantagem (negativa) ou desvantagem (positiva) de Suape.

**Média, mediana ou razão:** Diferença simples.

**Exemplo (2025):** **-22,1 h**.

```dax
[Espera Mediana Suape (h)] - [Espera Mediana Média Pares (h)]
```
Formato: `+#,0.0" h";"−"#,0.0" h";0.0" h"` · Pasta: `Eficiência\Benchmark Nordeste`

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
Formato: `+0.0%;"−"0.0%;0.0%` · Pasta: `Volume\Suape`

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

### [Latitude do Complexo]

**Definição:** Latitude do complexo portuário (média das coordenadas oficiais ponderada por toneladas).

```dax
MAX ( dInstalacao[Latitude do Complexo] )
```
Formato: `0.000` · Pasta: `Auxiliares\Mapa`

### [Longitude do Complexo]

**Definição:** Longitude do complexo portuário (média das coordenadas oficiais ponderada por toneladas).

```dax
MAX ( dInstalacao[Longitude do Complexo] )
```
Formato: `0.000` · Pasta: `Auxiliares\Mapa`

### [Destaque no Mapa]

**Definição:** 1 para Suape e para os 5 complexos com mais toneladas no contexto (os que recebem rótulo no mapa).

```dax
VAR Posicao =
    IF (
        ISINSCOPE ( dInstalacao[Complexo Portuário] ),
        RANKX ( ALLSELECTED ( dInstalacao[Complexo Portuário] ), [Toneladas], , DESC, DENSE )
    )
RETURN
    IF ( NOT ISBLANK ( [Toneladas] ) && ( Posicao <= 5 || MAX ( dInstalacao[EhSuape] ) = 1 ), 1 )
```
Formato: `#,0` · Pasta: `Auxiliares\Mapa`

### [Latitude (rótulo)]

**Definição:** Latitude só dos complexos destacados (camada de rótulos).

```dax
IF ( [Destaque no Mapa] = 1, MAX ( dInstalacao[Latitude do Rótulo] ) )
```
Formato: `0.000` · Pasta: `Auxiliares\Mapa`

### [Longitude (rótulo)]

**Definição:** Longitude só dos complexos destacados (camada de rótulos).

```dax
IF ( [Destaque no Mapa] = 1, MAX ( dInstalacao[Longitude do Rótulo] ) )
```
Formato: `0.000` · Pasta: `Auxiliares\Mapa`

### [UF do Complexo]

**Definição:** UF(s) do complexo portuário (dica de ferramenta).

```dax
CONCATENATEX ( VALUES ( dInstalacao[UF] ), dInstalacao[UF], "/" )
```
Formato: `texto` · Pasta: `Auxiliares\Mapa`

### [Rótulo Toneladas]

**Definição:** Toneladas em milhões com unidade (cartão).

```dax
VAR v = [Toneladas (Mi t)]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0.0" ) & " Mi t" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Var % AA]

**Definição:** Variação vs. ano anterior com sinal (cartão).

```dax
VAR v = [Var % Toneladas AA]
RETURN
    IF (
        NOT ISBLANK ( v ),
        IF ( v >= 0, "+", "−" ) & FORMAT ( ABS ( v ), "0.0%" )
    )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Atracações]

**Definição:** Nº de atracações com separador de milhar (cartão).

```dax
VAR v = [Nº Atracações]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0" ) )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Espera Mediana]

**Definição:** Espera mediana com 1 casa e unidade (cartão).

```dax
VAR v = [Espera Mediana (h)]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0.0" ) & " h" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Prancha Operacional]

**Definição:** Prancha operacional inteira com unidade (cartão).

```dax
VAR v = [Prancha Média Operacional (t/h)]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0" ) & " t/h" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Tempo Atracado]

**Definição:** Tempo atracado médio (cartão).

```dax
VAR v = [Tempo Atracado Médio (h)]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0.0" ) & " h" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo % Atracado em Operação]

**Definição:** % do tempo atracado em operação (cartão).

```dax
VAR v = [% Atracado em Operação]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "0.0%" ) )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Horas Paralisadas]

**Definição:** Horas paralisadas em milhares (cartão).

```dax
VAR v = DIVIDE ( [Horas Paralisadas], 1000 )
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0.0" ) & " mil h" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo TEU]

**Definição:** TEU em milhares (cartão).

```dax
VAR v = DIVIDE ( [TEU], 1000 )
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0" ) & " mil TEU" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo % Contêiner]

**Definição:** % contêiner (cartão).

```dax
VAR v = [% Contêiner]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "0.0%" ) )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo % Longo Curso]

**Definição:** % longo curso (cartão).

```dax
VAR v = [% Longo Curso]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "0.0%" ) )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo % Cabotagem]

**Definição:** % cabotagem (cartão).

```dax
VAR v = [% Cabotagem]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "0.0%" ) )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Toneladas Suape]

**Definição:** Toneladas de Suape em milhões (cartão).

```dax
VAR v = DIVIDE ( [Toneladas Suape], 1000000 )
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0.0" ) & " Mi t" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Var % Suape]

**Definição:** Variação de Suape vs. ano anterior (cartão).

```dax
VAR v = [Var % Toneladas Suape AA]
RETURN
    IF (
        NOT ISBLANK ( v ),
        IF ( v >= 0, "+", "−" ) & FORMAT ( ABS ( v ), "0.0%" )
    )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo TEU Suape]

**Definição:** TEU de Suape em milhares (cartão).

```dax
VAR v = DIVIDE ( [TEU Suape], 1000 )
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "#,0" ) & " mil TEU" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo % Contêiner Suape]

**Definição:** % contêiner de Suape (cartão).

```dax
VAR v = [% Contêiner Suape]
RETURN
    IF ( NOT ISBLANK ( v ), FORMAT ( v, "0.0%" ) )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Rótulo Ranking Suape]

**Definição:** Posição de Suape no Brasil (cartão).

```dax
VAR r = [Ranking Suape Brasil]
RETURN
    IF ( NOT ISBLANK ( r ), r & "ª do Brasil" )
```
Formato: `texto` · Pasta: `Auxiliares\Rótulos`

### [Última Atualização]

**Definição:** Texto com o recorte e a data de processamento do pipeline.

```dax
"Dados ANTAQ 2021–2025 (anos completos) · processado em "
    & FORMAT ( MAX ( Meta[Data de Processamento] ), "dd/mm/yyyy" )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Título Dinâmico Período]

**Definição:** Texto do período filtrado (ex.: 'em 2025', 'de 2021 a 2025').

```dax
VAR DataIni = CALCULATE ( MIN ( dCalendario[Data] ), dCalendario[Mês com Dado] = TRUE () )
VAR DataFim = CALCULATE ( MAX ( dCalendario[Data] ), dCalendario[Mês com Dado] = TRUE () )
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
        "de " & AnoIni & " a " & AnoFim
    )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Toneladas (Top 10) (Mi t)]

**Definição:** Toneladas (Mi t) só das 10 maiores instalações visíveis (ranking sem barra de rolagem).

```dax
IF ( [Ranking Porto] <= 10, [Toneladas (Mi t)] )
```
Formato: `#,0.0" Mi t"` · Pasta: `Auxiliares`

### [Toneladas (Top 10 mercadorias) (Mi t)]

**Definição:** Toneladas (Mi t) só das 10 maiores mercadorias visíveis.

```dax
VAR Posicao =
    IF (
        ISINSCOPE ( dMercadoria[Mercadoria] ),
        RANKX ( ALLSELECTED ( dMercadoria[Mercadoria] ), [Toneladas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 10, [Toneladas (Mi t)] )
```
Formato: `#,0.0" Mi t"` · Pasta: `Auxiliares`

### [Horas Paralisadas (Top 8 motivos)]

**Definição:** Horas paralisadas só dos 8 motivos com mais horas no contexto (cabe sem rolagem em qualquer zoom).

```dax
VAR Posicao =
    IF (
        ISINSCOPE ( fParalisacao[Motivo da Paralisação] ),
        RANKX ( ALLSELECTED ( fParalisacao[Motivo da Paralisação] ), [Horas Paralisadas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 8, [Horas Paralisadas] )
```
Formato: `#,0" h"` · Pasta: `Auxiliares`

### [Cor Destaque Suape]

**Definição:** Cor das barras/pontos: dourado para Suape (ou o complexo que contém Suape), azul para as demais.

```dax
IF ( MAX ( dInstalacao[EhSuape] ) = 1, "#C9A96E", "#8FB4D9" )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Cor Texto Suape]

**Definição:** Cor do texto: dourado na linha de Suape, branco nas demais.

```dax
IF ( MAX ( dInstalacao[EhSuape] ) = 1, "#C9A96E", "#FFFFFF" )
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
        Espera <= 24, "#6E5F33",
        Espera <= 72, "#8F4A28",
        "#7A1C2A"
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
        IF ( Espera <= [Espera Mediana Média Pares (h)], "#1E3A2F", "#5A2318" )
    )
```
Formato: `texto` · Pasta: `Auxiliares`

### [Título KPI Brasil]

**Definição:** Manchete da página Visão Geral.

```dax
VAR Mt = [Toneladas] / 1000000
VAR Variacao = [Var % Toneladas AA]
RETURN
    "Portos brasileiros movimentaram " & FORMAT ( Mt, "#,0.0" ) & " Mi t " & [Título Dinâmico Período]
        & IF (
            NOT ISBLANK ( Variacao ),
            " (" & IF ( Variacao >= 0, "+", "−" ) & FORMAT ( ABS ( Variacao ), "0.0%" ) & " vs. ano anterior)"
        )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Linha Mensal]

**Definição:** Título do gráfico de linha mensal.

```dax
"Toneladas por mês " & [Título Dinâmico Período] & " (cinza = ano anterior)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Região]

**Definição:** Título do gráfico por região.

```dax
VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Região] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Lider, dInstalacao[Região] ) & " concentra " & FORMAT ( DIVIDE ( MAXX ( Lider, [@t] ), [Toneladas] ), "0%" )
        & " da carga"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Top 10]

**Definição:** Título do ranking de instalações.

```dax
VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Instalação] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    "Top 10 instalações: " & MAXX ( Lider, dInstalacao[Instalação] ) & " lidera com "
        & FORMAT ( MAXX ( Lider, [@t] ) / 1000000, "#,0.0" ) & " Mi t " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Mapa]

**Definição:** Título do mapa.

```dax
"Complexos portuários " & [Título Dinâmico Período] & " (tamanho = toneladas)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Benchmark Espera]

**Definição:** Manchete da página Nordeste & Suape: espera de Suape vs. pares.

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

### [Título Tabela Benchmark]

**Definição:** Título da tabela de benchmark.

```dax
"Suape x pares " & [Título Dinâmico Período] & " · verde = espera mediana até a média dos pares"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Crescimento Pares]

**Definição:** Título das barras de crescimento.

```dax
VAR Pares =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[Porto (benchmark NE)] ), "@v", [Var % Toneladas AA] ),
        NOT ISBLANK ( dInstalacao[Porto (benchmark NE)] )
    )
VAR Lider = TOPN ( 1, FILTER ( Pares, NOT ISBLANK ( [@v] ) ), [@v], DESC )
VAR v = MAXX ( Lider, [@v] )
RETURN
    IF (
        ISEMPTY ( Lider ), "Crescimento vs. ano anterior",
        "Maior alta " & [Título Dinâmico Período] & ": " & MAXX ( Lider, dInstalacao[Porto (benchmark NE)] )
            & " (" & IF ( v >= 0, "+", "−" ) & FORMAT ( ABS ( v ), "0.0%" ) & ")"
    )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Linha Suape Pares]

**Definição:** Título da linha Suape x pares.

```dax
"Espera mediana por mês " & [Título Dinâmico Período] & ": Suape (dourado) x média dos pares (cinza)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Eficiência]

**Definição:** Manchete da página Eficiência e Gargalos.

```dax
"Navio típico esperou " & FORMAT ( [Espera Mediana (h)], "#,0.0" ) & " h para atracar " & [Título Dinâmico Período]
    & "; prancha operacional de " & FORMAT ( [Prancha Média Operacional (t/h)], "#,0" ) & " t/h"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Mapa de Calor]

**Definição:** Título do mapa de calor.

```dax
VAR Lider =
    TOPN (
        1,
        CALCULATETABLE (
            ADDCOLUMNS ( VALUES ( dInstalacao[Porto (benchmark NE)] ), "@e", [Espera Mediana (h)] ),
            NOT ISBLANK ( dInstalacao[Porto (benchmark NE)] )
        ),
        [@e], DESC
    )
RETURN
    "Espera mediana (h) por mês " & [Título Dinâmico Período] & " · maior: " & MAXX ( Lider, dInstalacao[Porto (benchmark NE)] )
        & " (" & FORMAT ( MAXX ( Lider, [@e] ), "#,0" ) & " h)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Operação]

**Definição:** Título das barras de % atracado em operação.

```dax
"Suape opera " & FORMAT ( CALCULATE ( [% Atracado em Operação], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 ), "0%" )
    & " do tempo atracado " & [Título Dinâmico Período]
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Paralisação]

**Definição:** Título das horas paralisadas por motivo.

```dax
VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( fParalisacao[Motivo da Paralisação] ), "@h", [Horas Paralisadas] ), [@h], DESC )
RETURN
    IF (
        ISEMPTY ( Lider ), "Horas paralisadas por motivo",
        "Top 8 motivos de paralisação · maior: " & MAXX ( Lider, fParalisacao[Motivo da Paralisação] ) & " ("
            & FORMAT ( DIVIDE ( MAXX ( Lider, [@h] ), [Horas Paralisadas] ), "0%" ) & ")"
    )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Dispersão]

**Definição:** Título da dispersão espera x prancha.

```dax
"Portos públicos " & [Título Dinâmico Período] & ": espera (h) x prancha (t/h)"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Perfil]

**Definição:** Manchete da página Perfil de Carga.

```dax
VAR Selecao =
    IF (
        HASONEVALUE ( dInstalacao[Instalação] ), SELECTEDVALUE ( dInstalacao[Instalação] ),
        IF ( ISFILTERED ( dInstalacao ), "Instalações selecionadas", "Brasil" )
    )
RETURN
    Selecao & " " & [Título Dinâmico Período] & ": " & FORMAT ( [Toneladas] / 1000000, "#,0.0" ) & " Mi t movimentadas"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Natureza]

**Definição:** Título da composição por natureza de carga.

```dax
VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dNaturezaCarga[Natureza da Carga] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    "Por mês · " & MAXX ( Lider, dNaturezaCarga[Natureza da Carga] ) & " responde por "
        & FORMAT ( DIVIDE ( MAXX ( Lider, [@t] ), [Toneladas] ), "0%" ) & " da carga"
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

### [Título Mercadorias]

**Definição:** Título do top mercadorias.

```dax
VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dMercadoria[Mercadoria] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    "Top 10 mercadorias · " & MAXX ( Lider, dMercadoria[Mercadoria] ) & ": "
        & FORMAT ( DIVIDE ( MAXX ( Lider, [@t] ), [Toneladas] ), "0%" ) & " das toneladas"
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
"Por navegação · longo curso " & FORMAT ( [% Longo Curso], "0%" ) & ", cabotagem " & FORMAT ( [% Cabotagem], "0%" )
```
Formato: `texto` · Pasta: `Auxiliares\Títulos`

