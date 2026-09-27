// Injeta os arquivos de /partials/ nos lugares marcados com data-include.
// Ex.: <div data-include="/partials/header.html"></div>
document.querySelectorAll('[data-include]').forEach((el) => {
  const path = el.getAttribute('data-include');
  fetch(path)
    .then((res) => {
      if (!res.ok) throw new Error(`Não encontrado: ${path}`);
      return res.text();
    })
    .then((html) => {
      el.outerHTML = html;
    })
    .catch((err) => console.error(err));
});
