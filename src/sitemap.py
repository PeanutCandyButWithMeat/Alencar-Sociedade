import xml.etree.ElementTree as ET
from urllib.parse import quote

import config

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def gerar_sitemap(materias):
    ET.register_namespace("", NS)
    urlset = ET.Element(f"{{{NS}}}urlset")

    paginas = [("", None), ("sobre.html", None), ("links.html", None)]
    paginas += [(m["caminho"], m["data"] or None) for m in materias]

    for caminho, data in paginas:
        url = ET.SubElement(urlset, f"{{{NS}}}url")
        ET.SubElement(url, f"{{{NS}}}loc").text = f"{config.SITE_URL}/{quote(caminho, safe='/')}"
        if data:
            ET.SubElement(url, f"{{{NS}}}lastmod").text = data[:10]  # YYYY-MM-DD

    arvore = ET.ElementTree(urlset)
    ET.indent(arvore, space="  ")
    arvore.write(config.SAIDA / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    print(f"Sitemap gerado: {len(paginas)} URLs")
