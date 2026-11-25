"""Automação do Power BI Desktop para o ciclo de verificação visual (capturas de tela).

Regras de segurança: este módulo só abre/fecha o Desktop, navega entre páginas, atualiza dados, ajusta o zoom,
recolhe painéis e salva (Ctrl+S). Nunca clica em Publicar, Entrar, Sair ou Compartilhar — qualquer controle
com esses nomes é bloqueado em `clicar()`.
"""
from __future__ import annotations

import ctypes
import subprocess
import sys
import time
from pathlib import Path

ctypes.windll.shcore.SetProcessDpiAwareness(2)

import mss  # noqa: E402
import mss.tools  # noqa: E402
import pyautogui  # noqa: E402
from pywinauto import Desktop  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PBIP = RAIZ / "powerbi" / "RaioXPortuario.pbip"
PROIBIDOS = ("publicar", "publish", "entrar", "sign in", "sair", "sign out", "compartilhar", "share")
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


def fechar() -> None:
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process PBIDesktop -ErrorAction SilentlyContinue | Stop-Process -Force"], check=False)
    time.sleep(3)


def abrir() -> None:
    fechar()
    subprocess.run(["powershell", "-NoProfile", "-Command", f'Start-Process -FilePath "{PBIP}"'], check=True)


def janela(timeout: int = 240):
    fim = time.time() + timeout
    while time.time() < fim:
        for w in Desktop(backend="uia").windows():
            t = w.window_text()
            if t.startswith("RaioXPortuario"):
                return w
        time.sleep(2)
    raise TimeoutError("janela do Power BI Desktop não apareceu")


def no_monitor2(w) -> None:
    """Move a janela para o monitor secundário (1920x1080, à direita do principal) e maximiza."""
    u32 = ctypes.windll.user32
    hwnd = w.handle
    u32.ShowWindow(hwnd, 9)          # SW_RESTORE
    time.sleep(1)
    u32.MoveWindow(hwnd, 1920 + 50, 50, 1600, 900, True)
    time.sleep(1)
    u32.ShowWindow(hwnd, 3)          # SW_MAXIMIZE
    time.sleep(2)


def capturar(caminho: Path, regiao: dict | None = None) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with mss.MSS() as m:
        area = regiao or m.monitors[2]
        img = m.grab(area)
        mss.tools.to_png(img.rgb, img.size, output=str(caminho))
    return caminho


def achar(w, nome: str, tipo: str | None = None, exato: bool = True):
    criterios = {"title": nome} if exato else {"title_re": f".*{nome}.*"}
    if tipo:
        criterios["control_type"] = tipo
    return w.child_window(**criterios)


def clicar(ctrl) -> None:
    nome = (ctrl.window_text() or "").lower()
    if any(p in nome for p in PROIBIDOS):
        raise RuntimeError(f"clique bloqueado por segurança: {nome!r}")
    r = ctrl.rectangle()
    pyautogui.moveTo((r.left + r.right) // 2, (r.top + r.bottom) // 2, duration=0.3)
    pyautogui.click()


def listar(w, profundidade: int = 4, filtro: str = "") -> None:
    def rec(c, d):
        if d > profundidade:
            return
        for f in c.children():
            try:
                t = f.window_text()
                info = f.element_info
                linha = f"{'  ' * d}{info.control_type} | {t!r} | {info.automation_id!r} | {f.rectangle()}"
                if not filtro or filtro.lower() in linha.lower():
                    print(linha)
            except Exception:  # noqa: BLE001
                continue
            rec(f, d + 1)
    rec(w, 0)


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "listar"
    if acao == "abrir":
        abrir()
        w = janela()
        no_monitor2(w)
        print("aberto:", w.window_text())
    elif acao == "listar":
        listar(janela(10), int(sys.argv[2]) if len(sys.argv) > 2 else 3, sys.argv[3] if len(sys.argv) > 3 else "")
    elif acao == "capturar":
        print(capturar(Path(sys.argv[2])))
    elif acao == "fechar":
        fechar()


# ---------------------------------------------------------------------------
# Ações no Desktop (localizadas por nome na árvore de UI Automation)
# ---------------------------------------------------------------------------
def _buscar(w, titulo: str, tipo: str, auto_id: str | None = None, tentativas: int = 3):
    for _ in range(tentativas):
        for c in w.descendants(control_type=tipo):
            try:
                if c.window_text() == titulo and (auto_id is None or c.element_info.automation_id == auto_id):
                    r = c.rectangle()
                    if r.width() > 0 and r.height() > 0:
                        return c
            except Exception:  # noqa: BLE001
                continue
        time.sleep(2)
    return None


def ir_pagina(w, nome: str) -> None:
    c = _buscar(w, nome, "TabItem")
    if c is None:
        raise LookupError(f"aba de página não encontrada: {nome}")
    clicar(c)
    time.sleep(4)


def recolher_paineis(w) -> None:
    for nome in ("Visualizações", "Dados", "Filtros"):
        c = _buscar(w, nome, "Button", tentativas=1)
        if c is not None:
            clicar(c)
            time.sleep(1.5)


def ajustar_pagina(w) -> None:
    c = _buscar(w, "Ajustar à página", "Button", tentativas=2)
    if c is not None:
        clicar(c)
        time.sleep(1.5)


def _dialogo_atualizacao_aberto(w) -> bool:
    for c in w.descendants(control_type="Window"):
        try:
            t = c.window_text()
        except Exception:  # noqa: BLE001
            continue
        if t in ("Atualizar", "Carregar", "Refresh", "Load"):
            return True
    return False


def atualizar(w, espera_max: int = 600) -> None:
    """Clica em 'Atualizar agora' (faixa amarela) ou no botão Atualizar da faixa de opções e espera terminar."""
    c = _buscar(w, "Atualizar agora", "Button", tentativas=1) or _buscar(w, "Atualizar", "Button")
    if c is None:
        raise LookupError("botão Atualizar não encontrado")
    clicar(c)
    time.sleep(15)
    fim = time.time() + espera_max
    livres = 0
    while time.time() < fim and livres < 3:
        livres = 0 if _dialogo_atualizacao_aberto(w) else livres + 1
        time.sleep(5)
    time.sleep(5)


def ir_pagina_parcial(w, trecho: str) -> None:
    for c in w.descendants(control_type="TabItem"):
        try:
            if trecho in c.window_text():
                clicar(c)
                time.sleep(4)
                return
        except Exception:  # noqa: BLE001
            continue
    raise LookupError(f"aba de página não encontrada: {trecho}")
