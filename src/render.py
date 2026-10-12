from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import config

env = Environment(loader=FileSystemLoader(config.TEMPLATES))


def render(modelo: str, destino: Path, **ctx):
    destino.write_text(env.get_template(modelo).render(**ctx), encoding="utf-8")
