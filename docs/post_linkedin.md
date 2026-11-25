# Rascunho de post (LinkedIn)

> Anexar o vídeo `docs/video/raio-x-portuario.mp4` ao post. Números conferidos em `docs/valores_referencia.md` (seção 4).

---

Moro em Recife e passo por Suape com frequência, mas nunca tinha olhado os números do porto de perto. Resolvi fazer isso com os dados abertos da ANTAQ, de 2021 a 2025.

O que mais me chamou atenção: a tonelagem de Suape quase não mexeu (24,3 milhões de t em 2025), mas o contêiner cresceu. Saiu de 519 mil TEU em 2021 para 698 mil TEU em 2025, 34,6% a mais. O porto está movimentando carga de mais valor sem crescer em peso.

Na fila, Suape vai bem: espera mediana de 4,3 h para atracar em 2025, contra 26,4 h na média dos vizinhos do Nordeste. Mas tem um detalhe que só aparece abrindo por tipo de carga: navio de contêiner espera 0,8 h, navio de granel líquido espera 28,8 h. Quem quiser melhorar a fila de Suape tem que olhar o cais de líquidos.

Montei tudo num painel de Power BI, com o pipeline em Python e DuckDB no GitHub. O vídeo abaixo mostra o painel em pouco mais de um minuto. O total que eu calculo bate com o oficial da ANTAQ com diferença de no máximo 1,16% por ano, e isso foi o que mais deu trabalho.

Código, método e PDF: github.com/gorc-supply/raio-x-portuario

Se você trabalha com porto ou com logística no Nordeste, me conta se esses números batem com o que você vê na operação.

#supplychain #logistica #powerbi #dadosabertos #portos
