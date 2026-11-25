# Pendências para o Gabriel

O que só você pode fazer, em ordem. Tempo total: **~1 h** (sem contar a espera pela volta do portal da ANTAQ).

Já feito: repositório público com release v1.0, README com vídeo/PDF/capturas, portfólio com o card publicado (PR #1 do `gorc-supply.github.io`, já no ar). Todos os lugares que vão receber o link público estão marcados com `LINK_PUBLICO` em comentários (invisíveis para o visitante).

---

## 1. Publicar o painel no Power BI Service — 15–20 min

Passo a passo completo em [PUBLICAR.md](PUBLICAR.md). Resumo:

1. Abra `C:\projetos\raio-x-portuario\powerbi\RaioXPortuario.pbip` (você já está logado com o e-mail da UPE). Se aparecer a faixa amarela, **Atualizar agora**.
2. Confira: Visão Geral, Ano = 2025, cartão Toneladas = **1.403,8 Mi t**.
3. **Página Inicial > Publicar > Meu workspace**.
4. No navegador: **Arquivo > Inserir relatório > Publicar na Web (público) > Criar código de inserção > Publicar**. Guarde o link `https://app.powerbi.com/view?r=...`.
5. Se aparecer "Contate o administrador": seção 3 do PUBLICAR.md (pedir à TI da UPE, usar conta própria de administrador ou ficar sem link — o projeto já se sustenta com vídeo e PDF).

## 2. Conferir o link público numa janela anônima — 5 min

1. Abra o link numa janela anônima (sem login).
2. Passe pelas 5 páginas: o **mapa** é uma imagem + dispersão (não usa Azure Maps), então deve aparecer igual ao Desktop. Confira que Suape aparece em dourado e que os rótulos não se sobrepõem.
3. Teste a segmentação **Região = Nordeste** e os botões de navegação (no link público, clique simples, sem Ctrl).
4. Se algo vier diferente do Desktop, anote a página e o visual e veja a seção "Riscos" do relatório final.

## 3. Colocar o link no README — 5 min

1. Em `README.md`, procure `LINK_PUBLICO` (2 comentários) e troque cada um por `**[Abrir o painel ao vivo ↗](SEU_LINK)**`.
2. `git add README.md; git commit -m "Link público do painel"; git push`

## 4. Colocar o link no portfólio — 10 min

1. `cd C:\projetos\_tmp\portfolio; git pull`
2. No `index.html`, procure `LINK_PUBLICO` (5 ocorrências: card em PT, traduções EN e ES, e o objeto `rpp` do modal). Em cada uma, tire o comentário (`<!-- ... -->` no HTML, `/* ... */` no JS) e troque `LINK_PUBLICO` pelo seu link.
3. Abra o `index.html` no navegador e confira o botão "Ver painel ao vivo" nas 3 línguas.
4. `git add index.html; git commit -m "Raio-X Portuário: link do painel ao vivo"; git push`. O GitHub Pages atualiza em ~1 min.

## 5. Postar no LinkedIn — 10 min

1. Rascunho em [post_linkedin.md](post_linkedin.md). Releia no seu tom.
2. Anexe o vídeo `docs/video/raio-x-portuario.mp4` (78 s, 2,7 MB).
3. Se publicou o painel, troque o comentário `<!-- quando publicar ... -->` por "Painel ao vivo: SEU_LINK".

## 6. (Opcional) Trocar o mapa para Azure Maps — 10 min

Só se preferir o visual do Azure Maps e a sua conta permitir. PUBLICAR.md, seção 5: `gerar_pbip.py --mapa azure --sem-plano-b`, abrir, atualizar, **Publicar > Substituir** (o link público continua o mesmo). Antes, confira o mapa numa janela anônima: o Azure Maps pode ficar em branco no link público se o administrador bloquear.

## 7. Quando o portal da ANTAQ voltar: trocar para a fonte oficial — 30 min

Os dados vêm de um espelho público fixado no Hugging Face (ver [DECISOES.md](DECISOES.md), D02); o total bate com o oficial com diferença de −0,13% a +1,16% ao ano.

1. Encontre a página "Base de Dados" do Estatístico Aquaviário a partir de `https://www.gov.br/antaq/pt-br/assuntos/estatistica` (o endereço antigo era `https://web3.antaq.gov.br/ea/sense/download.html`).
2. Baixe, para **cada ano de 2021 a 2025**, os arquivos de **Atracação, Carga, Tempos de Atracação e Tempos de Atracação Paralisação** (o zip "todas as tabelas do ano" também serve; o pipeline procura `{ano}Atracacao.txt`, `{ano}Carga.txt`, `{ano}TemposAtracacao.txt` e `{ano}TemposAtracacaoParalisacao.txt` dentro de qualquer `.zip`), mais o dicionário de dados e a tabela auxiliar **Mercadoria**.
3. Coloque os `.zip` em `data\raw\antaq_oficial\` e rode `.venv\Scripts\python etl\run_all.py`.
4. **Confira o layout do TXT oficial:** o leitor assume `;`, cabeçalho na 1ª linha, vírgula decimal e datas `dd/mm/aaaa hh:mm:ss`. Isso não pôde ser testado com arquivo real; se a conciliação ou algum teste falhar, o ajuste fica em `_sql_txt_oficial()` de `etl/02_transform.py`.
5. Para incluir 2026 quando o ano fechar: `ANO_FINAL` em `etl/config.py` e o `Fim` do calendário em `etl/pbip_modelo.py`; depois regenerar o PBIP, as capturas e o vídeo (`ferramentas/sessao_final.py` e `ferramentas/entregaveis.py`).
