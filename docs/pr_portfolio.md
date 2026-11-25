## Raio-X Portuário no portfólio

Adiciona o projeto **Raio-X Portuário** (painel Power BI sobre os portos brasileiros com foco em Suape, dados abertos da ANTAQ de 2021 a 2025) e reorganiza a grade de Projetos.

### O que muda

- **Grade de Projetos:** a linha 1 volta ao desenho original (card grande do Supply OPME + 2 cards laterais), que estava desequilibrada com 3 cards na coluna lateral. O Raio-X Portuário ganha uma **linha 2 em card largo**, com o vídeo alinhado à coluna do card grande e o texto alinhado à coluna lateral. No celular, tudo vira uma coluna.
- **Card:** título, descrição curta, tags (Power BI, DAX, Python, DuckDB, Dados abertos), vídeo em loop com pôster (como os demais) e botões *Ver detalhes*, *GitHub* e *PDF*. O botão **"Ver painel ao vivo"** já está pronto, mas comentado com o marcador `LINK_PUBLICO` (no card, nas traduções EN/ES e no modal) até o painel ser publicado na web.
- **Modal de detalhes:** vídeo de 78 s + as 5 páginas do painel em miniatura (com ampliação), 5 destaques no recorte 2021–2025, stack e links.
- **Mídias:** `video/raio-x-portuario-tour.mp4` (2,7 MB, 1920×1080), pôster `img/raio-x-portuario-t.webp` e `img/rpp-*.webp` (miniatura 960 px + imagem cheia). Removida a imagem provisória `img/raio-x-portuario-t.svg`.
- **Modal (todos os projetos):** vídeo com `object-fit: contain`. Para os outros vídeos (16:10) não muda nada; o novo (16:9) deixa de ser cortado nas bordas.
- Traduções EN/ES do card e do modal; selo "Concluído" no padrão dos demais.

### Conferência

- Capturas com navegador sem interface em 1440 px e 390 px, em PT/EN/ES, do card e do modal: sem rolagem horizontal; vídeo e texto do card largo com a mesma altura (335 px) no desktop.
- Nenhum marcador visível para o visitante: os 5 `LINK_PUBLICO` estão em comentários HTML/JS.

### Depois de publicar o painel

Procurar `LINK_PUBLICO` no `index.html`, tirar o comentário e trocar pelo link do "Publicar na Web" (passo a passo em `raio-x-portuario/docs/PUBLICAR.md`, seção 4).

Código do projeto: https://github.com/gorc-supply/raio-x-portuario

🤖 Generated with [Claude Code](https://claude.com/claude-code)
