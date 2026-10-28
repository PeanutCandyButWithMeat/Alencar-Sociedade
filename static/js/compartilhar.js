/* Compartilhar: barra de share, imagem para Story e cartão do trecho selecionado.
   Depende de cartao.js (renderer) e das variáveis de cor do style.css. */
(() => {
  "use strict";

  const raiz = document.querySelector("[data-share]");
  const corpo = document.querySelector(".article__body");
  if (!raiz || !corpo || !window.AlencarCartao) return;

  const D = raiz.dataset;
  const EN = D.lang === "en";
  const URL_MATERIA = D.url;
  const MARCA = (document.querySelector(".logo")?.textContent || "").trim() || "Alencar e Sociedade";
  const POEMA = corpo.classList.contains("texto--poema");
  const MAX_CHARS = 320;

  const T = EN ? {
    trecho: "Share excerpt", materia: "Instagram", formato: "Format", cor: "Color",
    story: "Story", quadrado: "Square", terracota: "Terracotta", creme: "Cream", petroleo: "Teal",
    compartilhar: "Share image", baixar: "Download", copiar: "Copy link",
    copiado: "Link copied", copiadoStory: "Link copied. Paste it in the Story's link sticker.",
    curto: "Excerpt shortened to fit the card.", fechar: "Close",
  } : {
    trecho: "Compartilhar trecho", materia: "Instagram", formato: "Formato", cor: "Cor",
    story: "Story", quadrado: "Quadrado", terracota: "Terracota", creme: "Creme", petroleo: "Petróleo",
    compartilhar: "Compartilhar imagem", baixar: "Baixar", copiar: "Copiar link",
    copiado: "Link copiado", copiadoStory: "Link copiado. Cole no adesivo de link do Story.",
    curto: "Trecho encurtado para caber no cartão.", fechar: "Fechar",
  };

  /* ---------- utilitários ---------- */

  const el = (tag, attrs = {}, ...filhos) => {
    const n = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => (v === true ? n.setAttribute(k, "") : n.setAttribute(k, v)));
    n.append(...filhos);
    return n;
  };

  const guardar = (k, v) => { try { localStorage.setItem("cartao:" + k, v); } catch (_) {} };
  const lembrar = (k, padrao, validos) => {
    try {
      const v = localStorage.getItem("cartao:" + k);
      return v && validos.includes(v) ? v : padrao;
    } catch (_) { return padrao; }
  };

  const copiar = async (texto) => {
    try { await navigator.clipboard.writeText(texto); return true; } catch (_) { return false; }
  };

  function toast(msg) {
    const pai = dlg.open ? dlg : document.body; // o <dialog> modal cobre o resto da página
    const n = el("div", { class: "share-toast", role: "status" }, msg);
    pai.append(n);
    setTimeout(() => n.remove(), 3200);
  }

  // Paleta lida do CSS na hora: se mudar a cor no style.css, o cartão acompanha.
  function temas() {
    const v = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
    const terra = v("--terracotta"), petrol = v("--petrol"), creme = v("--cream"),
          ambar = v("--amber"), tinta = v("--ink");
    return {
      terracota: { bg: terra,   texto: creme, destaque: ambar, onda: [[petrol, 0.85], [ambar, 1]] },
      creme:     { bg: creme,   texto: tinta, destaque: terra, onda: [[petrol, 0.4], [ambar, 1]] },
      petroleo:  { bg: petrol,  texto: creme, destaque: ambar, onda: [[terra, 0.5],  [ambar, 1]] },
    };
  }

  async function carregarFontes(texto) {
    const amostra = texto + MARCA + D.autor + D.title + "\u201C\u201D\u2014\u2026\u00B7";
    try {
      await Promise.all([
        document.fonts.load("900 48px Nature", amostra),
        document.fonts.load("400 48px Kanopi", MARCA),
        document.fonts.load("500 32px Inter", amostra),
        document.fonts.load("400 32px Inter", amostra),
      ]);
    } catch (_) { /* segue com as fontes de reserva */ }
  }

  const podeCompartilharArquivo = (blob) => {
    try {
      return !!(blob && navigator.canShare &&
        navigator.canShare({ files: [new File([blob], "a.png", { type: "image/png" })] }));
    } catch (_) { return false; }
  };

  const cortar = (t, max) => {
    const corte = t.slice(0, max);
    return corte.slice(0, Math.max(corte.lastIndexOf(" "), max * 0.6)).trimEnd() + "\u2026";
  };

  /* ---------- diálogo do cartão ---------- */

  const estado = {
    tipo: "trecho", texto: "", blob: null, token: 0,
    formato: lembrar("formato", "story", Object.keys(AlencarCartao.FORMATOS)),
    tema: lembrar("tema", "terracota", ["terracota", "creme", "petroleo"]),
  };

  const canvas = el("canvas", { "aria-label": T.trecho, role: "img" });
  const ui = {
    titulo: el("h2", { class: "cartao__titulo", id: "cartao-titulo" }),
    fechar: el("button", { type: "button", class: "cartao__fechar", "aria-label": T.fechar }, "\u00D7"),
    aviso: el("p", { class: "cartao__aviso", hidden: true }, T.curto),
    compartilhar: el("button", { type: "button", class: "share__btn share__btn--destaque", hidden: true }, T.compartilhar),
    baixar: el("button", { type: "button", class: "share__btn" }, T.baixar),
    copiar: el("button", { type: "button", class: "share__btn" }, T.copiar),
  };

  function grupo(rotulo, chave, opcoes) {
    const botoes = Object.entries(opcoes).map(([valor, nome]) => {
      const b = el("button", { type: "button", class: "opcao", "data-valor": valor }, nome);
      b.addEventListener("click", () => {
        estado[chave] = valor;
        guardar(chave, valor);
        marcar();
        renderizar();
      });
      return b;
    });
    const marcar = () => botoes.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.valor === estado[chave])));
    marcar();
    return el("div", { class: "cartao__grupo", role: "group", "aria-label": rotulo },
      el("span", { class: "cartao__rotulo" }, rotulo), ...botoes);
  }

  const dlg = el("dialog", { class: "cartao", "aria-labelledby": "cartao-titulo" },
    el("div", { class: "cartao__corpo" },
      el("div", { class: "cartao__topo" }, ui.titulo, ui.fechar),
      el("div", { class: "cartao__previa" }, canvas),
      ui.aviso,
      grupo(T.formato, "formato", { story: T.story, quadrado: T.quadrado }),
      grupo(T.cor, "tema", { terracota: T.terracota, creme: T.creme, petroleo: T.petroleo }),
      el("div", { class: "cartao__acoes" }, ui.compartilhar, ui.baixar, ui.copiar)));
  document.body.append(dlg);

  function atualizarAcoes() {
    const pronto = !!estado.blob;
    ui.baixar.disabled = !pronto;
    ui.compartilhar.disabled = !pronto;
    // sem canShare (desktop, Firefox) o botão nunca aparece e sobra o "Baixar"
    ui.compartilhar.hidden = !navigator.canShare || (pronto && !podeCompartilharArquivo(estado.blob));
  }

  async function renderizar() {
    const token = ++estado.token;
    estado.blob = null;
    atualizarAcoes();
    await carregarFontes(estado.texto);
    if (token !== estado.token) return;

    AlencarCartao.desenhar(canvas, {
      formato: estado.formato,
      paleta: temas()[estado.tema],
      texto: estado.texto,
      tipo: estado.tipo,
      marca: MARCA,
      autor: D.autor,
      rodape: estado.tipo === "trecho" ? D.title : D.categoria,
    });
    canvas.toBlob((b) => {
      if (token !== estado.token) return;
      estado.blob = b;       // pronto antes do clique: share() precisa rodar dentro do gesto do toque
      atualizarAcoes();
    }, "image/png");
  }

  function abrir(tipo, texto) {
    const longo = texto.length > MAX_CHARS;
    estado.tipo = tipo;
    estado.texto = longo ? cortar(texto, MAX_CHARS) : texto;
    ui.titulo.textContent = tipo === "trecho" ? T.trecho : T.materia;
    ui.aviso.hidden = !longo;
    canvas.setAttribute("aria-label", estado.texto);
    if (!dlg.open) dlg.showModal();
    renderizar();
  }

  function baixar() {
    if (!estado.blob) return;
    const a = el("a", { href: URL.createObjectURL(estado.blob), download: `${D.slug || "cartao"}-${estado.tipo}.png` });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  async function compartilharImagem() {
    if (!estado.blob) return;
    const arquivo = new File([estado.blob], `${D.slug || "cartao"}.png`, { type: "image/png" });
    const copiou = copiar(URL_MATERIA); // sem await: o share() precisa sair dentro do gesto do toque
    try {
      await navigator.share({ files: [arquivo], text: `${D.title}\n${URL_MATERIA}` });
      if (await copiou) toast(T.copiadoStory);
    } catch (e) {
      if (e.name !== "AbortError") baixar();
    }
  }

  ui.fechar.addEventListener("click", () => dlg.close());
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); }); // clique no fundo escuro
  ui.baixar.addEventListener("click", baixar);
  ui.compartilhar.addEventListener("click", compartilharImagem);
  ui.copiar.addEventListener("click", async () => toast((await copiar(URL_MATERIA)) ? T.copiado : URL_MATERIA));

  /* ---------- barra de compartilhar (fim da matéria) ---------- */

  const acoes = {
    nativo: () => navigator.share({ title: D.title, text: D.title, url: URL_MATERIA }).catch(() => {}),
    story: () => abrir("materia", D.title),
    copiar: async () => toast((await copiar(URL_MATERIA)) ? T.copiado : URL_MATERIA),
  };
  raiz.querySelectorAll("[data-acao]").forEach((item) => {
    const nome = item.dataset.acao;
    if (nome === "nativo" && !navigator.share) return; // só aparece onde o aparelho tem share nativo
    item.closest("li").hidden = false;
    item.addEventListener("click", acoes[nome]);
  });

  /* ---------- seleção de texto -> botão flutuante ---------- */

  const btnSel = el("button", { type: "button", class: "sel-share", hidden: true }, T.trecho);
  document.body.append(btnSel);
  let selecionado = "";
  let adiar;

  const normalizar = (t) => POEMA
    ? t.split(/\n+/).map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n")
    : t.replace(/\s+/g, " ").trim();

  function atualizarSelecao() {
    if (dlg.open) return;
    const s = window.getSelection();
    if (!s || s.isCollapsed || !s.rangeCount) { btnSel.hidden = true; return; }
    const r = s.getRangeAt(0);
    if (!corpo.contains(r.commonAncestorContainer)) { btnSel.hidden = true; return; }
    const texto = normalizar(s.toString());
    if (texto.length < 8) { btnSel.hidden = true; return; }
    selecionado = texto;

    btnSel.hidden = false;
    const caixa = r.getBoundingClientRect();
    const rects = r.getClientRects();
    const ultimo = rects.length ? rects[rects.length - 1] : caixa;
    const toque = matchMedia("(pointer: coarse)").matches;
    const larg = btnSel.offsetWidth, alt = btnSel.offsetHeight;

    // toque: o menu nativo do sistema fica em cima da seleção, então o botão vai embaixo
    let y = toque || caixa.top - alt - 10 < 8 ? ultimo.bottom + 12 : caixa.top - alt - 10;
    let x = caixa.left + caixa.width / 2 - larg / 2;
    x = Math.min(Math.max(8, x), window.innerWidth - larg - 8);
    btnSel.style.left = `${x + window.scrollX}px`;
    btnSel.style.top = `${y + window.scrollY}px`;
  }

  document.addEventListener("selectionchange", () => {
    clearTimeout(adiar);
    adiar = setTimeout(atualizarSelecao, 160);
  });
  window.addEventListener("resize", () => { btnSel.hidden = true; });
  btnSel.addEventListener("mousedown", (e) => e.preventDefault()); // não perde a seleção ao clicar
  btnSel.addEventListener("click", () => {
    const texto = selecionado;
    btnSel.hidden = true;
    window.getSelection()?.removeAllRanges();
    if (texto) abrir("trecho", texto);
  });
})();
