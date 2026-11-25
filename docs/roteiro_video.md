# Roteiro do vídeo (gravação de tela, 78 s)

Vídeo final: [docs/video/raio-x-portuario.mp4](video/raio-x-portuario.mp4) (1920×1080, H.264, 30 fps, 2,7 MB) · pôster: [docs/video/poster.jpg](video/poster.jpg).

No estilo dos tours do portfólio: gravação de tela muda, legenda curta embutida no rodapé (faixa semitransparente), cortes secos, cursor visível e lento. Gravado no Power BI Desktop por `ferramentas/sessao_final.py` (navegação automatizada, recorte só na área do relatório, ano 2025) e editado por `ferramentas/entregaveis.py` (cartelas e legendas). Os tempos de cada cena ficam em `docs/video/cenas.json`. Todos os números estão em [valores_referencia.md](valores_referencia.md) (seção 4) ou em [conciliacao_antaq.md](conciliacao_antaq.md).

| # | Tempo | O que aparece | Ação | Achado em destaque | Legenda (texto na tela) |
|---|---|---|---|---|---|
| 1 | 0–2 s | Cartela de abertura | — | Título e recorte | "Raio-X Portuário · Dados abertos da ANTAQ, 2021–2025" |
| 2 | 2–6 s | Página **Visão Geral** inteira | Cursor parado | Página de entrada | "Visão Geral · ano de 2025" |
| 3 | 6–9 s | Cartões de KPI | Cursor passa pelos cartões | Recorde de 2025 | "1.403,8 milhões de t em 2025, 5,9% acima de 2024" |
| 4 | 9–14 s | Linha mensal | Passar o mouse em agosto (dica de ferramenta) | 2025 x 2024 mês a mês | "Mês a mês, 2025 fica acima de 2024 a partir de março" |
| 5 | 14–20 s | Mapa (malha do IBGE) | Passar o mouse na bolha de Suape (dica: UF, toneladas, var %, espera, prancha) | Suape no mapa | "Mapa com malha do IBGE: Suape em dourado" |
| 6 | 20–32 s | Segmentação **Região** | Abrir a lista, marcar "Nordeste", fechar | O painel inteiro passa a mostrar o Nordeste | "Filtro Região = Nordeste: 329,7 milhões de t" |
| 7 | 32–46 s | Página **Nordeste & Suape** | Ctrl+clique no botão; passar o mouse na linha de Suape da tabela e na linha mensal | Suape x pares | "Suape espera 4,3 h (mediana); a média dos pares, 26,4 h" |
| 8 | 46–57 s | Página **Eficiência e Gargalos** | Ctrl+clique; passar o mouse no mapa de calor | Fila em Itaqui | "Itaqui concentra a fila: 143,9 h de espera mediana" |
| 9 | 57–67 s | Página **Perfil de Carga** | Ctrl+clique; passar o mouse no top de mercadorias | O que cada porto movimenta | "Perfil de carga: o que cada porto movimenta" |
| 10 | 67–75 s | Página **Sobre** | Ctrl+clique | Método e conferência | "Total conferido com a ANTAQ: diferença máxima de 1,16% ao ano" |
| 11 | 75–78 s | Cartela de encerramento | — | Links | "github.com/gorc-supply/raio-x-portuario · gorc-supply.github.io" |

**Revisão:** um quadro a cada 5 s em `docs/video/quadros/` (conferidos: nenhum clique errado, lista suspensa fecha logo após a seleção, legendas legíveis).

**Para regravar** (depois de mudar o relatório): `.venv\Scripts\python ferramentas\sessao_final.py` e depois `.venv\Scripts\python ferramentas\entregaveis.py`. Não mexa no mouse durante a gravação (~6 min com a atualização dos dados).
