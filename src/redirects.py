"""Páginas-ponte nos endereços antigos, para não quebrar links já divulgados.

Dois casos:
  - config.REDIRECIONAR_ANTIGOS: matérias que circulavam em noticias/<slug>.html
  - "enderecos_antigos" no frontmatter: sempre que mover uma matéria (mudar de seção,
    categoria, idioma...), copie o caminho antigo para essa lista antes de mover.
"""
import posixpath

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
        antigos = list(m.get("enderecos_antigos") or [])
        if m["slug"] in config.REDIRECIONAR_ANTIGOS:
            antigos.append(f"noticias/{m['slug']}.html")

        for antigo in dict.fromkeys(antigos):  # sem repetidos, mantendo a ordem
            if antigo == m["caminho"]:
                continue  # nunca sobrescreve a própria matéria
            relativo = posixpath.relpath(m["caminho"], start=posixpath.dirname(antigo))
            destino = config.SAIDA / antigo
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(MODELO.format(canonico=f"{config.SITE_URL}/{m['caminho']}", relativo=relativo),
                               encoding="utf-8")
