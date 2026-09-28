/* Psychological Predecessors of AI — router, registry, views.
   Stage 0: the scaffold and the stated program. The readers, concordance,
   atlas and timeline follow the sibling sites' proven machinery as the
   modules ship. */
const D = { works: [], texts: {} };
const view = document.getElementById("view");

const esc = s => String(s ?? "").replace(/[&<>"']/g, m =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
const el = h => { const t = document.createElement("template"); t.innerHTML = h.trim(); return t.content.firstElementChild; };

/* The four lines of the corpus. It confines itself to what is in the
   United States public domain — published through 1930 — and ends where
   the machines begin to learn. */
const LINIE = {
  messen: "The measured mind",
  lernen: "The learning animal",
  automat: "The automaton debate",
  labor: "The machine in the laboratory",
};
const LCOLOR = { messen: "var(--messen)", lernen: "var(--lernen)",
  automat: "var(--automat)", labor: "var(--labor)" };
const LLEDE = {
  messen: "Sensation brought under a formula, memory under a curve, association under a " +
    "stopwatch, intelligence under a factor and a scale: Fechner, Ebbinghaus, Galton, " +
    "Spearman, Binet. The line that ends, generations later, in the benchmark.",
  lernen: "From Hartley's associations and Bain's trial and error through Morgan's canon, " +
    "Loeb's tropisms, Thorndike's law of effect, Watson's manifesto, Pavlov's conditioned " +
    "reflexes — and Köhler's insight as the counter-evidence within. The ancestral line of " +
    "reinforcement learning.",
  automat: "Huxley's conscious automata, James's reply that consciousness is a fighter for " +
    "ends, McDougall's last defence of the soul: the nineteenth century's debate about " +
    "machine minds, conducted about our own.",
  labor: "Where the two lines converge: Hull's aptitude-forecasting machinery and the " +
    "Hull–Baernstein conditioning machine of 1929/30 — psychologists building a device " +
    "that learns. The corpus closes here.",
};

/* ------------------------------------------------------- citation grid */
/* Each shipped work defines how a unit is cited. */
const CITE = {
  huxley: (sec, u) => `Aut. [${u.n}]`,
  thorndike: (sec, u) =>
    sec.id === 'laws' ? `AI, ch. VI [${u.k}]` : `AI, ch. II [${u.k}]`,
  spearman: (sec, u) => `GI [${u.k}]`,
  ebbinghaus: (sec, u) => `Mem. [${u.k}]`,
  fechner: (sec, u) => `EP [${u.k}]`,
  galton: (sec, u) => `IHF [${u.k}]`,
  binet: (sec, u) => `DIC [${u.k}]`,
  morgan: (sec, u) => `CP [${u.k}]`,
  loeb: (sec, u) => `CPB [${u.k}]`,
  watson: (sec, u) => `PBV [${u.n}]`,
  pavlov: (sec, u) => `CR [${u.k}]`,
  mcdougall: (sec, u) => `BM [${u.k}]`,
  bain: (sec, u) => `SI [${u.k}]`,
  james: (sec, u) => sec.id === 'automata' ? `AWA [${u.k}]` : `PP [${u.k}]`,
};
const citeOf = (workId, sec, u) => (CITE[workId] || ((s, x) => `[${x.n}]`))(sec, u);

/* One public-domain plate per module where a suitable image exists
   (assets/plates/, registry data/plates.json, built by tools/build-plates.py). */
const plateFig = id => {
  const pl = (D.plates || {})[id];
  return pl ? `<figure class="plate">
    <img src="assets/plates/${id}.jpg" alt="${esc(pl.caption)}" loading="lazy">
    <figcaption class="fine">${esc(pl.caption)}
      <span style="color:var(--fg3)"> — ${esc(pl.credit)}</span></figcaption>
  </figure>` : "";
};

const ROUTES = {};
let atlasStop = null;
function route() {
  const h = (location.hash || "#/overview").slice(2).split("/");
  const name = h[0] || "overview";
  document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("active", a.dataset.v === name));
  if (atlasStop) { atlasStop(); atlasStop = null; }
  view.innerHTML = ""; window.scrollTo(0, 0);
  (ROUTES[name] || viewOverview)(h.slice(1));
}

/* ============================================================ OVERVIEW */
function viewOverview() {
  view.append(el(`<div>
    <div class="viewhead">
      <span class="tag">Research apparatus · in construction</span>
      <h1>Before the machines could learn, psychologists made the mind lawful</h1>
      ${(D.plates || {}).overview ? `<figure class="plate anchor">
        <a href="#/works/galton"><img src="assets/plates/overview.jpg"
          alt="${esc(D.plates.overview.caption)}"></a>
        <figcaption class="fine">${esc(D.plates.overview.caption)}
          <a href="#/works/galton">The module carries it.</a>
          <span style="color:var(--fg3)"> — ${esc(D.plates.overview.credit)}</span></figcaption>
      </figure>` : ""}
      <p class="lede">Artificial intelligence has a philosophical prehistory — reasoning become
      reckoning — and it has a psychological one: the mind become mechanism, measure, and law of
      learning. This apparatus will collect the public-domain sources of that second prehistory in
      citable, searchable editions: the texts in which sensation was brought under a formula and
      memory under a curve; in which animals taught the laws of learning that machines would one
      day obey; in which the question whether we ourselves are automata was argued at full
      strength — and the texts of 1928–1930 in which psychologists began building machines that
      learn. It ends, deliberately, at that threshold: Craik, McCulloch &amp; Pitts, Wiener and
      Turing remain in copyright, and are named in the <a href="#/coda">coda</a>.</p>
      <p class="fine">A sister apparatus carries the philosophical line —
      <a href="https://philosophical-predecessors-of-ai.netlify.app" rel="noopener">Calculemus:
      philosophical predecessors of AI</a> — and the two will cross-reference each other. The
      method follows the same discipline: everything public domain, every paragraph citable,
      working translations marked as such, no tracking.</p>
    </div>

    <div class="grid g2" style="margin-bottom:1.6rem">
      ${Object.keys(LINIE).map(k => `
      <div class="card linie-${k}">
        <span class="tag" style="color:${LCOLOR[k]}">${esc(LINIE[k])}</span>
        <p style="font-size:.9rem;color:var(--fg2);margin:.3rem 0 0">${esc(LLEDE[k])}</p>
      </div>`).join("")}
    </div>

    <h2>The program — ${D.works.filter(w=>w.status==="shipped").length} of ${D.works.length} modules shipped</h2>
    <p class="fine" style="margin:.2rem 0 1rem">Each entry names its source digitisation now, and
    moves into a reader as it ships. Status is tracked here and in the repository.</p>
    <div class="grid g2" id="worklist"></div>
  </div>`));
  const wl = view.querySelector("#worklist");
  for (const w of D.works) wl.append(workCard(w));
}

function workCard(w) {
  const open = w.status === "shipped";
  const card = el(`<div class="workcard card linie-${w.linie}" ${open ? 'style="cursor:pointer"' : ""}>
    ${(D.plates || {})[w.id] ? `<img class="platethumb" src="assets/plates/${w.id}_t.jpg" alt="" loading="lazy">` : ""}
    <div style="display:flex;gap:.6rem;align-items:baseline;justify-content:space-between;flex-wrap:wrap">
      <strong style="font-family:var(--serif)">${esc(w.autor)}</strong>
      <span class="status ${open ? "shipped" : "planned"}">${open ? "reader" : "planned"}</span>
    </div>
    <p class="fine" style="margin:.1rem 0 .3rem">${esc(w.leben)} · ${esc(w.sprachen)}</p>
    <h3 style="margin:.1rem 0 .3rem;font-size:1rem">${esc(w.titel)}</h3>
    <p style="font-size:.88rem;color:var(--fg2);margin:0">${esc(w.claim)}</p>
    ${open ? "" : `<p class="fine" style="margin:.45rem 0 0">Planned: ${esc(w.geplant)}</p>`}
  </div>`);
  if (open) card.onclick = () => location.hash = `#/works/${w.id}`;
  return card;
}

/* ============================================================== READER */
function workReader(id, secId) {
  const w = D.works.find(x => x.id === id);
  const t = D.texts[id];
  if (!w || !t) { location.hash = "#/works"; return; }
  if (secId) return sectionReader(w, t, secId);
  view.append(el(`<div>
    <p class="fine"><a href="#/works">← All works</a></p>
    <div class="viewhead">
      <span class="tag" style="color:${LCOLOR[w.linie]}">${esc(w.autor)} · ${esc(String(t.jahr))}</span>
      <h1>${esc(t.titel)}</h1>
      <p class="lede">${esc(w.claim)}</p>
    </div>
    ${plateFig(id)}
    <div class="grid g2" id="toc"></div>
    <p class="fine" style="margin-top:1.2rem">Cited as <span class="mono">${esc(t.zitierweise)}</span>.
      ${esc(t.quelle)} ${esc(t.hinweis || "")}</p>
  </div>`));
  const toc = view.querySelector("#toc");
  for (const s of t.sections) {
    const card = el(`<div class="workcard card linie-${w.linie}" style="cursor:pointer">
      <div style="display:flex;gap:.6rem;align-items:baseline;justify-content:space-between">
        <h3 style="margin:0;font-size:1rem">${esc(s.titel)}</h3>
        <span class="fine">${s.units.length} ¶</span></div>
    </div>`);
    card.onclick = () => location.hash = `#/works/${id}/${s.id}`;
    toc.append(card);
  }
}

function sectionReader(w, t, secId) {
  secId = secId.split("@")[0];
  const i = t.sections.findIndex(s => s.id === secId);
  if (i < 0) { location.hash = `#/works/${w.id}`; return; }
  const s = t.sections[i];
  const prev = t.sections[(i - 1 + t.sections.length) % t.sections.length];
  const next = t.sections[(i + 1) % t.sections.length];
  view.append(el(`<div>
    <p class="fine"><a href="#/works/${w.id}">← ${esc(w.kurz)}</a>${t.sections.length > 1 ? ` ·
      <a href="#/works/${w.id}/${prev.id}">${esc(prev.titel.split("—")[0])}</a> ·
      <a href="#/works/${w.id}/${next.id}">${esc(next.titel.split("—")[0])}</a>` : ""}</p>
    <div class="viewhead">
      <span class="tag" style="color:${LCOLOR[w.linie]}">${esc(w.autor)} · ${esc(String(t.jahr))}</span>
      <h1 style="font-size:1.4rem">${esc(s.titel)}</h1>
      <p class="fine">${s.units.length} paragraphs · cited as shown on each paragraph</p>
    </div>
    <div id="langbar"></div>
    <div id="body"></div>
    <p class="fine">${esc(t.quelle)} ${esc(t.hinweis || "")}</p>
  </div>`));
  const bilingual = s.units.some(u => u.orig);
  const render = () => {
    view.querySelector("#body").innerHTML = s.units.map(u => unitHtml(w, s, u)).join("");
  };
  if (bilingual) {
    const bar = el(`<div class="toolbar" style="margin-bottom:1rem">
      ${["en", "orig", "both"].map(m => `<button class="chip ${LANG === m ? "on" : ""}" data-m="${m}">
        ${{ en: "English", orig: "Original", both: "Both" }[m]}</button>`).join(" ")}</div>`);
    bar.querySelectorAll("[data-m]").forEach(b => b.onclick = () => {
      LANG = b.dataset.m;
      bar.querySelectorAll("[data-m]").forEach(x => x.classList.toggle("on", x.dataset.m === LANG));
      render();
    });
    view.querySelector("#langbar").append(bar);
  }
  render();
  const anchor = (location.hash.split("@")[1] || "");
  if (anchor) setTimeout(() =>
    document.getElementById("u" + anchor)?.scrollIntoView({ behavior: "instant", block: "start" }), 0);
}

let LANG = "en"; /* language mode for bilingual readers: en | orig | both */

function unitHtml(w, s, u) {
  const label = u.label ? `<p class="ulabel">${esc(u.label)}</p>` : "";
  const note = u.note ? `<p class="fine" style="color:var(--acc)">${esc(u.note)}</p>` : "";
  let body;
  if (!u.orig) body = `<p class="readable">${esc(u.txt)}</p>`;
  else if (LANG === "orig") body = `<p class="readable">${esc(u.orig)}</p>`;
  else if (LANG === "both") body =
    `<p class="readable" style="color:var(--fg2)">${esc(u.orig)}</p><p class="readable">${esc(u.txt)}</p>`;
  else body = `<p class="readable">${esc(u.txt)}</p>`;
  return `<div class="unit" id="u${u.n}">
    <div style="display:flex;gap:.6rem;align-items:baseline"><span class="cite">${esc(citeOf(w.id, s, u))}</span></div>
    ${label}${body}${note}</div>`;
}

/* ========================================================= CONCORDANCE */
function viewConcordance() {
  view.append(el(`<div>
    <div class="viewhead">
      <span class="tag">Cross-corpus search</span>
      <h1>Concordance</h1>
      <p class="lede">Keyword in context across every shipped text, each hit resolved to its
      citation. New modules join the search as they ship.</p>
    </div>
    <div class="toolbar">
      <input class="grow" id="q" type="search" placeholder="Search word or phrase …">
      <button class="primary" id="go">Search</button>
    </div>
    <div id="out"></div>
    <div class="card" style="margin-top:1.4rem"><span class="tag">Starting points</span>
      <p style="margin:.5rem 0 0">${["machine", "automaton", "consciousness", "habit",
        "association", "instinct", "learning", "satisfaction", "law", "soul"]
        .map(x => `<button class="chip" data-t="${x}">${x}</button>`).join(" ")}</p></div>
  </div>`));
  const out = view.querySelector("#out");
  const q = view.querySelector("#q");
  function run() {
    const term = q.value.trim();
    out.innerHTML = "";
    if (term.length < 3) { out.append(el(`<p class="fine">Type at least three characters.</p>`)); return; }
    const rx = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
    let hits = 0;
    for (const w of D.works.filter(x => x.status === "shipped")) {
      const t = D.texts[w.id];
      if (!t) continue;
      for (const s of t.sections) for (const u of s.units) {
        rx.lastIndex = 0;
        let src = u.txt, m = rx.exec(u.txt);
        if (!m && u.orig) { rx.lastIndex = 0; m = rx.exec(u.orig); src = u.orig; }
        if (!m) continue;
        hits++;
        if (hits > 200) break;
        const a = Math.max(0, m.index - 90), b = Math.min(src.length, m.index + term.length + 130);
        const ctx = (a > 0 ? "…" : "") + src.slice(a, b) + (b < src.length ? "…" : "");
        out.append(el(`<div class="unit">
          <div style="display:flex;gap:.6rem;align-items:baseline;flex-wrap:wrap">
            <a class="cite" href="#/works/${w.id}/${s.id}@${u.n}">${esc(citeOf(w.id, s, u))}</a>
            <span class="fine">${esc(w.autor)}</span></div>
          <p class="readable" style="font-size:.95rem">${esc(ctx).replace(rx, x => `<mark>${x}</mark>`)}</p>
        </div>`));
      }
    }
    out.prepend(el(`<p class="fine">${hits}${hits > 200 ? "+ (first 200 shown)" : ""} hits.</p>`));
  }
  view.querySelector("#go").onclick = run;
  q.addEventListener("keydown", e => { if (e.key === "Enter") run(); });
  view.querySelectorAll("[data-t]").forEach(b => b.onclick = () => { q.value = b.dataset.t; run(); });
}

/* =============================================================== WORKS */
function viewWorks(args) {
  if (args && args[0]) return workReader(args[0], args[1]);
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Four lines</span>
      <h1>The corpus, line by line</h1>
      <p class="lede">Eighteen modules in four lines, every one public domain in the United
      States (published through 1930). The threshold moves: works of 1931 join on 1 January
      2027, and the program says so where it matters.</p></div>
    <div id="lines"></div>
  </div>`));
  const box = view.querySelector("#lines");
  for (const k of Object.keys(LINIE)) {
    const ws = D.works.filter(w => w.linie === k);
    if (!ws.length) continue;
    const sec = el(`<div style="margin-bottom:2rem">
      <h2 style="margin:0 0 .2rem;color:${LCOLOR[k]}">${esc(LINIE[k])}</h2>
      <p class="fine" style="margin:0 0 .8rem;max-width:60rem">${esc(LLEDE[k])}</p>
      <div class="grid g2"></div></div>`);
    const grid = sec.querySelector(".grid");
    for (const w of ws) grid.append(workCard(w));
    box.append(sec);
  }
}

/* =============================================================== ATLAS */
/* Concept map: paragraph-level co-occurrence of the corpus's leading
   content terms (data/network.json, built by tools/build-network.py).
   Ported from the sibling apparatus: canvas force layout, cursor-centred
   zoom, pan, labels in screen space; colours read from the CSS variables
   so the atlas follows the theme (the view rebuilds on a theme switch). */
let NET = null;
async function viewAtlas() {
  if (!NET) NET = await fetch("data/network.json").then(r => r.json());
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Term network</span>
      <h1>Atlas</h1>
      <p class="lede">The ${NET.nodes.length} leading content terms of the shipped corpus, linked
      where they occur in the same paragraph. Colour is the line whose texts use the term most
      (<span style="color:var(--messen)">the measured mind</span> ·
      <span style="color:var(--lernen)">the learning animal</span> ·
      <span style="color:var(--automat)">the automaton debate</span> ·
      <span style="color:var(--labor)">the machine in the laboratory</span>); size is frequency.
      Click a term for its neighbours and citations; scroll or double-click to zoom — more labels
      appear as you go — and drag to pan. The map grows as modules ship.</p></div>
    <div class="toolbar">
      <label class="fine" for="dens">Density</label>
      <select id="dens">
        <option value="140">sparse</option>
        <option value="260" selected>medium</option>
        <option value="420">dense</option>
      </select>
      <button class="chip" id="zin" title="Zoom in">+</button>
      <button class="chip" id="zout" title="Zoom out">−</button>
      <button class="chip" id="zreset" title="Reset view">Reset</button>
      <span class="fine" id="atlasinfo"></span>
    </div>
    <div class="card" style="padding:0;overflow:hidden"><canvas id="cv" style="width:100%;display:block;cursor:grab"></canvas></div>
    <div id="sel"></div>
    <div class="card" style="margin-top:1.2rem"><span class="tag">Bridge terms</span>
      <p style="margin:.5rem 0 0" class="readable">Terms carried by three or more of the works —
      the shared vocabulary in which the lines argue with each other:
      ${NET.bridges.map(b => `<button class="chip" data-b="${esc(b)}">${esc(b)}</button>`).join(" ")}</p></div>
  </div>`));
  const cv = view.querySelector("#cv");
  const selBox = view.querySelector("#sel");
  const densSel = view.querySelector("#dens");
  const W = Math.min(Math.max(view.clientWidth || 900, 480), 980), H = Math.max(460, Math.round(W * 0.62));
  const dpr = window.devicePixelRatio || 1;
  cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + "px";
  const cx = cv.getContext("2d"); cx.scale(dpr, dpr);

  const nodes = NET.nodes.map(n => ({ ...n,
    x: W / 2 + (Math.random() - 0.5) * W * 0.8, y: H / 2 + (Math.random() - 0.5) * H * 0.8,
    vx: 0, vy: 0, r: 3 + Math.sqrt(n.f) * 0.9 }));
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  let edges = [], selected = null, tick = 0;

  function setDensity() {
    edges = NET.edges.slice(0, +densSel.value).map(e => ({ ...e, a: byId[e.s], b: byId[e.t] }))
      .filter(e => e.a && e.b);
    view.querySelector("#atlasinfo").textContent =
      `${nodes.length} terms · ${edges.length} links · from ${NET.n_units} paragraphs`;
    tick = 0;
  }
  setDensity();
  densSel.onchange = setDensity;

  function step() {
    for (const n of nodes) { n.fx = 0; n.fy = 0; }
    for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + 40;
      const f = 1400 / d2;
      const d = Math.sqrt(d2);
      dx /= d; dy /= d;
      a.fx += dx * f; a.fy += dy * f; b.fx -= dx * f; b.fy -= dy * f;
    }
    for (const e of edges) {
      let dx = e.b.x - e.a.x, dy = e.b.y - e.a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const want = 60 + 700 / (e.w + 4);
      const f = (d - want) * 0.004 * Math.min(e.w, 6);
      dx /= d; dy /= d;
      e.a.fx += dx * f * d * 0.02; e.a.fy += dy * f * d * 0.02;
      e.b.fx -= dx * f * d * 0.02; e.b.fy -= dy * f * d * 0.02;
    }
    for (const n of nodes) {
      n.fx += (W / 2 - n.x) * 0.004; n.fy += (H / 2 - n.y) * 0.004;
      n.vx = (n.vx + n.fx) * 0.82; n.vy = (n.vy + n.fy) * 0.82;
      n.x += n.vx; n.y += n.vy;
      n.x = Math.max(14, Math.min(W - 14, n.x)); n.y = Math.max(14, Math.min(H - 14, n.y));
    }
  }

  const _csv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const COLOR = { messen: _csv("--messen"), lernen: _csv("--lernen"),
                  automat: _csv("--automat"), labor: _csv("--labor") };
  const LIGHT = document.documentElement.getAttribute("data-theme") === "light";
  const EDGE_ON = LIGHT ? "rgba(31,110,102,.55)" : "rgba(90,169,160,.55)";
  const EDGE = LIGHT ? "rgba(90,100,115,.16)" : "rgba(160,160,180,.13)";
  const RING = LIGHT ? "#17222c" : "#fff";
  const LABEL = LIGHT ? "rgba(28,38,48,.92)" : "rgba(233,230,224,.92)";

  let Z = 1, OX = 0, OY = 0;
  const clampZ = z => Math.max(0.6, Math.min(8, z));
  function zoomAt(sx, sy, factor) {
    const nz = clampZ(Z * factor);
    OX = sx - (sx - OX) * (nz / Z);
    OY = sy - (sy - OY) * (nz / Z);
    Z = nz;
  }

  function draw() {
    cx.clearRect(0, 0, W, H);
    const neigh = new Set();
    if (selected) for (const e of edges) {
      if (e.a === selected) neigh.add(e.b);
      if (e.b === selected) neigh.add(e.a);
    }
    cx.save();
    cx.translate(OX, OY); cx.scale(Z, Z);
    for (const e of edges) {
      const on = selected && (e.a === selected || e.b === selected);
      cx.strokeStyle = on ? EDGE_ON : EDGE;
      cx.lineWidth = (on ? 1.4 : Math.min(1, 0.3 + e.w * 0.05)) / Z;
      cx.beginPath(); cx.moveTo(e.a.x, e.a.y); cx.lineTo(e.b.x, e.b.y); cx.stroke();
    }
    for (const n of nodes) {
      const dimmed = selected && n !== selected && !neigh.has(n);
      cx.globalAlpha = dimmed ? 0.25 : 1;
      cx.fillStyle = COLOR[n.linie];
      cx.beginPath(); cx.arc(n.x, n.y, n.r, 0, 7); cx.fill();
      if (n === selected) { cx.strokeStyle = RING; cx.lineWidth = 1.5 / Z; cx.stroke(); }
      cx.globalAlpha = 1;
    }
    cx.restore();
    for (const n of nodes) {
      const dimmed = selected && n !== selected && !neigh.has(n);
      if (dimmed) continue;
      if (!(n.f * Z > 25 || n === selected || neigh.has(n))) continue;
      const sx = n.x * Z + OX, sy = n.y * Z + OY - n.r * Z - 4;
      if (sx < -40 || sx > W + 40 || sy < -20 || sy > H + 14) continue;
      cx.fillStyle = LABEL;
      cx.font = (n === selected ? "600 " : "") + "11px system-ui, sans-serif";
      cx.textAlign = "center";
      cx.fillText(n.id, sx, sy);
    }
  }

  let raf;
  function loop() {
    if (tick < 260) { step(); tick++; }
    draw();
    raf = requestAnimationFrame(loop);
  }
  loop();

  const toScreen = ev => {
    const r = cv.getBoundingClientRect();
    return [(ev.clientX - r.left) * (W / r.width), (ev.clientY - r.top) * (H / r.height)];
  };
  function pick(sx, sy) {
    const x = (sx - OX) / Z, y = (sy - OY) / Z;
    let best = null, bd = Infinity;
    for (const n of nodes) {
      const d = (n.x - x) ** 2 + (n.y - y) ** 2;
      if (d < (n.r + 10 / Z) ** 2 && d < bd) { best = n; bd = d; }
    }
    return best;
  }
  let drag = null;
  cv.onmousedown = ev => {
    const [sx, sy] = toScreen(ev);
    drag = { sx, sy, ox: OX, oy: OY, moved: false };
    cv.style.cursor = "grabbing";
    ev.preventDefault();
  };
  const onMove = ev => {
    if (!drag) return;
    const [sx, sy] = toScreen(ev);
    if (Math.abs(sx - drag.sx) + Math.abs(sy - drag.sy) > 4) drag.moved = true;
    if (drag.moved) { OX = drag.ox + (sx - drag.sx); OY = drag.oy + (sy - drag.sy); }
  };
  const onUp = ev => {
    if (!drag) return;
    cv.style.cursor = "grab";
    const wasClick = !drag.moved;
    drag = null;
    if (wasClick) { const [sx, sy] = toScreen(ev); select(pick(sx, sy)); }
  };
  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);
  cv.addEventListener("wheel", ev => {
    ev.preventDefault();
    const [sx, sy] = toScreen(ev);
    zoomAt(sx, sy, Math.exp(-ev.deltaY * 0.0015));
  }, { passive: false });
  cv.ondblclick = ev => {
    ev.preventDefault();
    const [sx, sy] = toScreen(ev);
    zoomAt(sx, sy, 1.7);
  };
  view.querySelector("#zin").onclick = () => zoomAt(W / 2, H / 2, 1.4);
  view.querySelector("#zout").onclick = () => zoomAt(W / 2, H / 2, 1 / 1.4);
  view.querySelector("#zreset").onclick = () => { Z = 1; OX = 0; OY = 0; };

  atlasStop = () => {
    cancelAnimationFrame(raf);
    window.removeEventListener("mousemove", onMove);
    window.removeEventListener("mouseup", onUp);
  };

  function select(n) {
    selected = n;
    selBox.innerHTML = "";
    if (!n) return;
    const co = edges.filter(e => e.a === n || e.b === n)
      .map(e => ({ o: e.a === n ? e.b : e.a, c: e.c })).sort((a, b) => b.c - a.c).slice(0, 14);
    const wk = Object.entries(n.works).sort((a, b) => b[1] - a[1]);
    selBox.append(el(`<div class="card" style="margin-top:1.2rem">
      <div style="display:flex;gap:.8rem;align-items:baseline;flex-wrap:wrap">
        <h3 style="margin:0;color:${COLOR[n.linie]}">${esc(n.id)}</h3>
        <span class="fine">${n.f} paragraphs · in ${n.spread} of ${D.works.filter(w => w.status === "shipped").length} works</span></div>
      <p class="fine" style="margin:.4rem 0">${wk.map(([id, c]) => {
        const w = D.works.find(x => x.id === id);
        return `${esc(w ? w.kurz : id)}: ${c}`; }).join(" · ")}</p>
      <p style="margin:.4rem 0 0">${co.map(x =>
        `<button class="chip" data-b="${esc(x.o.id)}">${esc(x.o.id)} <span class="fine">${x.c}</span></button>`).join(" ")}</p>
      <p style="margin:.6rem 0 0">${n.cites.map(([wid, sid, un]) => {
        const t = D.texts[wid];
        const s = t && t.sections.find(x => x.id === sid);
        const u = s && s.units.find(x => x.n === un);
        return u ? `<a class="cite" href="#/works/${wid}/${sid}@${un}">${esc(citeOf(wid, s, u))}</a>` : "";
      }).join(" ")}</p>
    </div>`));
    selBox.querySelectorAll("[data-b]").forEach(b => b.onclick = () => select(byId[b.dataset.b]));
  }

  view.querySelectorAll("[data-b]").forEach(b => b.onclick = () => select(byId[b.dataset.b]));
}

/* ============================================================ TIMELINE */
/* Chronological view of the four lines, planned stations included — the
   registry pins its sources in advance, so the chart can show the whole
   program. Dates are editorial anchors: the year of the work, not of the
   author; translated modules sit at their originals, the carried
   public-domain translation named in the reader. Editorial matter, CC BY 4.0. */
const TIMELINE = [
  { id: "hartley", y: 1749, jahr: "1749" },
  { id: "bain", y: 1855, jahr: "1855" },
  { id: "fechner", y: 1860, jahr: "1860" },
  { id: "huxley", y: 1874, jahr: "1874" },
  { id: "james", y: 1879, jahr: "1879 / 1890" },
  { id: "galton", y: 1883, jahr: "1883" },
  { id: "ebbinghaus", y: 1885, jahr: "1885" },
  { id: "morgan", y: 1894, jahr: "1894" },
  { id: "thorndike", y: 1898, jahr: "1898 / 1911" },
  { id: "loeb", y: 1900, jahr: "1900" },
  { id: "spearman", y: 1904, jahr: "1904" },
  { id: "binet", y: 1905, jahr: "1905–11" },
  { id: "mcdougall", y: 1911, jahr: "1911" },
  { id: "watson", y: 1913, jahr: "1913" },
  { id: "koehler", y: 1917, jahr: "1917" },
  { id: "pavlov", y: 1927, jahr: "1927" },
  { id: "hull_aptitude", y: 1928, jahr: "1928" },
  { id: "hull_machines", y: 1929, jahr: "1929/30" },
];
const TL_ERAS = [
  { until: 1800, titel: "The eighteenth century" },
  { until: 1875, titel: "The mid-nineteenth century" },
  { until: 1900, titel: "The laboratory decades" },
  { until: 1917, titel: "Into the twentieth century" },
  { until: 9999, titel: "To the threshold — where the corpus ends" },
];
/* Crossings between stations. A crossing with an anchor is documented by a
   carried passage; the others are documented by the works themselves and
   gain their passage when the module ships. */
const TL_CROSS = [
  { from: "bain", to: "ebbinghaus", anchor: "#/works/ebbinghaus/chVII@3",
    titel: "Ebbinghaus dismisses Bain's one-idea-one-ganglion-cell theory (Mem. [63]) — the corpus arguing with itself across thirty years" },
  { from: "loeb", to: "mcdougall", anchor: "#/works/mcdougall/verhalten@4",
    titel: "McDougall answers the tropism doctrine, citing Loeb's Die Bedeutung der Tropismen (BM [4], note) — the learning line meets the automaton debate" },
  { from: "huxley", to: "james", anchor: "#/works/james/automata@1",
    titel: "James's reply opens by naming Huxley's Belfast address (AWA [1]) — “Are We Automata?” (1879) answers the automaton hypothesis of 1874" },
  { from: "pavlov", to: "hull_machines",
    titel: "Hull & Baernstein build “a mechanical parallel to the conditioned reflex” (1929) — the closing arc; the passage joins when the module ships" },
];

function viewTimeline() {
  const CX = { messen: 165, lernen: 380, automat: 595, labor: 810 };
  const W = 960, ROW = 44, ERAROW = 42, TOP = 46;
  const byId = Object.fromEntries(D.works.map(w => [w.id, w]));
  const rows = [...TIMELINE].sort((a, b) => a.y - b.y);

  /* lay out rows, inserting an era band whenever the era changes */
  let yy = TOP, eraIdx = -1;
  const bands = [], pos = {};
  for (const r of rows) {
    const e = TL_ERAS.findIndex(x => r.y < x.until);
    if (e !== eraIdx) { eraIdx = e; bands.push({ y: yy, titel: TL_ERAS[e].titel }); yy += ERAROW; }
    pos[r.id] = { x: CX[byId[r.id].linie], y: yy + ROW / 2, jahr: r.jahr };
    yy += ROW;
  }
  const H = yy + 16;

  /* per-line spines from first to last station */
  const spines = Object.keys(CX).map(l => {
    const ys = rows.filter(r => byId[r.id].linie === l).map(r => pos[r.id].y);
    return { l, y1: Math.min(...ys), y2: Math.max(...ys) };
  });

  const bandSvg = bands.map(b => `
    <text x="20" y="${b.y + 28}" font-family="var(--serif)" font-size="14" font-style="italic"
      fill="var(--fg3)">${esc(b.titel)}</text>
    <line x1="20" x2="${W - 20}" y1="${b.y + 36}" y2="${b.y + 36}" stroke="var(--line)"/>`).join("");

  const spineSvg = spines.map(s => `
    <line x1="${CX[s.l]}" x2="${CX[s.l]}" y1="${s.y1}" y2="${s.y2}"
      stroke="${LCOLOR[s.l]}" stroke-width="2" stroke-opacity=".35"/>`).join("");

  const crossSvg = TL_CROSS.map(c => {
    const a = pos[c.from], b = pos[c.to];
    const same = a.x === b.x, bow = same ? a.x - 78 : (a.x + b.x) / 2;
    const d = `M ${a.x} ${a.y} C ${bow} ${a.y + (b.y - a.y) * .25}, ${bow} ${a.y + (b.y - a.y) * .75}, ${b.x} ${b.y}`;
    return `<path d="${d}" fill="none" stroke="var(--fg3)" stroke-width="1.4"
      stroke-dasharray="4 4" stroke-opacity="${c.anchor ? ".75" : ".35"}"><title>${esc(c.titel)}</title></path>`;
  }).join("");

  const dotSvg = rows.map(r => {
    const w = byId[r.id], p = pos[r.id];
    const open = w.status === "shipped";
    const right = w.linie !== "labor";
    return `<a href="${open ? `#/works/${w.id}` : "#/works"}">
      <title>${esc(w.autor)} — ${esc(w.titel)}${open ? "" : " (planned)"}</title>
      <text x="96" y="${p.y + 4}" text-anchor="end" font-family="var(--mono)" font-size="11"
        fill="var(--fg3)">${esc(p.jahr)}</text>
      <circle cx="${p.x}" cy="${p.y}" r="5.5"
        fill="${open ? LCOLOR[w.linie] : "var(--bg)"}"
        stroke="${open ? "var(--bg)" : LCOLOR[w.linie]}" stroke-width="1.5"/>
      <text x="${p.x + (right ? 15 : -15)}" y="${p.y + 4.5}" text-anchor="${right ? "start" : "end"}"
        font-family="var(--serif)" font-size="13.5" fill="${open ? "var(--fg)" : "var(--fg3)"}"
        paint-order="stroke" stroke="var(--bg)" stroke-width="4" stroke-linejoin="round">
        ${esc(w.kurz)}</text>
    </a>`;
  }).join("");

  const headSvg = Object.entries(LINIE).map(([l, t]) => `
    <text x="${CX[l]}" y="24" text-anchor="middle" font-size="13" font-weight="600"
      fill="${LCOLOR[l]}">${esc(t)}</text>`).join("");

  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Chronology</span>
      <h1>Timeline — four lines toward the threshold</h1>
      <p class="lede">The corpus in time: eighteen stations from Hartley's vibrating
      associations of 1749 to the conditioning machine of 1929/30, four lines converging on
      the year the machines begin to learn. Filled dots are shipped modules and open their
      readers; hollow dots are planned, their sources already pinned on the
      <a href="#/works">works page</a>. Dashed arcs mark crossings between the stations.</p></div>
    <div class="tlwrap panel" style="padding:1rem .4rem">
      <svg class="tl" viewBox="0 0 ${W} ${H}" role="img"
        aria-label="Chronological chart of the corpus's eighteen modules in four lines">
        ${headSvg}${bandSvg}${spineSvg}${crossSvg}${dotSvg}
      </svg>
    </div>
    <div class="panel">
      <h2 style="margin-top:0">The crossings</h2>
      <ul style="margin:.4rem 0 0;padding-left:1.2rem">
        <li style="margin-bottom:.5rem"><a href="#/works/ebbinghaus/chVII@3">Bain → Ebbinghaus</a> —
          the carried passage: Ebbinghaus dismisses the “curious theory of Bain and others that
          each idea is lodged in a separate ganglion cell” (Mem. [63]).</li>
        <li style="margin-bottom:.5rem"><a href="#/works/mcdougall/verhalten@4">Loeb → McDougall</a> —
          the carried passage: McDougall's chapter on behaviour opens against the tropism
          doctrine, and his footnote names its source — Loeb's <em>Die Bedeutung der
          Tropismen</em> (BM [4]). The learning line and the automaton debate meet here.</li>
        <li style="margin-bottom:.5rem"><a href="#/works/james/automata@1">Huxley → James</a> — the
          carried passage: “Are We Automata?” (Mind, 1879) opens by naming the “Conscious-Automaton-theory
          to which Prof. Huxley gave such publicity in his Belfast address” (AWA [1]), and closes
          by hailing Huxley and Clifford as true prophets only on a condition no philosophy has
          met. James's Principles, in turn, quote Huxley's drilled veteran as the very image of
          habit (PP [55]).</li>
        <li><a href="#/works">Pavlov → Hull &amp; Baernstein</a> — the closing arc: a “mechanical
          parallel to the conditioned reflex” (Science, 1929) — psychologists building the machine
          that learns. The passage joins when the module ships.</li>
      </ul>
      <p class="fine" style="margin:.8rem 0 0">Dates are editorial anchors — the year of the work,
      not of the author. Translated modules sit at their originals (Ebbinghaus 1885, carried in the
      English of 1913; Köhler 1917, in Winter's English of 1925; Binet–Simon 1905–11, in Kite's
      English of 1916), the carried public-domain translation named in each reader. Anthology
      modules span years and are so labelled (James 1879/1890, Thorndike 1898/1911, the Hull
      machine papers 1929/30). The chart spaces stations by order, not by elapsed time — a linear
      scale would spend a third of the page on the century between Hartley and Bain.</p>
    </div>
  </div>`));
}

/* =============================================================== ESSAY */
/* Introductory essay on the corpus as a whole, and on the apparatus's own
   machine-assisted making. Editorial matter, CC BY 4.0. */
function viewEssay() {
  const C = (id, sec, n, label) => `<a class="cite" href="#/works/${id}/${sec}@${n}">${label}</a>`;
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Editorial</span>
      <h1>The mind made measurable</h1>
      <p class="lede">An introductory essay: what the four lines of this corpus argue when they
      are read together, why the collection ends in 1930 — and why an edition of the
      psychological prehistory of artificial intelligence, made with a machine that has
      learned, should say so on its own pages.</p></div>

    <div class="panel"><h2>Two prehistories</h2>
      <p class="readable">Artificial intelligence tells its origin story in philosophical
      quotations: Hobbes's reckoning, Leibniz's <em>calculemus</em>, Turing's question. A sister
      apparatus, <a href="https://philosophical-predecessors-of-ai.netlify.app"
      rel="noopener">Calculemus</a>, documents that line in full. But between the philosophers'
      wager — that reasoning is computation — and the engineers' machines lies a second
      prehistory, less quoted and more operational: the roughly one hundred and eighty years in
      which psychology made the mind <em>lawful</em>. Sensation was brought under a formula,
      memory under a curve, association under a stopwatch, intelligence under a scale; animals
      taught experimenters the laws of learning; and the question whether we ourselves are
      automata was argued at full strength a century before anyone asked it of software. When
      the first machine learning systems appeared, nearly every concept they needed — stimulus
      and response, reinforcement, learning curve, test, norm, level — was already on the shelf,
      manufactured by the authors collected here. This corpus assembles that second prehistory
      in citable, searchable editions, and this essay says what the assembly is meant to
      show.</p></div>

    <div class="panel"><h2>The measured mind</h2>
      <p class="readable">The first line runs from a formula to a scale. Fechner's
      <em>Elemente der Psychophysik</em> (1860) is its founding act: the claim that inner life
      obeys an equation, culminating in the Massformel ${C('fechner','formel',21,'EP [61]')}
      and its interpretation as nothing less than a general relation of dependence between
      mind and matter ${C('fechner','formel',37,'EP [77]')}. Ebbinghaus turned the wager into
      laboratory routine: nonsense syllables, the savings method
      ${C('ebbinghaus','chVI',9,'Mem. [49]')}, forgetting as a lawful function of time — the
      learning curve that machine learning still plots. Galton made statistics portable across
      persons: composite portraiture, the imagery questionnaire, association timed with a
      chronograph — and, in one of the corpus's most instructive passages, described a word
      association that worked "instantaneously and in a meaningless way, just as a machine
      might act" ${C('galton','psychometric',13,'IHF [65]')}. Spearman extracted from the
      correlations a single common function, <em>g</em>
      ${C('spearman','concl',5,'GI [41]')}. And Binet built the instrument: a definition of
      intelligence as judgment ${C('binet','programm',20,'DIC [20]')}, thirty graded tasks
      ${C('binet','tests',7,'DIC [29]')}, age norms, a scoring rubric, and a computable mental
      level — with the warning, carried here in full, that the method is "not an automatic
      method comparable to a weighing machine"
      ${C('binet','niveau',1,'DIC [69]')}. Anyone who has assembled an evaluation suite for a
      language model has re-enacted this line, usually without knowing it: graded tasks, norms,
      a rubric, a leaderboard — and, mostly forgotten, Binet's warning.</p></div>

    <div class="panel"><h2>The learning animal, and its discipline</h2>
      <p class="readable">The second line domesticates learning itself. Its centrepiece is
      Thorndike: cats in puzzle boxes, the gradual stamping-in of the successful movement
      ${C('thorndike','method',6,'AI, ch. II [20]')}, and the Law of Effect stated as law
      ${C('thorndike','laws',13,'AI, ch. VI [13]')} — the sentence reinforcement learning
      cites as its origin, the corpus's most direct wire into the present. Around it stand the
      ancestors and the correctives: Hartley's associations before it, and Bain, who in 1855
      already had the random movement that happens to relieve a pain "clutched in the embrace
      of the feeling" and kept going ${C('bain','wille',16,'SI [16]')} — the law of effect
      forty years early; Köhler's insight experiments as the standing counter-evidence within. Beneath it
      lies Loeb's floor. The moth, he insisted, "does not fly into the flame out of
      'curiosity'", nor is it attracted by the light; "it is only oriented by it"
      ${C('loeb','instinkt',6,'CPB [29]')}, and to posit a "flying-into-the-flame centre" in
      its nervous system is to explain a behaviour by naming a module after it
      ${C('loeb','instinkt',7,'CPB [30]')}. Loeb then drew the line the whole corpus is built
      around: associative memory, a mechanism he says "can be imitated by machines like the
      phonograph" ${C('loeb','kriterium',1,'CPB [32]')}, is the criterion of mind, and "if an
      animal can learn … it must possess associative memory"
      ${C('loeb','kriterium',8,'CPB [39]')}. Mind begins, for Loeb, where learning begins —
      which is exactly where this collection stops.</p>
      <p class="readable">Beside Thorndike, Pavlov turned learning into procedure. The
      hemispheres' fundamental function is "signalization", reacting to "innumerable stimuli
      of interchangeable signification" ${C('pavlov','lecture1',32,'CR [32]')}; the difference
      between an inborn and an acquired reflex is only that of a private line and a
      connection made at the central exchange ${C('pavlov','lecture2',18,'CR [50]')}; and a
      new "conditioned" reflex ${C('pavlov','lecture2',19,'CR [51]')}, given the right order
      of stimuli in a sound-proof chamber, is "infallibly obtained"
      ${C('pavlov','lecture2',32,'CR [64]')}. Watson drew the programme from it in 1913:
      psychology as "a purely objective experimental branch of natural science" whose goal
      is "the prediction and control of behavior", with "no dividing line between man and
      brute" ${C('watson','text',1,'PBV [1]')}, and consciousness discarded as an object of
      study ${C('watson','text',8,'PBV [8]')}. It is the psychology most ready to be
      mechanised — and the one the automaton debate had warned against. Over the whole line
      presides its conscience: Morgan's canon — "in no case may we interpret an action as the
      outcome of the exercise of a higher psychical faculty, if it can be interpreted as the
      outcome of the exercise of one which stands lower in the psychological scale"
      ${C('morgan','kanon',2,'CP [26]')}. Morgan reasoned from a chronometer forced to read
      all other clockwork in terms of its own works; every present-day argument about whether
      a model "understands" replays his chapter, and mostly less carefully.</p></div>

    <div class="panel"><h2>The automaton debate</h2>
      <p class="readable">The third line shows that the debate about machine minds did not
      wait for machines. Huxley's address of 1874 states the automaton theory at full
      strength — brutes, and by extension we ourselves, as conscious automata
      ${C('huxley','text',81,'Aut. [81]')} — and James's "Are We Automata?" (1879), the great
      reply, names Huxley's address in its first sentence ${C('james','automata',1,'AWA [1]')}
      and answers it with Darwin: consciousness has evolved like every organ that has a use,
      and its use is to load the dice of an unstable brain — "a fighter as well as a
      standard-bearer" ${C('james','automata',20,'AWA [20]')}, not an impotently paralytic
      spectator of the game ${C('james','automata',47,'AWA [47]')}. McDougall
      mounts the last full-dress defence of the soul, and he fights on the mechanists' own
      ground — behaviour. Against the tropism doctrine he sets persistence with varied
      effort: "the clock-work stops without a struggle if you thrust a spoke into its wheel"
      ${C('mcdougall','verhalten',6,'BM [6]')}; and against every stimulus-response scheme
      his telegram — "Your son is dead" — whose effect no physics of black marks on paper
      explains, since the one link common to all its possible forms is meaning
      ${C('mcdougall','verhalten',25,'BM [25]')}. The nineteenth century, in other words,
      rehearsed the entire space of positions — eliminativist, functionalist, animist — about
      its own minds, before a single relay clicked. The corpus carries the debate so that its
      re-enactments about software can at least know they are re-enactments.</p></div>

    <div class="panel"><h2>The threshold</h2>
      <p class="readable">The fourth line is the shortest and the hinge: Hull's
      aptitude-forecasting machinery, and then, in 1929 and 1930, Hull and Baernstein building
      an electro-chemical "mechanical parallel to the conditioned reflex" — psychologists
      constructing a device that learns, and arguing that knowledge and purpose are habit
      mechanisms a machine could have. There the corpus stops, deliberately. The boundary is a
      rights fact — works published through 1930 are in the United States public domain, while
      Craik, McCulloch &amp; Pitts, Wiener and Turing remain in copyright and are named in the
      <a href="#/coda">coda</a> — but the rights fact coincides with the intellectual
      watershed: the corpus ends where the machines begin to learn. The threshold moves; works
      of 1931 join on 1 January 2027.</p></div>

    <div class="panel"><h2>What the corpus knows about the present</h2>
      <p class="readable">Read together, the lines hand the present four mirrors. The
      benchmark has an ancestor, and the ancestor came with operating instructions we have
      dropped: Binet's insistence that results "have no value if deprived of all comment"
      ${C('binet','niveau',1,'DIC [69]')}. Reinforcement has an ancestor, and the ancestor's
      finest observers already knew the difference between performing and understanding —
      and between explaining a behaviour and merely naming a centre for it
      ${C('loeb','instinkt',7,'CPB [30]')}.
      Anthropomorphism has a discipline, older than the machines by a century
      ${C('morgan','kanon',2,'CP [26]')}. And measurement has a politics: the same Galton who
      built the methods coined "eugenics" on page 24 of the same book
      ${C('galton','prog',2,'IHF [2]')} — carried here in his own words, stated, not passed
      over — while his criminal composites quietly delivered the corpus's great negative
      result: averaged, the faces of convicts dissolve into "the common humanity of a low
      type", with "no villainy written on them" ${C('galton','composite',17,'IHF [19]')}. A
      century before face-classification startups, the founding experiment had already
      failed, and said so in print.</p></div>

    <div class="panel"><h2>Distant reading, distant writing</h2>
      <p class="readable">One more thing should be said about this apparatus, and it belongs
      in the essay rather than the small print. Two decades ago Franco Moretti proposed
      <em>distant reading</em>: understanding literature at scales no reader can reach by
      reading — graphs, maps, trees, models in place of pages. This corpus is built by the
      inverse operation, for which <em>distant writing</em> is the honest name: the editions,
      emendations, translations and apparatus here were produced in sustained working sessions
      with a large language model, under an editor who directed every selection, verified the
      worst passages against the page images, and answers for every printed word. Distance, in
      Moretti's sense, was a condition of knowledge; here it is a condition of production —
      and it changes what an edition owes its reader. Hannes Bajohr has described the coming
      condition as "post-artificial": texts whose human or machine provenance can no longer be
      presumed and soon will not be asked. A scholarly edition cannot want that. So this one
      keeps its making on record — the <a href="#/method">method page</a> says how the work
      was done, the build scripts in the repository show it being done, and the paragraph
      grids make every claim checkable against the print.</p>
      <p class="readable">There is also a stranger symmetry, and it is the real reason this
      section exists. The machine that helped edit this corpus is a descendant of its
      contents: trained by gradient methods that descend from the very laws of effect and
      exercise Thorndike stated ${C('thorndike','laws',13,'AI, ch. VI [13]')}, evaluated by
      batteries that descend from Binet's thirty tasks
      ${C('binet','tests',7,'DIC [29]')}, and discussed daily in terms Morgan's canon was
      built to discipline ${C('morgan','kanon',2,'CP [26]')}. A corpus that ends where the
      machines begin to learn, edited with a machine that has learned, is not a paradox to be
      hidden but the exhibit's last vitrine: the prehistory documented here runs, without a
      break, into the tool that helped document it.</p></div>

    <div class="panel"><h2>How to read this corpus</h2>
      <p class="readable">These are selections chosen for an argument, not a library: every
      module says what it carries, what it omits, and why; the registry pins each source
      digitisation before a line of it is carried, so the plan itself is checkable; and every
      paragraph carries a stable citation — the codes used in this essay resolve, on click, to
      the passage in its module. Where the texts are ugly — Galton's eugenics, Morgan's
      colonial hierarchies of "civilised" and "primitive" — they are carried as printed and
      named as what they are, because a prehistory of measurement that hid the politics of
      measurement would document nothing. The <a href="#/works">works page</a> holds the
      program; the <a href="#/timeline">timeline</a>, the <a href="#/atlas">atlas</a> and the
      <a href="#/concordance">concordance</a> hold the corpus's own cross-references. The rest
      is the texts' affair.</p>
      <p class="fine">Editorial matter, CC BY 4.0. References: Franco Moretti, "Conjectures on
      World Literature" (2000) and <em>Distant Reading</em> (2013); Hannes Bajohr,
      "Artifizielle und postartifizielle Texte" (2023). The corpus's own sources are given
      module by module in <span class="mono">SOURCES.md</span>.</p></div>
  </div>`));
}

/* ================================================================ CODA */
/* Editorial closing note. Editorial matter, CC BY 4.0. */
function viewCoda() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Editorial</span>
      <h1>After 1930 — what this corpus cannot contain</h1>
      <p class="lede">The boundary of this apparatus is a rights fact, and it falls at an uncanny
      moment: the corpus must end at the very point where its story hands over.</p></div>
    <div class="panel"><h2>The locked successors</h2>
      <p class="readable">Kenneth Craik's <em>The Nature of Explanation</em> (1943), with its
      models in the head; McCulloch and Pitts's logical calculus of nervous activity (1943);
      Hull's own <em>Principles of Behavior</em> (1943), the axiomatised learning theory his
      machines pointed toward; Wiener's <em>Cybernetics</em> (1948); Turing's imitation game
      (1950) — a test of machine intelligence that is, at bottom, a psychological instrument.
      All remain in copyright in the United States and are named here rather than carried.</p>
      <p class="readable">One case is stranger: Freud's <em>Entwurf einer Psychologie</em>, the
      neurological machine-model of the mind, was written in 1895 — squarely inside this
      corpus's period — but published only in 1950. Written before the threshold, locked
      behind it: the apparatus can point at it, and does.</p>
      <p class="readable">The threshold itself moves. Works published in 1931 enter the United
      States public domain on 1 January 2027 — the second Baernstein–Hull machine paper among
      them — and the program will take them up as they arrive.</p></div>
    <div class="panel"><h2>Stated exclusions</h2>
      <p class="readable">This is a corpus about the mind become mechanism, measure and law of
      learning — not a history of psychology entire. Psychoanalysis is represented only by the
      locked <em>Entwurf</em> above; phenomenology and the Geisteswissenschaften debate are the
      philosophical sibling's territory where they are anyone's; and the eugenic uses of the
      measurement line (Galton and after) are stated in the modules that carry its texts, not
      passed over.</p></div>
  </div>`));
}

/* ============================================================== METHOD */
function viewMethod() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Transparency</span>
      <h1>Method, sources and limits</h1>
      <p class="lede">What this site is, where its texts will come from, and what its editions
      will and will not claim.</p></div>

    <div class="panel"><h2>The rights position</h2>
      <p class="readable">Everything this apparatus ships will be in the United States public
      domain, and the site is operated from the United States, whose rules govern its edition
      choices. The original works qualify by publication date: everything published through 1930
      is public domain, which carries the corpus from Hartley (1749) to Hull's machine papers
      (1929/30) — the 1930 paper entered the public domain on 1 January 2026. Where a
      public-domain English translation exists it will be used and named (Ebbinghaus 1913,
      Binet–Simon in Kite's translation of 1916, Pavlov in Anrep's of 1927, Köhler in Winter's
      of 1925); where none exists — notably Fechner, whose English translation of 1966 is in
      copyright and will not be consulted — this site will supply its own working translation,
      made directly from the original and dedicated to the public domain. Working translations
      are labelled as unofficial throughout: cite the original.</p>
      <p class="readable">The boundary of the site is itself a rights fact: the founding texts
      of cybernetics and machine intelligence — Craik 1943, McCulloch &amp; Pitts 1943, Hull's
      Principles 1943, Wiener 1948, Turing 1950 — remain in copyright. The apparatus therefore
      ends, deliberately, at the threshold: the last texts it can carry in full are those in
      which psychologists first built a machine that learns.</p></div>

    <div class="panel"><h2>The editions to come</h2>
      <p class="readable">Each module follows the discipline proven on the sibling sites
      (<a href="https://philosophical-predecessors-of-ai.netlify.app" rel="noopener">Calculemus</a>,
      <a href="https://ignatian-research.netlify.app" rel="noopener">Ignatiana</a>): a named
      public-domain digitisation, OCR emended by hand against the sense and disclosed, a stable
      paragraph-level citation grid, and per-module notes on what was selected and why. The
      registry on the <a href="#/works">works page</a> pins each module's source digitisation
      now, before a line of it is carried, so that the plan itself is checkable. As modules
      ship, the apparatus gains the sibling machinery: readers with language toggles, a
      cross-corpus concordance, a concept atlas, a chronological timeline, plates from the
      printings, and a citation-bound dialogue.</p></div>

    <div class="panel"><h2>Limits, stated in advance</h2>
      <p class="readable">These will be selections chosen for an argument — how the mind was
      made lawful, measurable and mechanisable — not complete works; each module will state its
      cut. The corpus is Anglo-German-French by the accident of where experimental psychology
      was written; the sibling site carries the non-Western roots of the computational idea, and
      the two cross-reference. The measurement line has a history that includes eugenics: the
      modules that carry Galton and the testing tradition state it. And the apparatus is built
      in sustained working sessions with a large language model, under an editor who takes
      responsibility for every selection, emendation and working translation — the repository's
      commit history records the making, stage by stage.</p></div>
  </div>`));
}

/* ===================================================== PRIVACY / IMPRINT */
function viewPrivacy() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Privacy</span><h1>Privacy</h1></div>
    <div class="panel"><p class="readable">This is a static site. It sets no cookies, runs no
      analytics, loads no third-party scripts or fonts, and transmits nothing you type — there
      is nothing to type. The only thing stored is your theme choice (dark or daylight), kept
      in your own browser's localStorage and sent nowhere. Server logs are those of the hosting
      provider (Netlify), governed by its privacy policy. When the citation-bound dialogue
      ships, this page will state exactly what that one optional function transmits, before it
      is enabled.</p></div>
  </div>`));
}
function viewImprint() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Legal notice</span><h1>Legal notice</h1></div>
    <div class="panel"><p class="readable">Site operated by Dr. Pantaleon Fassbender,
      16751 NE 5th Street, Williston, FL 32696, United States ·
      pantaleonfassbender@googlemail.com. A non-commercial research apparatus. Operated from
      the United States; no offering is directed at the European Union in the sense of
      Art. 3(2) GDPR. Licensing: source code MIT; editorial matter CC BY 4.0; editions,
      working translations and derived data CC0 — see LICENSES.md in the repository.</p></div>
  </div>`));
}

/* ================================================================ BOOT */
Object.assign(ROUTES, {
  overview: viewOverview, works: viewWorks, coda: viewCoda,
  concordance: viewConcordance, atlas: viewAtlas, timeline: viewTimeline,
  essay: viewEssay,
  method: viewMethod, privacy: viewPrivacy, imprint: viewImprint,
});

async function boot() {
  D.works = await fetch("data/works.json").then(r => r.json());
  D.plates = await fetch("data/plates.json").then(r => r.json()).catch(() => ({}));
  const shipped = D.works.filter(w => w.status === "shipped" && w.datei);
  const res = await Promise.all(shipped.map(w => fetch(`data/${w.datei}.json`).then(r => r.json())));
  shipped.forEach((w, i) => D.texts[w.id] = res[i]);
  window.addEventListener("hashchange", route);
  const syncTheme = () => {
    document.getElementById("themeLabel").textContent =
      document.documentElement.getAttribute("data-theme") === "light" ? "Dark room" : "Daylight";
  };
  document.getElementById("themeBtn").onclick = () => {
    const light = document.documentElement.getAttribute("data-theme") === "light";
    if (light) document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", "light");
    try { localStorage.setItem("theme", light ? "dark" : "light"); } catch (e) {}
    syncTheme(); route();
  };
  syncTheme();
  route();
}
boot();
