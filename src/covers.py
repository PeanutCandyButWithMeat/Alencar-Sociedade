"""Geração das imagens de capa (Open Graph) das matérias."""
from PIL import Image, ImageDraw, ImageFont

import config


def _quebrar(draw, texto, fonte, largura):
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
    """Cria docs/img/og/<slug>.jpg e devolve o caminho relativo ao site."""
    W, H, M = 1200, 630, 80
    img = Image.new("RGB", (W, H), "#111827")
    d = ImageDraw.Draw(img)
    tam = 64
    while True:  # diminui a fonte até o título caber em 4 linhas
        f_tit = ImageFont.truetype(str(config.FONTE_BOLD), tam)
        linhas = _quebrar(d, m["titulo"], f_tit, W - 2 * M)
        if len(linhas) <= 4 or tam <= 32:
            break
        tam -= 4

    d.rectangle([0, 0, 16, H], fill="#F59E0B")
    d.text((M, M), m["categoria"].upper(),
           font=ImageFont.truetype(str(config.FONTE_REG), 30), fill="#F59E0B")
    for i, linha in enumerate(linhas):
        d.text((M, M + 80 + i * int(tam * 1.25)), linha, font=f_tit, fill="#F9FAFB")
    d.text((M, H - M - 28), f"{m['autor']}  ·  {config.NOME_SITE}",
           font=ImageFont.truetype(str(config.FONTE_REG), 28), fill="#9CA3AF")

    destino = config.SAIDA / "img" / "og"
    destino.mkdir(parents=True, exist_ok=True)
    img.save(destino / f"{m['slug']}.jpg", quality=88)
    return f"img/og/{m['slug']}.jpg"
