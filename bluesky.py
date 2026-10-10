import json
import os
from pathlib import Path
import time
from atproto_client.exceptions import InvokeTimeoutError

ARQUIVO = Path(__file__).parent / "bluesky.json"

def _login(client, tentativas=3):
    for i in range(1, tentativas + 1):
        try:
            client.login(os.environ["BSKY_HANDLE"], os.environ["BSKY_APP_PASSWORD"])
            return
        except InvokeTimeoutError:
            if i == tentativas:
                raise
            print(f"Timeout ao conectar no Bluesky (tentativa {i}/{tentativas}), tentando de novo…")
            time.sleep(3)

def _carregar():
    return json.loads(ARQUIVO.read_text("utf-8")) if ARQUIVO.exists() else {}


def _salvar(dados):
    ARQUIVO.write_text(json.dumps(dados, indent=2, ensure_ascii=False), "utf-8")


def _postar(titulo, descricao, url, capa_path=None):
    from atproto import Client, models  # import aqui: só exige a lib quando for postar

    client = Client()
    _login(client)

    thumb = None
    if capa_path and Path(capa_path).exists():
        thumb = client.upload_blob(Path(capa_path).read_bytes()).blob

    embed = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            uri=url, title=titulo, description=descricao, thumb=thumb
        )
    )
    resp = client.send_post(text=f"{titulo}\n\n{descricao}"[:300], embed=embed)
    return resp.uri


def web_url(uri):
    """at://did/app.bsky.feed.post/rkey -> link clicável no bsky.app"""
    _, _, did, _, rkey = uri.split("/")
    return f"https://bsky.app/profile/{did}/post/{rkey}"


def garantir_post(slug, titulo, descricao, url, capa_path=None, confirmar=True):
    """Posta no Bluesky se a matéria ainda não tem post. Retorna o URI (ou None)."""
    dados = _carregar()
    if slug in dados:
        return dados[slug]

    if confirmar and input(f"Postar '{titulo}' no Bluesky? [s/N] ").strip().lower() != "s":
        return None

    uri = _postar(titulo, descricao, url, capa_path)
    dados[slug] = uri
    _salvar(dados)
    return uri


def uri_de(slug):
    """Só consulta, sem postar. Útil para o template."""
    return _carregar().get(slug)
