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
};
const citeOf = (workId, sec, u) => (CITE[workId] || ((s, x) => `[${x.n}]`))(sec, u);

const ROUTES = {};
function route() {
  const h = (location.hash || "#/overview").slice(2).split("/");
  const name = h[0] || "overview";
  document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("active", a.dataset.v === name));
  view.innerHTML = ""; window.scrollTo(0, 0);
  (ROUTES[name] || viewOverview)(h.slice(1));
}

/* ============================================================ OVERVIEW */
function viewOverview() {
  view.append(el(`<div>
    <div class="viewhead">
      <span class="tag">Research apparatus · in construction</span>
      <h1>Before the machines could learn, psychologists made the mind lawful</h1>
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
    <div id="body">${s.units.map(u => unitHtml(w, s, u)).join("")}</div>
    <p class="fine">${esc(t.quelle)} ${esc(t.hinweis || "")}</p>
  </div>`));
  const anchor = (location.hash.split("@")[1] || "");
  if (anchor) setTimeout(() =>
    document.getElementById("u" + anchor)?.scrollIntoView({ behavior: "instant", block: "start" }), 0);
}

function unitHtml(w, s, u) {
  const label = u.label ? `<p class="ulabel">${esc(u.label)}</p>` : "";
  const note = u.note ? `<p class="fine" style="color:var(--acc)">${esc(u.note)}</p>` : "";
  return `<div class="unit" id="u${u.n}">
    <div style="display:flex;gap:.6rem;align-items:baseline"><span class="cite">${esc(citeOf(w.id, s, u))}</span></div>
    ${label}<p class="readable">${esc(u.txt)}</p>${note}</div>`;
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
        const m = rx.exec(u.txt);
        if (!m) continue;
        hits++;
        if (hits > 200) break;
        const a = Math.max(0, m.index - 90), b = Math.min(u.txt.length, m.index + term.length + 130);
        const ctx = (a > 0 ? "…" : "") + u.txt.slice(a, b) + (b < u.txt.length ? "…" : "");
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
  concordance: viewConcordance,
  method: viewMethod, privacy: viewPrivacy, imprint: viewImprint,
});

async function boot() {
  D.works = await fetch("data/works.json").then(r => r.json());
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
