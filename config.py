"""Configurações e caminhos do site. Tudo que muda de um site pra outro fica aqui."""
from pathlib import Path

RAIZ = Path(__file__).parent
CONTEUDO = RAIZ / "content"
TEMPLATES = RAIZ / "templates"
STATIC = RAIZ / "static"
SAIDA = RAIZ / "docs"  # pasta de saída: o GitHub Pages publica a partir de /docs
DADOS = RAIZ / "data"  # estado que não faz parte do site (ex.: posts já feitos no Bluesky)

SITE_URL = "https://peanutcandybutwithmeat.github.io/Alencar-Sociedade"
NOME_SITE = "Alencar e Sociedade"
AUTOR_PADRAO = "Adryan de Alencar"

FONTE_BOLD = STATIC / "fonts/ZTNature-Black.ttf"
FONTE_REG = STATIC / "fonts/ZTNature-Medium.ttf"

LINKS = [
    {"titulo": "Últimas matérias", "url": "index.html", "desc": NOME_SITE},
    {"titulo": "LinkedIn", "url": "https://www.linkedin.com/in/adryan-de-alencar-61b386309", "desc": "Perfil profissional"},
    {"titulo": "Lattes", "url": "http://lattes.cnpq.br/3380250362638685", "desc": "Currículo Lattes"},
]

# Matérias que já circulavam com o endereço antigo (noticias/<slug>.html).
# O build deixa uma página-ponte só para estes slugs. Matérias novas não entram aqui.
REDIRECIONAR_ANTIGOS = [
    "a-relacao-da-filosofia-estetica-com-o-fingidor-de-samir-yazbek",
    "o-fingidor-de-samir-yazbek",
    "primeiro-turno-eleicoes-2026",
    "uma-reflexao-sobre-etnografia",
    "hegemonia-fora-do-senso-comum-um-estudo-gramsciano",
]
