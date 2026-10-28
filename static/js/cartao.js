/* Desenha o cartão de compartilhamento (story 9:16 ou quadrado) num <canvas>.
   Não toca no DOM: recebe tudo por parâmetro, então dá para testar fora do navegador.
   As ondas usam os mesmos caminhos SVG do header/footer do site (base.html). */
(function (global) {
  "use strict";

  const FORMATOS = {
    // topo/base = zonas que o Instagram cobre com a interface do Story (nome e caixa de resposta)
    story:    { w: 1080, h: 1920, margem: 100, topo: 250, base: 340, marca: 46, tamMax: 88, tamMin: 40 },
    quadrado: { w: 1080, h: 1080, margem: 90,  topo: 90,  base: 190, marca: 40, tamMax: 76, tamMin: 34 },
  };

  const ONDAS = [
    "M0,20 C200,50 400,0 600,20 C800,50 1000,0 1200,20 L1200,60 L0,60 Z",
    "M0,35 C200,10 400,60 600,35 C800,10 1000,60 1200,35 L1200,60 L0,60 Z",
  ];

  const FONTE_TEXTO = (tam) => `900 ${tam}px Nature, Inter, sans-serif`;
  const ENTRELINHA = 1.26;

  function quebrar(c, texto, larg) {
    const saida = [];
    texto.split("\n").forEach((paragrafo) => {
      let atual = "";
      paragrafo.split(/\s+/).filter(Boolean).forEach((palavra) => {
        const teste = atual ? atual + " " + palavra : palavra;
        if (!atual || c.measureText(teste).width <= larg) atual = teste;
        else { saida.push(atual); atual = palavra; }
      });
      if (atual) saida.push(atual);
    });
    return saida;
  }

  function encaixar(c, texto, larg) {
    if (c.measureText(texto).width <= larg) return texto;
    while (texto.length > 1 && c.measureText(texto + "…").width > larg) texto = texto.slice(0, -1);
    return texto.trimEnd() + "…";
  }

  /* o = { formato, paleta:{bg,texto,destaque,onda:[[cor,alpha],[cor,alpha]]},
           texto, tipo:"trecho"|"materia", marca, autor, rodape } */
  function desenhar(canvas, o) {
    const F = FORMATOS[o.formato] || FORMATOS.story;
    const P = o.paleta;
    const W = F.w, H = F.h, M = F.margem, L = W - 2 * M;
    canvas.width = W;
    canvas.height = H;
    const c = canvas.getContext("2d");
    c.textBaseline = "alphabetic";

    c.fillStyle = P.bg;
    c.fillRect(0, 0, W, H);

    // ondas no pé do cartão (mesma ideia do footer do site)
    const altOnda = Math.round(W * 0.13);
    P.onda.forEach(([cor, alpha], i) => {
      c.save();
      c.globalAlpha = alpha;
      c.fillStyle = cor;
      c.translate(0, H - altOnda);
      c.scale(W / 1200, altOnda / 60);
      c.fill(new Path2D(ONDAS[i]));
      c.restore();
    });

    // marca
    c.fillStyle = P.texto;
    c.font = `400 ${F.marca}px Kanopi, Nature, sans-serif`;
    c.fillText(o.marca, M, F.topo + F.marca);

    // autoria (fixa no pé do bloco)
    const yFim = H - F.base;
    c.fillStyle = P.destaque;
    c.fillRect(M, yFim - 124, 72, 6);
    c.fillStyle = P.texto;
    c.font = "500 40px Inter, sans-serif";
    c.fillText(encaixar(c, o.autor, L), M, yFim - 56);
    c.globalAlpha = 0.8;
    c.font = "400 32px Inter, sans-serif";
    c.fillText(encaixar(c, o.rodape, L), M, yFim);
    c.globalAlpha = 1;

    // zona do texto
    const zonaTopo = F.topo + F.marca + 80;
    const zonaBase = yFim - 124 - 70;
    const zonaAlt = zonaBase - zonaTopo;

    // aspas de abertura (só em trecho), medidas de verdade para não depender da fonte
    let aspas = null;
    if (o.tipo === "trecho") {
      const tamAspas = F.tamMax * 2;
      c.font = `900 ${tamAspas}px Nature, Inter, serif`;
      const m = c.measureText("\u201C");
      aspas = { tam: tamAspas, asc: m.actualBoundingBoxAscent, h: m.actualBoundingBoxAscent + m.actualBoundingBoxDescent };
    }
    const folgaAspas = aspas ? aspas.h + 28 : 0;

    // encolhe a fonte até o texto caber
    let tam = F.tamMax, linhas, altTexto;
    for (;; tam -= 2) {
      c.font = FONTE_TEXTO(tam);
      linhas = quebrar(c, o.texto, L);
      altTexto = linhas.length * tam * ENTRELINHA;
      if (folgaAspas + altTexto <= zonaAlt || tam <= F.tamMin) break;
    }

    // centraliza o grupo (aspas + texto) na zona
    let y = zonaTopo + Math.max(0, (zonaAlt - (folgaAspas + altTexto)) / 2);
    if (aspas) {
      c.fillStyle = P.destaque;
      c.font = `900 ${aspas.tam}px Nature, Inter, serif`;
      c.fillText("\u201C", M - 6, y + aspas.asc);
      y += folgaAspas;
    }
    c.fillStyle = P.texto;
    c.font = FONTE_TEXTO(tam);
    linhas.forEach((linha, i) => c.fillText(linha, M, y + tam * 0.9 + i * tam * ENTRELINHA));

    return { tam, linhas: linhas.length };
  }

  const api = { FORMATOS, desenhar };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.AlencarCartao = api;
})(typeof window !== "undefined" ? window : globalThis);
