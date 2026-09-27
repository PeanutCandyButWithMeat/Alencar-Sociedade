"""
Gerador estático do site Alencar e Sociedade.

Uso:
    python build.py

Lê tudo que está em content/*.md, gera o HTML de cada página em site/,
e cria site/search-index.json para a busca por palavra-chave.

Para publicar uma matéria nova: copie um arquivo de content/, edite os
metadados e o texto, rode este script de novo.
"""

import json
import shutil
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader

RAIZ = Path(__file__).parent
CONTEUDO_DIR = RAIZ / "content"
TEMPLATES_DIR = RAIZ / "templates"
STATIC_DIR = RAIZ / "static"
SAIDA_DIR = RAIZ / "docs"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def carregar_materias():
    materias = []
    for caminho in sorted(CONTEUDO_DIR.glob("*.md")):
        post = frontmatter.load(caminho)
        meta = post.metadata

        obrigatorios = ["titulo", "categoria", "idioma"]
        faltando = [campo for campo in obrigatorios if campo not in meta]
        if faltando:
            raise ValueError(
                f"{caminho.name}: faltam os campos {faltando} no cabeçalho da matéria."
            )

        corpo_html = markdown.markdown(post.content, extensions=["extra"])

        materias.append({
            "slug": meta.get("slug", caminho.stem),
            "titulo": meta["titulo"],
            "categoria": meta["categoria"],
            "idioma": meta["idioma"],
            "palavras_chave": meta.get("palavras_chave", []),
            "data": str(meta.get("data", "")),
            "resumo": meta.get("resumo", ""),
            "autor": meta.get("autor", "Adryan de Alencar"),
            "tempo_leitura": meta.get("tempo_leitura", ""),
            "destaque": bool(meta.get("destaque", False)),
            "conteudo_html": corpo_html,
        })
    return materias


def montar():
    if SAIDA_DIR.exists():
        shutil.rmtree(SAIDA_DIR)
    SAIDA_DIR.mkdir()

    for pasta in ["css", "fonts", "img", "js"]:
        origem = STATIC_DIR / pasta
        if origem.exists():
            shutil.copytree(origem, SAIDA_DIR / pasta)

    materias = carregar_materias()
    materias.sort(key=lambda m: m["data"], reverse=True)

    destaques = [m for m in materias if m["destaque"]]
    destaque = destaques[0] if destaques else (materias[0] if materias else None)
    lista = [m for m in materias if m is not destaque]

    # Página inicial
    tpl_index = env.get_template("index.html")
    (SAIDA_DIR / "index.html").write_text(
        tpl_index.render(
            title="Alencar e Sociedade",
            base_path="",
            destaque=destaque,
            materias=lista,
        ),
        encoding="utf-8",
    )

    # Sobre
    tpl_sobre = env.get_template("sobre.html")
    (SAIDA_DIR / "sobre.html").write_text(
        tpl_sobre.render(title="Sobre — Alencar e Sociedade", base_path=""),
        encoding="utf-8",
    )

    # Matérias individuais
    pasta_noticias = SAIDA_DIR / "noticias"
    pasta_noticias.mkdir()
    tpl_materia = env.get_template("article.html")
    for m in materias:
        idioma_html = "en" if m["idioma"].upper() == "EN" else "pt-BR"
        html = tpl_materia.render(
            title=f"{m['titulo']} — Alencar e Sociedade",
            base_path="../",
            html_lang=idioma_html,
            **m,
        )
        (pasta_noticias / f"{m['slug']}.html").write_text(html, encoding="utf-8")

    # Índice de busca
    indice = [
        {
            "titulo": m["titulo"],
            "categoria": m["categoria"],
            "idioma": m["idioma"],
            "palavras_chave": m["palavras_chave"],
            "resumo": m["resumo"],
            "url": f"noticias/{m['slug']}.html",
        }
        for m in materias
    ]
    (SAIDA_DIR / "search-index.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Build concluído: {len(materias)} matéria(s) gerada(s) em {SAIDA_DIR}/")


import subprocess
from datetime import datetime

def publicar():
    msg = f"Publicação {datetime.now():%Y-%m-%d %H:%M}"

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    montar()
    publicar()

