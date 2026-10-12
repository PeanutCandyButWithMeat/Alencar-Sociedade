import unicodedata

import frontmatter
import markdown

import config

CAMPOS_OBRIGATORIOS = {"titulo", "categoria", "idioma"}


def slugificar(texto):
    """'Críticas Culturais' -> 'criticas-culturais'"""
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return "-".join("".join(c if c.isalnum() else " " for c in sem_acento.lower()).split())


def carregar_materias():
    """Lê content/*.md e devolve a lista de matérias, da mais nova para a mais antiga."""
    materias = []
    for caminho in config.CONTEUDO.glob("*.md"):
        post = frontmatter.load(caminho)
        faltando = CAMPOS_OBRIGATORIOS - post.metadata.keys()
        if faltando:
            raise ValueError(f"{caminho.name}: faltam os campos {sorted(faltando)}")
        materia = {
            "slug": caminho.stem,
            "palavras_chave": [],
            "resumo": "",
            "autor": config.AUTOR_PADRAO,
            "tempo_leitura": "",
            **post.metadata,
            "data": str(post.metadata.get("data", "")),
            "destaque": bool(post.metadata.get("destaque")),
            "conteudo_html": markdown.markdown(post.content, extensions=["extra"]),
        }
        # noticias/<categoria>/<idioma>/<slug>.html, tudo derivado do frontmatter
        materia["categoria_slug"] = slugificar(materia["categoria"])
        materia["caminho"] = (f"noticias/{materia['categoria_slug']}/"
                              f"{str(materia['idioma']).lower()}/{materia['slug']}.html")
        materia["base_path"] = "../" * materia["caminho"].count("/")
        materias.append(materia)
    return sorted(materias, key=lambda m: m["data"], reverse=True)
