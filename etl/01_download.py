"""Etapa 1 — aquisição dos dados brutos.

Ordem de preferência (ver docs/DECISOES.md, D02):
  1. Zips OFICIAIS da ANTAQ colocados à mão em data/raw/antaq_oficial/
     (ex.: 2024Atracacao.zip, 2024Carga.zip ou 2024.zip com os .txt dentro).
  2. Zips OFICIAIS descobertos automaticamente na página de download da ANTAQ
     (os links são lidos do HTML da página; nenhuma URL de arquivo é presumida).
  3. Contingência: espelho público (Hugging Face, CC-BY-4.0, revisão fixada) com os
     mesmos arquivos oficiais convertidos para Parquet.

Também baixa a tabela oficial de nomenclatura SH do Comex Stat (MDIC).

Idempotente: não baixa de novo o que já existe com o mesmo hash; tenta de novo em
caso de falha; registra cada arquivo em data/raw/download.log e no manifesto JSON.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

UA = "raio-x-portuario/1.0 (projeto de portfolio; dados abertos)"
TENTATIVAS = 4
TIMEOUT = 120

log = logging.getLogger("download")


def configurar_log() -> None:
    C.RAW_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    for h in (logging.FileHandler(C.DOWNLOAD_LOG, encoding="utf-8"), logging.StreamHandler(sys.stdout)):
        h.setFormatter(fmt)
        log.addHandler(h)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def carregar_manifesto() -> dict:
    if C.MANIFEST_FILE.exists():
        return json.loads(C.MANIFEST_FILE.read_text(encoding="utf-8"))
    return {"arquivos": {}}


def salvar_manifesto(man: dict) -> None:
    man["atualizado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    C.MANIFEST_FILE.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")


def baixar(url: str, destino: Path, man: dict, fonte: str) -> bool:
    """Baixa url -> destino com retentativas. Retorna True se o arquivo está disponível."""
    chave = destino.relative_to(C.RAW_DIR).as_posix()
    reg = man["arquivos"].get(chave)
    if destino.exists() and reg and reg.get("sha256") == sha256(destino):
        log.info("JA EXISTE  %s (%s bytes) — não baixado de novo", chave, destino.stat().st_size)
        return True

    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            with requests.get(url, headers={"User-Agent": UA}, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()
                with tmp.open("wb") as f:
                    for bloco in r.iter_content(1 << 20):
                        f.write(bloco)
            tmp.replace(destino)
            man["arquivos"][chave] = {
                "fonte": fonte,
                "url": url,
                "bytes": destino.stat().st_size,
                "sha256": sha256(destino),
                "baixado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            salvar_manifesto(man)
            log.info("BAIXADO    %s (%s bytes) <- %s", chave, destino.stat().st_size, url)
            return True
        except Exception as exc:  # noqa: BLE001 — queremos registrar qualquer falha
            espera = 5 * tentativa
            log.warning("FALHA %d/%d %s: %s — nova tentativa em %ss", tentativa, TENTATIVAS, url, exc, espera)
            tmp.unlink(missing_ok=True)
            if tentativa < TENTATIVAS:
                time.sleep(espera)
    log.error("DESISTIU   %s", url)
    return False


# ---------------------------------------------------------------------------
# 1 e 2: fonte oficial
# ---------------------------------------------------------------------------
def zips_oficiais_locais() -> dict[tuple[int, str], Path]:
    """Mapeia (ano, tabela) -> zip oficial colocado à mão em data/raw/antaq_oficial/."""
    achados: dict[tuple[int, str], Path] = {}
    if not C.RAW_OFICIAL_DIR.exists():
        return achados
    import zipfile

    for z in sorted(C.RAW_OFICIAL_DIR.glob("*.zip")):
        try:
            nomes = zipfile.ZipFile(z).namelist()
        except zipfile.BadZipFile:
            log.warning("ZIP INVALIDO %s — ignorado", z.name)
            continue
        for nome in nomes:
            m = re.match(r"^(\d{4})(Atracacao|Carga|TemposAtracacao|TemposAtracacaoParalisacao)\.txt$",
                         Path(nome).name)
            if m and int(m.group(1)) in C.ANOS:
                achados[(int(m.group(1)), m.group(2))] = z
    return achados


def descobrir_links_oficiais() -> list[str]:
    """Lê a página oficial de download e devolve os links .zip encontrados no HTML."""
    try:
        r = requests.get(C.ANTAQ_PAGINA_DOWNLOAD, headers={"User-Agent": UA}, timeout=60)
    except Exception as exc:  # noqa: BLE001
        log.warning("PAGINA OFICIAL inacessível (%s): %s", C.ANTAQ_PAGINA_DOWNLOAD, exc)
        return []
    if r.status_code != 200 or "zip" not in r.text.lower():
        log.warning("PAGINA OFICIAL respondeu HTTP %s sem links .zip (url final: %s)", r.status_code, r.url)
        return []
    links = sorted({urljoin(r.url, h) for h in re.findall(r"""["']([^"']+?\.zip)["']""", r.text, re.I)})
    log.info("PAGINA OFICIAL: %d links .zip encontrados", len(links))
    return links


def baixar_oficiais(man: dict) -> None:
    for link in descobrir_links_oficiais():
        nome = Path(link).name
        m = re.match(r"^(\d{4})(Atracacao|Carga|TemposAtracacao|TemposAtracacaoParalisacao)?\.zip$", nome)
        if m and int(m.group(1)) in C.ANOS and (m.group(2) is None or m.group(2) in C.TABELAS):
            baixar(link, C.RAW_OFICIAL_DIR / nome, man, "ANTAQ (oficial)")


# ---------------------------------------------------------------------------
# 3: espelho de contingência
# ---------------------------------------------------------------------------
def baixar_espelho(man: dict, faltando: list[tuple[int, str]]) -> list[tuple[int, str]]:
    falhas = []
    for ano, tabela in faltando:
        url = C.ESPELHO_URL.format(repo=C.ESPELHO_REPO, rev=C.ESPELHO_REVISAO, tabela=tabela, ano=ano)
        destino = C.RAW_ESPELHO_DIR / tabela / f"{ano}.parquet"
        if not baixar(url, destino, man, f"Espelho HF {C.ESPELHO_REPO}@{C.ESPELHO_REVISAO[:7]}"):
            falhas.append((ano, tabela))
    return falhas


def main() -> int:
    configurar_log()
    log.info("=== Início do download (recorte %s-%s) ===", C.ANO_INICIAL, C.ANO_FINAL)
    man = carregar_manifesto()

    baixar_oficiais(man)
    oficiais = zips_oficiais_locais()
    for (ano, tab), z in sorted(oficiais.items()):
        log.info("OFICIAL    %s %s <- %s", ano, tab, z.name)

    faltando = [(a, t) for a in C.ANOS for t in C.TABELAS if (a, t) not in oficiais]
    if faltando:
        log.warning("Fonte oficial indisponível para %d combinações ano x tabela; usando espelho de contingência",
                    len(faltando))
    falhas = baixar_espelho(man, faltando)

    ok_sh = baixar(C.COMEXSTAT_SH_URL, C.RAW_SH_FILE, man, "Comex Stat / MDIC (oficial)")

    if falhas:
        log.error("Sem dados para: %s", ", ".join(f"{a}/{t}" for a, t in falhas))
    log.info("=== Fim do download: %d oficiais, %d via espelho, %d falhas, tabela SH=%s ===",
             len(oficiais), len(faltando) - len(falhas), len(falhas), "ok" if ok_sh else "FALHOU")
    return 1 if (falhas or not ok_sh) else 0


if __name__ == "__main__":
    sys.exit(main())
