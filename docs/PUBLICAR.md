# Como publicar o painel (passo a passo manual)

Tempo total estimado: **1h30 a 2h** na primeira vez.

## 1. Abrir o projeto (10 min)

1. Confirme que os CSV existem em `C:\projetos\raio-x-portuario\data\processed\` (se não, rode `.venv\Scripts\python etl\run_all.py`).
2. Abra `powerbi\RaioXPortuario.pbip` no Power BI Desktop.
   - Se o Desktop pedir, ative em **Arquivo > Opções > Recursos de visualização**: "Opção de salvamento do Projeto do Power BI (.pbip)", "Armazenar modelo semântico usando o formato TMDL" e "Armazenar relatórios usando o formato de metadados avançado (PBIR)". Feche e abra de novo.
   - Se aparecer aviso de "alterações não aplicadas", clique em **Aplicar**.
3. Se o projeto estiver em outra pasta: **Página Inicial > Transformar dados > Editar parâmetros > CaminhoDados** (termine com `\`).
4. **Página Inicial > Atualizar**. A carga leva 1–3 minutos (~400 mil atracações).
5. Se der erro de carga, anote a tabela e a mensagem e veja a seção "Se algo der errado" no fim.

## 2. Conferir os KPIs (20 min)

Abra [valores_referencia.md](valores_referencia.md) ao lado.

1. Página **Visão Geral Brasil**, Ano = 2025, Região em branco: os 5 cartões devem bater com a tabela "1. Brasil", coluna 2025 (Toneladas 1.403.813.213; Var. +5,9%; Atracações 94.118; Espera mediana 1,4 h; Prancha 765 t/h).
2. Troque o Ano para 2021, 2023 e 2026 e confira os mesmos cartões (2026 é parcial: só janeiro).
3. Página **Nordeste & Suape**, Ano = 2025: a tabela deve bater com "3. Benchmark Nordeste / 2025"; os cartões de Suape com a tabela "2. Suape".
4. Diferenças só na última casa decimal são arredondamento. Diferença maior = anote em `docs/PENDENCIAS.md`.

## 3. Revisar os visuais (20–40 min)

O relatório foi gerado por código e validado contra os schemas, mas a aparência final precisa de olho humano. Itens específicos estão em [PENDENCIAS.md](PENDENCIAS.md) (item 2). Em resumo: mapa (geocodificação), cores condicionais, botões de navegação, sincronização das segmentações (**Exibir > Sincronizar segmentações**) e legibilidade do tema escuro.

Depois: **Arquivo > Salvar** (salva no próprio PBIP).

## 4. Publicar no serviço (10 min)

1. **Página Inicial > Publicar > Meu workspace**. Entre com sua conta Microsoft se pedir.
2. Abra o link que o Desktop mostra (app.powerbi.com).
3. No serviço, abra o relatório e confira se as 5 páginas carregam e se o mapa aparece.

## 5. Publicar na Web (5 min)

1. No relatório aberto no serviço: **Arquivo > Inserir relatório > Publicar na Web (público)**.
2. Leia o aviso (qualquer pessoa com o link vê os dados — aqui são dados públicos da ANTAQ) e clique em **Criar código de inserção > Publicar**.
3. Copie os dois: o **link** (`https://app.powerbi.com/view?r=...`) e o **HTML do iframe**.
4. Na página do relatório, em **Configurações**, confirme que "Mostrar painel de filtros" está desligado para leitores.

## 6. Atualizar README e portfólio (15 min)

1. No `README.md` deste repositório: troque `LINK_PUBLICO` pelo link e `LINK_VIDEO` pelo link do vídeo (ou remova). Commit e push.
2. No clone do portfólio (`C:\projetos\_tmp\portfolio`, branch `raio-x-portuario`): troque as ocorrências de `LINK_PUBLICO` em `index.html` pelo link, adicione o vídeo e o pôster (ver PENDENCIAS), commit e push. O PR é atualizado sozinho.

## Plano B: "Publicar na Web" não aparece na sua conta

Acontece quando a conta é corporativa/escolar e o administrador desligou a opção, ou quando a conta não tem licença do Power BI.

1. **Tente primeiro** uma conta Microsoft 365 pessoal/de desenvolvedor em que você seja o administrador do tenant: no **Portal de administração > Configurações do locatário > Publicar na Web**, ative a opção.
2. Se não der: publique o projeto sem o link público.
   - Grave o vídeo (roteiro em [roteiro_video.md](roteiro_video.md)) com o relatório aberto no **Desktop**.
   - Exporte prints das 5 páginas (**Arquivo > Exportar > PDF**, ou captura de tela 1920×1080) para `docs/img/` e use 2–3 no README no lugar do link.
   - O PBIP já está no GitHub: quem quiser abre no próprio Desktop seguindo "Como reproduzir" no README.
   - No portfólio, troque o botão "Abrir painel ↗" (`LINK_PUBLICO`) pelo link do vídeo ou remova-o, e deixe "Ver código" apontando para o repositório.

## Se algo der errado ao abrir

| Sintoma | O que fazer |
|---|---|
| Erro citando um arquivo `.json` do relatório | Rode `.venv\Scripts\python etl\validar_pbip.py`; se passar, abra uma issue com a mensagem exata — provavelmente uma propriedade de visual que a sua versão do Desktop não aceita. Apague só aquele `visual.json` e monte o visual à mão (descrição em PENDENCIAS). |
| Erro de TMDL | A mensagem indica arquivo e linha em `powerbi\RaioXPortuario.SemanticModel\definition\`. |
| Erro de carga "arquivo não encontrado" | Parâmetro `CaminhoDados` errado ou CSV não gerado. |
| Tema não aplicado | **Exibir > Temas > Procurar temas** e escolha `powerbi\tema-raio-x.json`. |
| Mapa vazio | Ver PENDENCIAS, item do mapa. |
