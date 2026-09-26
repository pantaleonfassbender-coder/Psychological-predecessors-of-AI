# -*- coding: utf-8 -*-
# Build data/ebbinghaus.json — Ebbinghaus, Memory: A Contribution to
# Experimental Psychology (1885), in the public-domain English of Ruger &
# Bussenius (New York: Teachers College, 1913). Source: Internet Archive
# memorycontributi00ebbiuoft (djvu, downloaded on demand into
# tools/.cache/). Five chapter selections, the sections carried complete:
#   chI   — ch. I  §§ 1-3   (memory in its effects and dependence);
#   chII  — ch. II §§ 4-5   (the method of natural science; numerical
#                            measurement introduced for memory);
#   chIII — ch. III §§ 11-12 (the nonsense syllables and their advantages);
#   chVI  — ch. VI §§ 22-23 (retention as a function of the number of
#                            repetitions: the savings method at work);
#   chVII — ch. VII §§ 26-27 and 29-30 (retention and obliviscence as a
#                            function of time: the forgetting curve; § 28,
#                            which is the results tables themselves, is
#                            omitted and named as the module's next step).
# The print's section headings become labels; its tables and formula
# displays are not reproduced (marked by notes where they fall); running
# heads and page numbers dropped; OCR emended against the sense.
# Usage: python tools/build-ebbinghaus.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'ebbinghaus.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/memorycontributi00ebbiuoft/'
        'memorycontributi00ebbiuoft_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

def digit_ratio(s):
    core = re.sub(r'\s', '', s)
    if not core: return 0
    return sum(c.isdigit() or c in '.,-—()%/=' for c in core) / len(core)

HEAD = re.compile(r'^\s*(\d{1,3}\s+)?(MEMORY|Memory|CHAPTER\s+\S+|'
                  r'A CONTRIBUTION TO EXPERIMENTAL PSYCHOLOGY.*|Digitized by.*|'
                  r'(Our Knowledge|The Possibility|The Method of Investigation|'
                  r'The Utility|Rapidity of Learning|Retention (as|and))\b.{0,45})\s*(\d{1,3})?\s*$')
NOISE = re.compile(r'^\s*(\d{1,3}|[ivxlIVXL]+\.?|[A-Za-z])\s*$')
SECLINE = re.compile(r'^Section\s+\S{1,4}\s*\.?\s*(.*)$')

def harvest(a, b, secnums):
    """Paragraphs from lines a..b; 'Section' headings become labels,
    renumbered in order from secnums (the OCR mangles the numerals)."""
    paras, buf = [], []
    for raw in lines[a - 1:b]:
        s = re.sub(r'\s+', ' ', raw).strip()
        if HEAD.match(s) or NOISE.match(s): continue
        if digit_ratio(s) > .5 and len(s) > 3:
            s = '\u0000TABLE'          # keep a marker so a note can be set
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(s)
    if buf: paras.append(' '.join(buf))

    out, labels_seen = [], 0
    secnums = list(secnums)
    for p in paras:
        m = SECLINE.match(p)
        if m and labels_seen < len(secnums):
            title = m.group(1).strip().rstrip('.')
            title = re.sub(r'\s+', ' ', title)
            out.append({'_label': f"§ {secnums[labels_seen]}. {title}"})
            labels_seen += 1
            continue
        out.append({'txt': p})
    assert labels_seen == len(secnums), (labels_seen, secnums)

    units, label = [], None
    for x in out:
        if '_label' in x: label = x['_label']; continue
        p = x['txt']
        p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
        table = '\u0000TABLE' in p
        p = p.replace('\u0000TABLE', ' ')
        p = re.sub(r'\s+', ' ', p).strip()
        alnum = sum(c.isalpha() for c in p) / max(1, len(p))
        caps = sum(c.isupper() for c in p if c.isalpha()) / max(1, sum(c.isalpha() for c in p))
        if (len(p) < 3 or p.startswith('*') or alnum < .55 or
                (len(p) < 34 and not re.search(r'[.!?;:]$', p)) or
                (caps > .8 and len(p) < 70)):
            if (table or len(p) < 34) and units and not units[-1].get('note'):
                units[-1]['note'] = TABNOTE
            continue
        u = {'txt': p}
        if table: u['note'] = TABNOTE
        if label: u['label'] = label; label = None
        units.append(u)
    merged = []
    for u in units:
        if merged and not u.get('label') and (
                re.match(r'^[a-z\)\],;:]', u['txt']) or
                (re.search(r'[a-z,]$', merged[-1]['txt']) and not u['txt'][:1] in '"\'')):
            merged[-1]['txt'] += ' ' + u['txt']
            if u.get('note'): merged[-1]['note'] = u['note']
        else:
            merged.append(u)
    return merged

TABNOTE = ('A table or formula display of the print falls in this paragraph '
           'and is not reproduced.')

FIXES = [
    ('�', '—'), (r'\s*\^\s*', ' '),
    (r'\btbe\b', 'the'), (r'\bTbe\b', 'The'), (r'\bbave\b', 'have'),
    (r'\bwbich\b', 'which'), (r'\bwitb\b', 'with'),
    (r'\bIt Is\b', 'It is'), (r' ,', ','), (r' \.', '.'),
]
def emend(us):
    for u in us:
        for pat, rep in FIXES:
            u['txt'] = re.sub(pat, rep, u['txt'])
        u['txt'] = re.sub(r'\s+', ' ', u['txt']).strip()
    return us

chI = emend(harvest(267, 518, [1, 2, 3]))
chII = emend(harvest(519, 732, [4, 5]))
chIII = emend(harvest(1225, 1338, [11, 12]))
chVI = emend(harvest(3267, 3864, [22, 23]))
chVII = emend(harvest(4118, 4369, [26, 27]) + harvest(6123, 6490, [29, 30]))

groups = [('chI', 'Ch. I — Memory in its effects and dependence (§§ 1–3)', chI),
          ('chII', 'Ch. II — Measurement enters (§§ 4–5)', chII),
          ('chIII', 'Ch. III — The nonsense syllables (§§ 11–12)', chIII),
          ('chVI', 'Ch. VI — Retention and repetitions: the savings method (§§ 22–23)', chVI),
          ('chVII', 'Ch. VII — Retention and obliviscence as a function of time (§§ 26–30)', chVII)]

k0, sections = 1, []
for sid, titel, us in groups:
    numbered = []
    for i, u in enumerate(us):
        v = {'n': i + 1, 'k': k0 + i, 'txt': u['txt']}
        if u.get('label'): v['label'] = u['label']
        if u.get('note'): v['note'] = u['note']
        numbered.append(v)
    k0 += len(us)
    sections.append({'id': sid, 'titel': titel, 'units': numbered})

out = {
 'id': 'ebbinghaus',
 'autor': 'Hermann Ebbinghaus',
 'titel': 'Memory: A Contribution to Experimental Psychology (1885; English 1913) — selections',
 'jahr': 1913,
 'zitierweise': 'Mem. [k]',
 'quelle': ("Selections from the translation of Henry A. Ruger and Clara E. "
            "Bussenius (New York: Teachers College, Columbia University, 1913; "
            "public domain), Internet Archive scan memorycontributi00ebbiuoft, "
            "OCR emended by hand against the sense. Thirteen of the book's "
            "sections carried complete in five chapter groups (I §§ 1–3, II "
            "§§ 4–5, III §§ 11–12, VI §§ 22–23, VII §§ 26–27 and 29–30; § 28, the results tables themselves, is omitted and named as the module's next step); the print's "
            "section headings are carried as labels, and its tables and "
            "formula displays are not reproduced — a note marks each place "
            "where one falls. Paragraph numbering k runs across the whole "
            "module, so a citation 'Mem. [k]' is unique. The German original "
            "of 1885 (Über das Gedächtnis) is named, not carried. Public "
            "domain."),
 'hinweis': ("Learning becomes a curve: nonsense syllables, constant "
             "conditions, the savings method — and the forgetting curve of "
             "chapter VII, rapid at first and then slow, which every "
             "machine-learning textbook still plots. The measured mind's "
             "central exhibit."),
 'sections': sections,
}

path = os.path.join(REPO, 'data', 'ebbinghaus.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(g[2]) for g in groups], 'units')
for g in groups:
    print(' ', g[0], 'first:', g[2][0]['txt'][:80])
