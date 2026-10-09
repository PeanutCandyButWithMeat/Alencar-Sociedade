import json
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "docs"
SITE_URL = "https://peanutcandybutwithmeat.github.io/Alencar-Sociedade"
FONTE_BOLD = RAIZ / "static/fonts/ZTNature-Black.ttf"
FONTE_REG = RAIZ / "static/fonts/ZTNature-Medium.ttf"
env = Environment(loader=FileSystemLoader(RAIZ / "templates"))

LINKS = [
    {"titulo": "Últimas matérias", "url": "index.html", "desc": "Alencar e Sociedade"},
    {"titulo": "LinkedIn", "url": "https://www.linkedin.com/in/adryan-de-alencar-61b386309", "desc": "Perfil profissional"},
    {"titulo": "Lattes", "url": "http://lattes.cnpq.br/3380250362638685", "desc": "Currículo Lattes"},
]

def quebrar(draw, texto, fonte, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if draw.textlength(teste, font=fonte) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    return linhas + [atual]


def gerar_og(m):
    W, H, M = 1200, 630, 80
    img = Image.new("RGB", (W, H), "#111827")
    d = ImageDraw.Draw(img)
    tam = 64
    while True:  # diminui a fonte até o título caber em 4 linhas
        f_tit = ImageFont.truetype(str(FONTE_BOLD), tam)
        linhas = quebrar(d, m["titulo"], f_tit, W - 2 * M)
        if len(linhas) <= 4 or tam <= 32:
            break
        tam -= 4

    d.rectangle([0, 0, 16, H], fill="#F59E0B")
    d.text((M, M), m["categoria"].upper(), font=ImageFont.truetype(str(FONTE_REG), 30), fill="#F59E0B")
    for i, linha in enumerate(linhas):
        d.text((M, M + 80 + i * int(tam * 1.25)), linha, font=f_tit, fill="#F9FAFB")
    d.text((M, H - M - 28), f"{m['autor']}  ·  Alencar e Sociedade",
           font=ImageFont.truetype(str(FONTE_REG), 28), fill="#9CA3AF")

    destino = SAIDA / "img" / "og"
    destino.mkdir(parents=True, exist_ok=True)
    img.save(destino / f"{m['slug']}.jpg", quality=88)
    return f"img/og/{m['slug']}.jpg"


def carregar_materias():
    materias = []
    for caminho in (RAIZ / "content").glob("*.md"):
        post = frontmatter.load(caminho)
        faltando = {"titulo", "categoria", "idioma"} - post.metadata.keys()
        if faltando:
            raise ValueError(f"{caminho.name}: faltam os campos {sorted(faltando)}")
        materias.append({
            "slug": caminho.stem,
            "palavras_chave": [],
            "resumo": "",
            "autor": "Adryan de Alencar",
            "tempo_leitura": "",
            **post.metadata,
            "data": str(post.metadata.get("data", "")),
            "destaque": bool(post.metadata.get("destaque")),
            "conteudo_html": markdown.markdown(post.content, extensions=["extra"]),
        })
    return sorted(materias, key=lambda m: m["data"], reverse=True)


def render(modelo, destino, **ctx):
    destino.write_text(env.get_template(modelo).render(**ctx), encoding="utf-8")


def montar():
    shutil.rmtree(SAIDA, ignore_errors=True)
    shutil.copytree(RAIZ / "static", SAIDA)
    (SAIDA / "noticias").mkdir(exist_ok=True)

    materias = carregar_materias()
    destaque = next((m for m in materias if m["destaque"]), materias[0] if materias else None)
    og_home = f"{SITE_URL}/img/og/home.jpg"  # criar à mão em static/img/og/home.jpg

    render("index.html", SAIDA / "index.html", title="Alencar e Sociedade", base_path="",
           destaque=destaque, materias=[m for m in materias if m is not destaque],
           og_image=og_home, og_url=f"{SITE_URL}/")

    render("sobre.html", SAIDA / "sobre.html", title="Sobre — Alencar e Sociedade", base_path="",
           og_image=og_home, og_url=f"{SITE_URL}/sobre.html")

    render("links.html", SAIDA / "links.html", title="Links — Alencar e Sociedade",
           base_path="", links=LINKS,
           og_image=og_home, og_url=f"{SITE_URL}/links.html")

    for m in materias:
        imagem = m.get("imagem") or gerar_og(m)
        render("article.html", SAIDA / "noticias" / f"{m['slug']}.html",
               **m, title=f"{m['titulo']} — Alencar e Sociedade", base_path="../",
               html_lang="en" if m["idioma"].upper() == "EN" else "pt-BR",
               og_image=f"{SITE_URL}/{imagem}",
               og_url=f"{SITE_URL}/noticias/{m['slug']}.html")

    campos = ("titulo", "categoria", "idioma", "palavras_chave", "resumo")
    indice = [{**{c: m[c] for c in campos}, "url": f"noticias/{m['slug']}.html"} for m in materias]
    (SAIDA / "search-index.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Build concluído: {len(materias)} matéria(s) em {SAIDA}/")


def publicar():
    subprocess.run(["git", "add", "."], check=True)
    # commit falha (código 1) quando não há mudanças; nesse caso não faz push
    if subprocess.run(["git", "commit", "-m", f"Publicação {datetime.now():%Y-%m-%d %H:%M}"]).returncode == 0:
        subprocess.run(["git", "push"], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--publicar", action="store_true",
                        help="depois do build, faz commit e push")
    args = parser.parse_args()

    montar()
    if args.publicar:
        publicar()
