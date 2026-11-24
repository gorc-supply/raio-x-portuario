# Pendências para o Gabriel

Em ordem de execução. Tempo total estimado: **~4 h** (sem contar a espera pela volta do portal da ANTAQ).

---

## 1. Abrir o PBIP no Power BI Desktop e atualizar os dados — 15 min

Passo a passo em [PUBLICAR.md](PUBLICAR.md), seções 1 e 2. Resumo:

1. `powerbi\RaioXPortuario.pbip` > abrir. Se pedir, ativar as opções de PBIP/TMDL/PBIR em Recursos de visualização.
2. Conferir o parâmetro **CaminhoDados** (`C:\projetos\raio-x-portuario\data\processed\`) e clicar em **Atualizar**.
3. Conferir os cartões de 2025 contra [valores_referencia.md](valores_referencia.md).

> Nada disso pôde ser testado sem abrir o Desktop. Os 86 JSON passaram na validação contra os schemas oficiais, todas as 126 referências de campo/medida existem no modelo, e o DAX foi conferido por script (referências) e por leitura — mas sintaxe DAX e M só o Desktop confirma.

## 2. Revisar os visuais gerados por código — 30–40 min

Todos os visuais foram gerados (nenhum espaço vazio). Verifique cada item; se algum não renderizar, apague o `visual.json` correspondente e monte à mão como descrito.

| Página | Visual (pasta em `definition/pages/<página>/visuals/`) | O que conferir | Se precisar montar à mão |
|---|---|---|---|
| Todas | `nav_*` (botões) | Clique navega para a página; botão da página atual em dourado | Inserir > Botão > Em branco; Ação = Navegação de página; texto da página; preenchimento `#1D2127` (atual `#C9A96E`), x=432+166·i, y=12, 160×34 |
| Todas | `seg_ano`, `seg_regiao` | Começa em 2025; **Exibir > Sincronizar segmentações**: as duas marcadas em todas as páginas | Segmentação suspensa de `dCalendario[Ano]` (x16, y58, 150×46) e `dInstalacao[Regiao]` (x174, y58, 190×46), grupo de sincronização "Ano"/"Regiao" |
| Visão Geral | `mapa_bolhas` (Azure Maps) | Bolhas nos municípios certos (Santos, Ipojuca, São Luís…) | Se o mapa ficar vazio ou com bolhas fora do lugar: remover `LocalMapa` e arrastar `dInstalacao[Latitude]` e `[Longitude]` para os campos Latitude/Longitude, `[Toneladas]` em Tamanho. Se o Azure Maps estiver bloqueado na sua conta: trocar por barras de `[Toneladas]` por `dInstalacao[UF]` (x952, y234, 312×478) e registrar a troca |
| Visão Geral | `top10_instalacoes` | 10 barras, Suape em dourado se aparecer | Barras clusterizadas: eixo `dInstalacao[Instalacao]`, valor `[Toneladas (Top 10)]`, cor por valor de campo `[Cor Destaque Suape]` |
| Visão Geral | `linha_mensal` | Duas linhas (azul = ano, cinza = ano anterior), eixo jan–dez | Linha: eixo `dCalendario[AnoMes]`, valores `[Toneladas]` e `[Toneladas AA]` |
| Nordeste & Suape | `tabela_benchmark` | Espera mediana com fundo verde/vermelho; nome "Suape" em dourado | Tabela: `PortoBenchmarkNE`, `[Toneladas]`, `[Var % Toneladas AA]`, `[Espera Mediana (h)]`, `[Prancha Média Operacional (t/h)]`, `[% Contêiner]`, `[Ranking Porto]`; formatação condicional > Cor de fundo > Valor do campo `[Cor Benchmark Espera]`; cor da fonte de `PortoBenchmarkNE` > `[Cor Texto Suape]` |
| Nordeste & Suape | `barras_crescimento` | Barras por porto, Suape em dourado | `PortoBenchmarkNE` x `[Var % Toneladas AA]`, cor `[Cor Destaque Suape]` |
| Nordeste & Suape | `linha_suape_pares` | Linha dourada (Suape) x cinza (média dos pares) | Linha: `dCalendario[AnoMes]`, `[Espera Mediana Suape (h)]`, `[Espera Mediana Média Pares (h)]` |
| Eficiência | `dispersao_espera_prancha` | 32 portos públicos com dado em 2025; Suape em dourado; tamanho = toneladas | Dispersão: Valores `dInstalacao[Instalacao]`, X `[Espera Mediana (h)]`, Y `[Prancha Média Operacional (t/h)]`, Tamanho `[Toneladas]`; filtro do visual `TipoInstalacao = Porto Organizado` |
| Eficiência | `mapa_calor_espera` | Matriz porto x mês com cores (verde = até 2 h … vinho = acima de 72 h) | Matriz: linhas `PortoBenchmarkNE`, colunas `dCalendario[MesAbrev]`, valor `[Espera Mediana (h)]`; cor de fundo por valor de campo `[Cor Calor Espera]`; filtro `GrupoBenchmark` = Suape, Pares do Nordeste |
| Eficiência | `barras_pct_operacao`, `barras_paralisacao` | Barras com rótulos; títulos dinâmicos | `PortoBenchmarkNE` x `[% Atracado em Operação]`; `fParalisacao[MotivoParalisacao]` x `[Horas Paralisadas (Top 10 motivos)]` |
| Perfil de Carga | `empilhado_natureza`, `top_mercadorias`, `barras_navegacao`, `rosca_sentido`, `seg_porto` | Segmentação de porto filtra os 4 visuais | Colunas empilhadas `AnoMes` x `[Toneladas]` com legenda `NaturezaCarga`; barras `dMercadoria[Mercadoria]` x `[Toneladas (Top 10 mercadorias)]`; barras `Navegacao` x `[Toneladas]`; rosca `dSentido[Sentido]` x `[Toneladas]` (3 fatias) |
| Sobre | `texto_sobre_esq`, `texto_sobre_dir` | Links clicáveis (gov.br/antaq, GitHub, portfólio, LinkedIn) | Caixas de texto com o conteúdo do `visual.json` |
| Todas | Títulos dinâmicos | Títulos com conclusão (ex.: "Suape opera com espera mediana 22,1 h menor…") | Formatar > Título > fx > Valor do campo > medida `Título …` |
| Todas | Tema | Fundo preto, cartões `#0C0D10`, texto legível | Exibir > Temas > Procurar temas > `powerbi\tema-raio-x.json` |

Depois de revisar: **Arquivo > Salvar** e commit (`git add powerbi && git commit -m "Ajustes do relatório no Desktop"`).

## 3. Criar o repositório no GitHub e fazer o push — 10 min

O `gh` não está instalado nesta máquina (e o conector do GitHub não autenticou), então nada foi enviado. Tudo está commitado localmente na branch `main`.

```powershell
winget install --id GitHub.cli          # se ainda não tiver o gh
gh auth login                           # escolha GitHub.com > HTTPS > navegador
cd C:\projetos\raio-x-portuario

# conferência antes do push: nada de data/raw, cache.abf ou arquivo > 50 MB
git ls-files | Select-String "data/raw|cache.abf|localSettings.json"      # deve vir vazio
git ls-files | ForEach-Object { Get-Item $_ } | Where-Object Length -gt 50MB  # deve vir vazio

gh repo create gorc-supply/raio-x-portuario --public --source . --remote origin --push `
  --description "Painel Power BI sobre o desempenho dos portos brasileiros com foco em Suape e no Nordeste, com dados abertos da ANTAQ"
gh repo edit gorc-supply/raio-x-portuario --add-topic power-bi --add-topic supply-chain --add-topic logistica `
  --add-topic dados-abertos --add-topic antaq --add-topic dax --add-topic python --homepage "https://gorc-supply.github.io"
```

## 4. Publicar o painel na web — 20 min

[PUBLICAR.md](PUBLICAR.md), seções 4 e 5 (e o Plano B, se "Publicar na Web" não aparecer). Guarde o link e o iframe.

## 5. Gravar o vídeo e a capa — 45 min

1. Roteiro cena a cena em [roteiro_video.md](roteiro_video.md) (~80 s). Salvar `raio-x-portuario-tour.mp4` (< 10 MB) e o pôster `raio-x-portuario-t.webp`.
2. Capa do README: GIF curto (5–8 s, página Visão Geral) ou print, em `docs/img/capa.gif`; no README, trocar `docs/img/capa-placeholder.svg` por `docs/img/capa.gif`.

## 6. Atualizar o README — 5 min

Trocar `LINK_PUBLICO` e `LINK_VIDEO` no `README.md`; commit e push.

## 7. Abrir o Pull Request do portfólio (sem merge) — 15 min

O card já está pronto e commitado na branch `raio-x-portuario` do clone `C:\projetos\_tmp\portfolio` (commit `297c06f`), mas **sem push** (sem gh). O texto do PR está em [pr_portfolio.md](pr_portfolio.md).

```powershell
cd C:\projetos\_tmp\portfolio
# trocar LINK_PUBLICO (5 ocorrências) no index.html; copiar o vídeo para video\ e o pôster para img\;
# trocar o <img> provisório pelo <video> (tag pronta no comentário TODO do card)
git add index.html img video
git commit -m "Raio-X Portuário: link público e vídeo"
git push -u origin raio-x-portuario
gh pr create --repo gorc-supply/gorc-supply.github.io --base main --head raio-x-portuario `
  --title "Adiciona o projeto Raio-X Portuário (Power BI)" `
  --body-file C:\projetos\raio-x-portuario\docs\pr_portfolio.md
```

Revise o card em PT/EN/ES e no celular antes de fazer o merge (o merge é seu).

## 8. Postar no LinkedIn — 10 min

Rascunho em [post_linkedin.md](post_linkedin.md): trocar `LINK_PUBLICO`, anexar o vídeo, reler no seu tom.

## 9. Quando o portal da ANTAQ voltar: trocar a fonte para a oficial — 30 min

O download oficial está fora do ar (ver [DECISOES.md](DECISOES.md), D02); os dados vieram de um espelho público. Para fechar o ciclo com a fonte oficial:

1. Encontrar a página "Base de Dados" do Estatístico Aquaviário. O endereço antigo era `https://web3.antaq.gov.br/ea/sense/download.html`; procure o novo a partir de `https://www.gov.br/antaq/pt-br/assuntos/estatistica`.
2. Baixar, para **cada ano de 2021 a 2026**, os arquivos anuais de **Atracação, Carga, Tempos de Atracação e Tempos de Atracação Paralisação** (o arquivo "todas as tabelas do ano" também serve: o pipeline procura `{ano}Atracacao.txt`, `{ano}Carga.txt`, `{ano}TemposAtracacao.txt` e `{ano}TemposAtracacaoParalisacao.txt` dentro de qualquer `.zip`).
3. Baixar também o **dicionário de dados** e a tabela auxiliar **Mercadoria** (para substituir a nomenclatura SH em `dMercadoria`, ver D08).
4. Colocar os `.zip` em `C:\projetos\raio-x-portuario\data\raw\antaq_oficial\` e rodar `.venv\Scripts\python etl\run_all.py`. O `docs/data_quality.md` passa a mostrar "ANTAQ oficial" na origem.
5. **Conferir o layout do TXT oficial** — o leitor assume separador `;`, cabeçalho na 1ª linha, vírgula decimal e datas `dd/mm/aaaa hh:mm:ss`, detectando UTF-8/Latin-1; isso não pôde ser testado com um arquivo real. Se a conciliação ou algum teste falhar, o ajuste fica em `_sql_txt_oficial()` de `etl/02_transform.py`.
6. Com dados mais recentes que jan/2026, ajustar `ANO_FINAL` em `etl/config.py` e o `Fim` do calendário em `etl/pbip_modelo.py` se passar de 2026.
