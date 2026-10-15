"""Páginas de listagem (seção, categoria, autor) e os dados do menu.

Como o site é estático, cada filtro vira uma página gerada no build:
    secao/<secao>.html                  todas as matérias da seção
    secao/<secao>/<categoria>.html      uma categoria dentro da seção
    autor/<autor>.html                  tudo de um autor (inclusive "só eu")
"""
import config
from src.loader import slugificar
from src.render import render


def montar_menu(materias):
    """Estrutura usada pelo header e pelo menu lateral (vira variável global dos templates)."""
    secoes = {s["slug"]: {"slug": s["slug"], "nome": s["nome"], "total": 0, "categorias": {}}
              for s in config.SECOES}
    autores = {}

    for m in materias:  # seções que aparecem só no frontmatter entram no fim
        s = secoes.setdefault(m["secao_slug"], {"slug": m["secao_slug"], "nome": m["secao"],
                                                "total": 0, "categorias": {}})
        s["total"] += 1
        c = s["categorias"].setdefault(m["categoria_slug"],
                                       {"slug": m["categoria_slug"], "nome": m["categoria"], "total": 0})
        c["total"] += 1
        a = autores.setdefault(m["autor_slug"], {"slug": m["autor_slug"], "nome": m["autor"], "total": 0})
        a["total"] += 1

    principal = slugificar(config.AUTOR_PADRAO)
    autores.setdefault(principal, {"slug": principal, "nome": config.AUTOR_PADRAO, "total": 0})
    ordem = sorted(autores.values(), key=lambda a: (a["slug"] != principal, a["nome"]))

    return {
        "secoes": [{**s, "categorias": sorted(s["categorias"].values(), key=lambda c: c["nome"])}
                   for s in secoes.values()],
        "autores": ordem,
        "autor_principal": autores[principal],
    }


def gerar_listagens(materias, menu):
    """Gera as páginas de listagem. Devolve os caminhos criados (para o sitemap)."""
    og = f"{config.SITE_URL}/img/og/home.jpg"
    criadas = []

    def pagina(caminho, titulo, lista, subtitulo="", profundidade=1):
        destino = config.SAIDA / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        render("listagem.html", destino,
               title=f"{titulo} — {config.NOME_SITE}", base_path="../" * profundidade,
               titulo_listagem=titulo, subtitulo=subtitulo, materias=lista,
               og_image=og, og_url=f"{config.SITE_URL}/{caminho}")
        criadas.append(caminho)

    for s in menu["secoes"]:
        da_secao = [m for m in materias if m["secao_slug"] == s["slug"]]
        pagina(f"secao/{s['slug']}.html", s["nome"], da_secao)
        for c in s["categorias"]:
            pagina(f"secao/{s['slug']}/{c['slug']}.html", c["nome"],
                   [m for m in da_secao if m["categoria_slug"] == c["slug"]],
                   subtitulo=s["nome"], profundidade=2)

    for a in menu["autores"]:
        pagina(f"autor/{a['slug']}.html", a["nome"],
               [m for m in materias if m["autor_slug"] == a["slug"]], subtitulo="Autor")

    return criadas
