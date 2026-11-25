# Publicar o painel (passo a passo para o Gabriel)

Tempo: **15 a 20 min**. Você já está logado no Power BI Desktop com o e-mail da UPE.

## 1. Abrir e conferir (3 min)

1. Abra `C:\projetos\raio-x-portuario\powerbi\RaioXPortuario.pbip`.
2. Se aparecer a faixa amarela "Algumas tabelas estão incompletas…", clique em **Atualizar agora** e espere terminar (~1 min).
3. Confira na Visão Geral: Ano = **2025**, Região = **Todos**, cartão Toneladas = **1.403,8 Mi t**.

## 2. Publicar em "Meu workspace" (3 min)

1. **Página Inicial > Publicar**.
2. Se perguntar se quer salvar, clique em **Salvar**.
3. Escolha **Meu workspace** > **Selecionar**. Espere a mensagem **"Êxito!"** e clique em **Abrir "RaioXPortuario.pbip" no Power BI**.

## 3. Publicar na Web (3 min)

1. No navegador (app.powerbi.com), com o relatório aberto: **Arquivo > Inserir relatório > Publicar na Web (público)**.
2. Clique em **Criar código de inserção** e depois em **Publicar**.
3. Copie o **link** (`https://app.powerbi.com/view?r=...`) e o **HTML do iframe**. Guarde os dois.
4. Abra o link numa janela anônima e confira as 5 páginas e o mapa (o mapa é próprio, não depende de login).

### Se aparecer "Contate o administrador" / a opção não existir

A UPE desligou o "Publicar na Web" para a sua conta. Três saídas, nesta ordem:

1. Peça ao suporte de TI da UPE para habilitar **Configurações do locatário > Publicar na Web** para o seu usuário (o painel só tem dados públicos da ANTAQ).
2. Ou use uma conta Microsoft 365 em que você seja o administrador (ex.: programa de desenvolvedor do Microsoft 365) e ative a opção no **Portal de administração > Configurações do locatário > Publicar na Web**. Entre com essa conta no Desktop e repita a seção 2.
3. Ou fique sem link público: o README e o portfólio já mostram vídeo, PDF e capturas. Não precisa fazer mais nada.

## 4. Colocar o link no README e no portfólio (5 min)

1. No `README.md`, troque os dois comentários `<!-- LINK_PUBLICO ... -->` pela linha `**[Abrir o painel ao vivo ↗](SEU_LINK)**`.
2. No portfólio (`C:\projetos\_tmp\portfolio\index.html`, ou direto no GitHub): procure `LINK_PUBLICO` — há o botão "Ver painel ao vivo" comentado no card e nas traduções EN/ES. Tire o comentário e troque `LINK_PUBLICO` pelo seu link.
3. Commit e push nos dois repositórios:

```powershell
cd C:\projetos\raio-x-portuario
git add README.md; git commit -m "Link público do painel"; git push
cd C:\projetos\_tmp\portfolio
git pull; git add index.html; git commit -m "Raio-X Portuário: link do painel ao vivo"; git push
```

## 5. Trocar o mapa e republicar (só se quiser)

O mapa da Visão Geral é o **mapa próprio com a malha do IBGE** (venceu a comparação, ver `docs/DECISOES.md`, D22). Se preferir a versão com **Azure Maps** (opção 1, já ajustada; depende de a sua conta permitir Azure Maps):

1. Feche o Desktop e rode: `.venv\Scripts\python etl\gerar_pbip.py --mapa azure --sem-plano-b`
2. Abra o `.pbip`, clique em **Atualizar** e confira o mapa.
3. **Publicar > Meu workspace > Substituir**. O link do "Publicar na Web" **continua o mesmo**.

Para voltar: `.venv\Scripts\python etl\gerar_pbip.py --mapa dispersao --sem-plano-b` e repetir os passos 2 e 3.
