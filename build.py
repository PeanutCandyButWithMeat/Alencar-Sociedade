"""Maestro do site: carrega o conteúdo, gera as páginas e (opcionalmente) publica.

Uso:
    python build.py              # só gera o site em docs/
    python build.py --publicar   # gera, depois faz commit e push
"""
import argparse
import shutil

import config
from src.covers import gerar_og
from src.git_publish import publicar
from src.loader import carregar_materias
from src.publishers.bluesky import garantir_post, web_url
from src.render import render
from src.search_index import gerar_indice_busca
from src.sitemap import gerar_sitemap


def titulo_pagina(nome=None):
    return f"{nome} — {config.NOME_SITE}" if nome else config.NOME_SITE


def preparar_saida():
    shutil.rmtree(config.SAIDA, ignore_errors=True)
    shutil.copytree(config.STATIC, config.SAIDA)
    (config.SAIDA / "noticias").mkdir(exist_ok=True)


def gerar_paginas_fixas(materias):
    og_home = f"{config.SITE_URL}/img/og/home.jpg"  # criar à mão em static/img/og/home.jpg
    destaque = next((m for m in materias if m["destaque"]), materias[0] if materias else None)

    render("index.html", config.SAIDA / "index.html", title=titulo_pagina(), base_path="",
           destaque=destaque, materias=[m for m in materias if m is not destaque],
           og_image=og_home, og_url=f"{config.SITE_URL}/")
    render("sobre.html", config.SAIDA / "sobre.html", title=titulo_pagina("Sobre"), base_path="",
           og_image=og_home, og_url=f"{config.SITE_URL}/sobre.html")
    render("links.html", config.SAIDA / "links.html", title=titulo_pagina("Links"), base_path="",
           links=config.LINKS, og_image=og_home, og_url=f"{config.SITE_URL}/links.html")


def gerar_materia(m):
    url = f"{config.SITE_URL}/noticias/{m['slug']}.html"
    imagem = m.get("imagem") or gerar_og(m)

    # Bluesky: posta (se ainda não postou) usando a imagem da matéria como capa
    uri = garantir_post(slug=m["slug"], titulo=m["titulo"], descricao=m["resumo"],
                        url=url, capa_path=config.SAIDA / imagem)
    m["bluesky_uri"] = uri
    m["bluesky_web"] = web_url(uri) if uri else None

    render("article.html", config.SAIDA / "noticias" / f"{m['slug']}.html",
           **m, title=titulo_pagina(m["titulo"]), base_path="../",
           html_lang="en" if m["idioma"].upper() == "EN" else "pt-BR",
           og_image=f"{config.SITE_URL}/{imagem}", og_url=url)


def montar():
    preparar_saida()
    materias = carregar_materias()
    gerar_paginas_fixas(materias)
    for m in materias:
        gerar_materia(m)
    gerar_indice_busca(materias)
    gerar_sitemap(materias)
    print(f"Build concluído: {len(materias)} matéria(s) em {config.SAIDA}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--publicar", action="store_true", help="depois do build, faz commit e push")
    args = parser.parse_args()

    montar()
    if args.publicar:
        publicar()
