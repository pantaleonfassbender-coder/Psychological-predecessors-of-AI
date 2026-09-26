# -*- coding: utf-8 -*-
# Build data/spearman.json — Spearman, "'General Intelligence,'
# Objectively Determined and Measured", American Journal of Psychology 15
# (1904), pp. 201-292. Source: the original printing via JSTOR Early
# Journal Content, Internet Archive jstor-1412107 (1412107_djvu.txt,
# downloaded on demand into tools/.cache/). Three selections:
#   intro   — Chapter I complete (Signs of Weakness in Experimental
#             Psychology; the programme of correlational psychology);
#   unity   — Chapter V, sections 4-5 complete: the Universal Unity of
#             the Intellective Function and the Hierarchy of the
#             Intelligences (the correlation tables themselves are not
#             reproduced and are said so);
#   concl   — Chapter V, section 8: the Summary of Conclusions complete.
# Running heads, page numbers and the bottom-of-page footnotes dropped;
# rows of tabular figures filtered; OCR emended against the sense.
# Usage: python tools/build-spearman.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'spearman.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/jstor-1412107/1412107_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

def digit_ratio(s):
    core = re.sub(r'\s', '', s)
    if not core: return 0
    return sum(c.isdigit() or c in '.,-—()' for c in core) / len(core)

HEAD = re.compile(r"^\s*(\d{1,3}\s+)?(SPEARMAN\s*:?|GENERAL\s+INTELLIGENCE.*|"
                  r"['\"]*\s*GENERAL\s+INTELLIGENCE.*|Digitized by.*)\s*(\d{1,3})?\s*$", re.I)
NOISE = re.compile(r'^\s*(\d{1,3}|[ivxlIVXL]+\.?|[A-Za-z])\s*$')

def harvest(a, b):
    paras, buf = [], []
    for raw in lines[a - 1:b]:
        s = raw.strip()
        if HEAD.match(s) or NOISE.match(s): continue
        if digit_ratio(s) > .55 and len(s) > 3: continue   # table rows
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    out = []
    for p in paras:
        if re.match(r'^\d [^.]', p): continue              # page-bottom footnote
        p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
        p = re.sub(r'\s+', ' ', p).strip()
        if len(p) > 2: out.append(p)
    merged = []
    for p in out:
        p = re.sub(r'^(\d)\.\.', r'\1.', p)
        p = re.sub(r'^j\.\s+', '3. ', p)          # OCR: '3.' read as 'j.'
        p = p.replace('The "Identities" of Science.', 'The Identities of Science')
        headish = bool(SECHEAD.match(p)) or p.lower().startswith('chapter')
        if merged and not headish and not SECHEAD.match(merged[-1]) and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,]$', merged[-1]) and not p[:1] in '"\'')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return [m for m in merged if not m.lower().startswith('chapter i')]

SECHEAD = re.compile(r'^(\d)\s*\.?\s+([A-Z][\w\s,\'-]{4,70}[a-z])\s*\.?$')

def units_of(paras, heads):
    """Turn numbered in-chapter section headings into labels."""
    us, label = [], None
    for p in paras:
        m = SECHEAD.match(p)
        if m and int(m.group(1)) in heads:
            label = f"§ {m.group(1)}. {m.group(2).strip()}"
            continue
        u = {'txt': p}
        if label: u['label'] = label; label = None
        us.append(u)
    return us

FIXES = [
    (r'I,eip', 'Leip'), (r'\bI,', 'L'), (r"' '", "'"),
    (r'\bfimction\b', 'function'), (r'\bfimctions\b', 'functions'),
    (r'\bcommou\b', 'common'), (r'\bantomatically\b', 'automatically'),
    (r'\bmore- over\b', 'moreover'),
]

def emend(us):
    for u in us:
        for pat, rep in FIXES:
            u['txt'] = re.sub(pat, rep, u['txt'])
        u['txt'] = re.sub(r'\s+', ' ', u['txt']).strip()
    return us

intro = emend(units_of(harvest(159, 368), {1, 2, 3, 4}))
unity = emend(units_of(harvest(4192, 4674), {4, 5}))
concl = emend(units_of(harvest(5080, 5181), {8}))

# the Hierarchy table's shredded rows are dropped; its place is marked
TABLE = re.compile(r'^(Activity\.|Classics,|Common Sense,|English,|Pitch Dis\.|Music,|Weight Dis\.)')
kept = []
for u in unity:
    if TABLE.match(u['txt']):
        if kept and not kept[-1].get('note'):
            kept[-1]['note'] = ('The hierarchy table that follows in the print — the specific '
                                'activities in their constant order of correlation — is not '
                                'reproduced.')
        continue
    kept.append(u)
unity = kept

def numbered(us, k0=1):
    out = []
    for i, u in enumerate(us):
        v = {'n': i + 1, 'k': k0 + i, 'txt': u['txt']}
        if u.get('label'): v['label'] = u['label']
        if u.get('note'): v['note'] = u['note']
        out.append(v)
    return out

u_intro = numbered(intro)
u_unity = numbered(unity, 1 + len(intro))
u_concl = numbered(concl, 1 + len(intro) + len(unity))

out = {
 'id': 'spearman',
 'autor': 'Charles Spearman',
 'titel': '“General Intelligence,” Objectively Determined and Measured (1904) — selections',
 'jahr': 1904,
 'zitierweise': 'GI [k]',
 'quelle': ("Selections from the American Journal of Psychology 15 (1904), pp. "
            "201–292, in the original printing via JSTOR Early Journal Content "
            "(Internet Archive jstor-1412107), OCR emended by hand against the "
            "sense. Carried complete: Chapter I (the programme), Chapter V "
            "sections 4–5 (the Universal Unity of the Intellective Function and "
            "the Hierarchy of the Intelligences — the correlation tables "
            "themselves are not reproduced), and Chapter V section 8, the "
            "Summary of Conclusions. Paragraph numbering k runs across the "
            "three selections, so a citation 'GI [k]' is unique; the paper's "
            "own section headings are carried as labels. The page-bottom "
            "footnotes are not carried. Public domain."),
 'hinweis': ("Intelligence becomes a factor: correlation corrected for "
             "attenuation, the hierarchy of the specific intelligences, and "
             "the conclusion that all branches of intellectual activity share "
             "one fundamental function — the mathematics of ‘how "
             "intelligent?’, the question later asked of machines."),
 'sections': [
   {'id': 'intro', 'titel': 'Ch. I — Introductory (complete)', 'units': u_intro},
   {'id': 'unity', 'titel': 'Ch. V, §§ 4–5 — Universal unity and the hierarchy', 'units': u_unity},
   {'id': 'concl', 'titel': 'Ch. V, § 8 — Summary of conclusions', 'units': u_concl},
 ],
}

path = os.path.join(REPO, 'data', 'spearman.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(intro), len(unity), len(concl)], 'units')
for us in (u_intro, u_unity, u_concl):
    print('  >', us[0]['txt'][:95])
    print('  <', us[-1]['txt'][:95])
