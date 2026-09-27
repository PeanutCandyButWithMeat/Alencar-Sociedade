// Busca por palavra-chave usando o search-index.json gerado pelo build.py.
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('busca');
  const lista = document.getElementById('resultados-busca');
  if (!input || !lista) return;

  const script = document.currentScript || document.querySelector('script[data-index]');
  const indexUrl = script.getAttribute('data-index');

  let indice = [];
  fetch(indexUrl)
    .then((res) => res.json())
    .then((dados) => { indice = dados; })
    .catch((err) => console.error('Não foi possível carregar o índice de busca:', err));

  input.addEventListener('input', () => {
    const termo = input.value.trim().toLowerCase();
    lista.innerHTML = '';
    if (!termo) return;

    const resultados = indice.filter((m) => {
      const alvo = [m.titulo, m.categoria, m.resumo, ...(m.palavras_chave || [])]
        .join(' ')
        .toLowerCase();
      return alvo.includes(termo);
    });

    if (resultados.length === 0) {
      lista.innerHTML = '<li>Nenhuma matéria encontrada.</li>';
      return;
    }

    resultados.forEach((m) => {
      const li = document.createElement('li');
      li.innerHTML = `<a href="${m.url}">${m.titulo}</a> <span class="tag tag--category">${m.categoria}</span>`;
      lista.appendChild(li);
    });
  });
});
