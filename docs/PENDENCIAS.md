# Pendências para o Gabriel

Já feito: repositório público com release v1.0, README com vídeo, PDF, capturas e passo a passo do PBIP, e portfólio com o card publicado.

**Fechadas (decisão D27):** publicar no Power BI Service, conferir o link público, colocar o link no README e no portfólio e trocar o mapa para Azure Maps. O "Publicar na Web" está bloqueado pelo administrador da conta institucional e não vai existir link público; o painel é distribuído por vídeo, PDF e PBIP.

---

## 1. Postar no LinkedIn — 10 min

1. Rascunho em [post_linkedin.md](post_linkedin.md). Releia no seu tom.
2. Anexe o vídeo `docs/video/raio-x-portuario.mp4` (78 s, 2,7 MB).

## 2. Quando o portal da ANTAQ voltar: trocar para a fonte oficial — 30 min

Os dados vêm de um espelho público fixado no Hugging Face (ver [DECISOES.md](DECISOES.md), D02); o total bate com o oficial com diferença de −0,13% a +1,16% ao ano.

1. Encontre a página "Base de Dados" do Estatístico Aquaviário a partir de `https://www.gov.br/antaq/pt-br/assuntos/estatistica` (o endereço antigo era `https://web3.antaq.gov.br/ea/sense/download.html`).
2. Baixe, para **cada ano de 2021 a 2025**, os arquivos de **Atracação, Carga, Tempos de Atracação e Tempos de Atracação Paralisação** (o zip "todas as tabelas do ano" também serve; o pipeline procura `{ano}Atracacao.txt`, `{ano}Carga.txt`, `{ano}TemposAtracacao.txt` e `{ano}TemposAtracacaoParalisacao.txt` dentro de qualquer `.zip`), mais o dicionário de dados e a tabela auxiliar **Mercadoria**.
3. Coloque os `.zip` em `data\raw\antaq_oficial\` e rode `.venv\Scripts\python etl\run_all.py`.
4. **Confira o layout do TXT oficial:** o leitor assume `;`, cabeçalho na 1ª linha, vírgula decimal e datas `dd/mm/aaaa hh:mm:ss`. Isso não pôde ser testado com arquivo real; se a conciliação ou algum teste falhar, o ajuste fica em `_sql_txt_oficial()` de `etl/02_transform.py`.
5. Para incluir 2026 quando o ano fechar: `ANO_FINAL` em `etl/config.py` e o `Fim` do calendário em `etl/pbip_modelo.py`; depois regenerar o PBIP, as capturas e o vídeo (`ferramentas/sessao_final.py` e `ferramentas/entregaveis.py`).
