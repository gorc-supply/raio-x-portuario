# Registro de decisões autônomas

Cada decisão: **contexto → decisão → alternativas → motivo**. Ordem cronológica.

## D01 — Python do projeto
- **Contexto:** o `python` do PATH é só o atalho da Microsoft Store (não instalado). Existe Python 3.12 gerenciado pelo `uv`.
- **Decisão:** `.venv` criado com `uv venv --python 3.12`; dependências instaladas só dentro do `.venv`.
- **Alternativas:** instalar Python pela Store/winget (instalação fora do projeto).
- **Motivo:** nada instalado fora do projeto; 3.12 tem wheels prontas para todas as dependências.
