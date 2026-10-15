import json

import config

CAMPOS = ("titulo", "categoria", "idioma", "palavras_chave", "resumo", "autor", "secao")


def gerar_indice_busca(materias):
    indice = [{**{c: m[c] for c in CAMPOS}, "url": m["caminho"]} for m in materias]
    (config.SAIDA / "search-index.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
