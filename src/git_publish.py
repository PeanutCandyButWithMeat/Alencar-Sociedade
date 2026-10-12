import subprocess
from datetime import datetime


def publicar():
    """Commit + push do que mudou. Sem mudanças, não faz push."""
    subprocess.run(["git", "add", "."], check=True)
    # commit falha (código 1) quando não há mudanças; nesse caso não faz push
    if subprocess.run(["git", "commit", "-m", f"Publicação {datetime.now():%Y-%m-%d %H:%M}"]).returncode == 0:
        subprocess.run(["git", "push"], check=True)
