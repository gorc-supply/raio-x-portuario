# Rascunho de post (LinkedIn)

> Revisar antes de postar: trocar LINK_PUBLICO pelo link do painel e anexar o vídeo. Números conferidos em `docs/valores_referencia.md` (seção 4).

---

Moro em Recife e passo por Suape com frequência, mas nunca tinha olhado os números do porto de perto. Resolvi fazer isso com os dados abertos da ANTAQ.

O que mais me chamou atenção: a tonelagem de Suape praticamente não mexeu nos últimos anos (24,3 milhões de t em 2025), mas o contêiner cresceu. Saiu de 519 mil TEU em 2021 para 698 mil TEU em 2025, 34,6% a mais. O porto está movimentando carga de mais valor sem crescer em peso.

Na fila, Suape vai bem: espera mediana de 4,3 h para atracar em 2025, contra 26,4 h na média dos vizinhos do Nordeste. Mas tem um detalhe que só aparece abrindo por tipo de carga: navio de contêiner espera 0,8 h, navio de granel líquido espera 28,8 h. Quem quiser melhorar a fila de Suape tem que olhar o cais de líquidos.

Montei tudo num painel Power BI público, com o pipeline em Python/DuckDB no GitHub. O total que eu calculo bate com o total oficial da ANTAQ com diferença de no máximo 1,16% por ano. Isso foi o que mais deu trabalho, e o que me deixa confortável em publicar.

Painel: LINK_PUBLICO
Código e método: github.com/gorc-supply/raio-x-portuario

Se você trabalha com porto ou com logística no Nordeste, me conta se esses números batem com o que você vê na operação.

#supplychain #logistica #powerbi #dadosabertos #portos
