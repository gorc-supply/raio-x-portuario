## Raio-X Portuário no portfólio

Adiciona o card do novo projeto **Raio-X Portuário** (painel Power BI sobre os portos brasileiros com foco em Suape), no mesmo padrão dos cards existentes:

- card na grade de Projetos (coluna lateral), com título, descrição, selo "Em publicação" e botões *Ver detalhes*, *Ver código* e *Abrir painel*;
- traduções EN/ES das chaves `rpph`, `rppd`, `rppa`;
- entrada `rpp` do modal de detalhes (pergunta, 5 destaques com números conferidos, stack e links);
- subtítulo da seção Projetos e `og:description` atualizados para mencionar o painel;
- imagem provisória `img/raio-x-portuario-t.svg`.

### Antes do merge (placeholders)

- [ ] Trocar as 5 ocorrências de `LINK_PUBLICO` pelo link do "Publicar na Web".
- [ ] Gravar o vídeo (roteiro em `raio-x-portuario/docs/roteiro_video.md`) e adicionar `video/raio-x-portuario-tour.mp4` (< 10 MB) e o pôster `img/raio-x-portuario-t.webp`.
- [ ] No card, trocar o `<img>` provisório pelo `<video>` (o comentário TODO no HTML tem a tag pronta) e, no objeto `rpp`, apontar o pôster para o `.webp`.
- [ ] Trocar o selo "Em publicação" por "No ar" (`<span class="pill">`) nas 3 línguas.
- [ ] Conferir o card em PT/EN/ES, no desktop e no celular.

Código do projeto: https://github.com/gorc-supply/raio-x-portuario

🤖 Generated with [Claude Code](https://claude.com/claude-code)
