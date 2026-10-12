"""Páginas-ponte nos endereços antigos (noticias/<slug>.html) para não quebrar links já divulgados."""
import config

MODELO = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Redirecionando…</title>
<link rel="canonical" href="{canonico}">
<meta http-equiv="refresh" content="0; url={relativo}">
</head><body><a href="{relativo}">Ir para a matéria</a></body></html>
"""


def gerar_redirecionamentos(materias):
    for m in materias:
        relativo = m["caminho"].removeprefix("noticias/")  # relativo à pasta noticias/
        antigo = config.SAIDA / "noticias" / f"{m['slug']}.html"
        antigo.parent.mkdir(parents=True, exist_ok=True)
        antigo.write_text(MODELO.format(canonico=f"{config.SITE_URL}/{m['caminho']}", relativo=relativo),
                          encoding="utf-8")
