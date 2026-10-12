import frontmatter
import markdown

import config

CAMPOS_OBRIGATORIOS = {"titulo", "categoria", "idioma"}


def carregar_materias():
    """Lê content/*.md e devolve a lista de matérias, da mais nova para a mais antiga."""
    materias = []
    for caminho in config.CONTEUDO.glob("*.md"):
        post = frontmatter.load(caminho)
        faltando = CAMPOS_OBRIGATORIOS - post.metadata.keys()
        if faltando:
            raise ValueError(f"{caminho.name}: faltam os campos {sorted(faltando)}")
        materias.append({
            "slug": caminho.stem,
            "palavras_chave": [],
            "resumo": "",
            "autor": config.AUTOR_PADRAO,
            "tempo_leitura": "",
            **post.metadata,
            "data": str(post.metadata.get("data", "")),
            "destaque": bool(post.metadata.get("destaque")),
            "conteudo_html": markdown.markdown(post.content, extensions=["extra"]),
        })
    return sorted(materias, key=lambda m: m["data"], reverse=True)
