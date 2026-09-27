# -*- coding: utf-8 -*-
# Build data/loeb.json — Jacques Loeb, Comparative Physiology of the
# Brain and Comparative Psychology (New York: G. P. Putnam's Sons,
# 1900). Source: Internet Archive comparativephysi00loeb (djvu text,
# downloaded on demand into tools/.cache/). Three selections:
#   programm  — the Preface (dedicated to Ernst Mach, the
#               antimetaphysical program) and Chapter I complete:
#               reflexes and tropisms, the identity of animal with
#               plant heliotropism, consciousness set aside as a
#               metaphysical term, associative memory announced as
#               the real problem;
#   instinkt  — Chapter XIII §§ 1-3: instincts as tropisms — the moth
#               and the flame demystified, the mock 'flying-into-the-
#               flame centre', stereotropism and the cracks;
#   kriterium — Chapter XV §§ 1-4: associative memory defined (the
#               phonograph comparison), Mach's ego, the criterion —
#               if an animal can learn it has associative memory —
#               the distribution survey, and the Bethe ant experiments
#               read as chemistry, not memory.
# Chapter bibliographies dropped; the Steiner footnote carried as a
# note. OCR emended against the sense.
# Usage: python tools/build-loeb.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'loeb.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/comparativephysi00loeb/'
        'comparativephysi00loeb_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

# ------------------------------------------------- footnote extraction
FOOTNOTES = [
 (7166, 7170, 'flying-into-the-flame', 'Steiner tries indeed'),
 (6948, 6951, None, 'Dr. Lyon'),
]
PENDING_NOTES = []
for a, b, attach, anchor in FOOTNOTES:
    seg = re.sub(r'\s+', ' ', ' '.join(lines[i - 1].strip() for i in range(a, b + 1)))
    assert anchor in seg, f'footnote anchor missing at {a}: {anchor!r} not in {seg[:80]!r}'
    if attach:
        PENDING_NOTES.append((attach, seg))
    for i in range(a, b + 1):
        lines[i - 1] = ''

# --------------------------------------------------------------- filters
def is_head(s):
    letters = re.sub(r'[^A-Za-z]', '', s)
    if len(letters) >= 6 and len(s) < 70:
        if sum(c.isupper() for c in letters) / len(letters) > .75:
            return True
    return False

NOISE = re.compile(r'^[\W\d]*$')

def is_noise(s):
    if NOISE.match(s): return True
    if not re.search(r'[A-Za-z]{2}', s) and len(s) < 8: return True
    return False

def digit_ratio(s):
    core = re.sub(r'\s', '', s)
    if not core: return 0
    return sum(c.isdigit() or c in '.,-—()' for c in core) / len(core)

SYMTOK = re.compile(r'^[\\/|^~*_{}<>«»·•¬£§+=)(-]+$')

def cleanup(p):
    p = ' '.join(t for t in p.split()
                 if not SYMTOK.match(t) or t in ('—', '–', '-'))
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'^[^\w"\'(\[]+', '', p)
    p = re.sub(r'\s+([;:,.!?])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

def harvest(a, b):
    paras, buf = [], []
    for ln in range(a, b + 1):
        s = lines[ln - 1].strip()
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        elif not (is_head(s) or is_noise(s) or (digit_ratio(s) > .55 and len(s) > 3)):
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    out = []
    for p in paras:
        p = cleanup(p)
        if len(p) > 2: out.append(p)
    merged = []
    for p in out:
        prev = merged[-1] if merged else None
        if prev is not None and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'^i\. The understanding', '1. The understanding'),
 (r'^i\. The discrimination', '1. The discrimination'),
 (r'^i\. The most important', '1. The most important'),
 (r'\bthetropisms\b', 'the tropisms'), (r'tropisms--and', 'tropisms — and'),
 (r'\bcesophugus\b', 'oesophagus'), (r'\btlame\b', 'flame'),
 (r'flying-into-thetlame', 'flying-into-the-flame'),
 (r'Palsemonetes', 'Palaemonetes'), (r'\blarvse\b', 'larvae'),
 (r'\btropismsof\b', 'tropisms of'), (r'to £O from', 'to go from'),
 (r'\(i, 1 1\)', '(1, 11)'), (r'\(i, n\)', '(1, 11)'), (r'\(i\)', '(1)'),
 (r'Miinsterberg', 'Münsterberg'), (r'\(6,  ?12\)', '(6, 12)'),
 (r'e°f£s', 'eggs'), (r'reflexes --the socalled', 'reflexes — the so-called'),
 (r'\bganglioncells\b', 'ganglion-cells'), (r'\bganglioncell\b', 'ganglion-cell'),
 (r'\bswarmspores\b', 'swarm-spores'), (r'\bcentretheory\b', 'centre-theory'),
 (r'Ccelenterates', 'Coelenterates'), (r'bend away\. from', 'bend away from'),
 (r'\bselfconcealment\b', 'self-concealment'), (r'per cent, of', 'per cent. of'),
 (r'\breactiontime\b', 'reaction-time'),
 (r'"knowing "of "friend and foe "', '"knowing" of "friend and foe"'),
 (r'" ([A-Za-z][^"]{0,28}?) "', r'"\1" '), (r'" instinct"', '"instinct"'),
 (r'"\s+([,.;:])', r'"\1'),
 (r'\bDIS TRIB UTION\b', ''), (r'\bTHEOR Y\b', ''),
 (r'\^([A-Za-z])', r'\1'), (r'([A-Za-z])\^', r'\1'), (r'\^', ''),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

def units_from(paras):
    return [{'txt': emend(p)} for p in paras]

# -------------------------------------------------------------- sections
programm = units_from(harvest(156, 206) + harvest(443, 915))
# restore the dateline the head-filter strips, and fold it into the close
for i, u in enumerate(programm):
    if u['txt'].startswith('October'):
        programm[i - 1]['txt'] += ' — The University of Chicago, October 1, 1900.'
        del programm[i]
        break
else:
    raise AssertionError('preface dateline not found')
instinkt = units_from(harvest(6969, 7274))
kriterium = units_from(harvest(8234, 8620))

# attach the extracted footnote
allus = programm + instinkt + kriterium
for target, seg in PENDING_NOTES:
    seg = emend(cleanup(seg))
    hit = [u for u in allus if target in u['txt']]
    assert hit, f'note target not found: {target!r}'
    hit[0]['note'] = ('The page-bottom footnote here is carried in full: "' +
                      seg.lstrip("'").strip() + '"')

# labels
h = [u for u in instinkt if 'does not fly into the flame out of' in u['txt']]
assert h, 'moth unit missing'
h[0]['label'] = 'The moth and the flame'
h = [u for u in kriterium if 'if an animal can learn' in u['txt']]
assert h, 'criterion unit missing'
h[0]['label'] = 'The criterion'
h = [u for u in kriterium if 'imitated by machines like the phonograph' in u['txt']]
assert h, 'phonograph unit missing'
h[0]['label'] = 'Associative memory defined'

# named omissions
instinkt[-1]['note'] = ('The chapter continues — the egg-laying instincts, '
                        'the alleged instinct of self-preservation, and the '
                        'heredity of instincts as the heredity of machine '
                        'structure (§§ 4–6, pp. 186–199) — and is not '
                        'carried further here.')
kriterium[-1]['note'] = ('The chapter continues — Loeb against Bethe on the '
                         'memory of ants and bees, the wasp observations, '
                         'and the summary (§§ 5–8, pp. 224–235) — and is '
                         'not carried further here; the survey chapters on '
                         'the animal classes are named, not carried.')

# ------------------------------------------------------------- assemble
def numbered(us, k0):
    out = []
    for i, u in enumerate(us):
        v = {'n': i + 1, 'k': k0 + i, 'txt': u['txt']}
        if u.get('label'): v['label'] = u['label']
        if u.get('note'): v['note'] = u['note']
        out.append(v)
    return out

k = 1
secs = []
for sid, titel, us in [
    ('programm', 'The program — Preface, and Chapter I complete (pp. v–vi, 1–15)', programm),
    ('instinkt', 'Instincts as tropisms — ch. XIII §§ 1–3 (pp. 177–186)', instinkt),
    ('kriterium', 'Associative memory as the criterion — ch. XV §§ 1–4 (pp. 213–224)', kriterium),
]:
    nu = numbered(us, k); k += len(us)
    secs.append({'id': sid, 'titel': titel, 'units': nu})

out = {
 'id': 'loeb',
 'autor': 'Jacques Loeb',
 'titel': 'Comparative Physiology of the Brain and Comparative Psychology (1900) — selections',
 'jahr': 1900,
 'zitierweise': 'CPB [k]',
 'quelle': ("Selections from the 1900 printing (New York: G. P. Putnam's "
            "Sons; trans. Anne Leonard Loeb, revised by the author), "
            "Internet Archive comparativephysi00loeb, OCR emended against "
            "the sense. Carried: the Preface and Chapter I complete; "
            "Chapter XIII §§ 1–3 (instincts as tropisms, with the Steiner "
            "footnote as a note); Chapter XV §§ 1–4 (associative memory "
            "and the criterion). The chapter bibliographies are not "
            "carried; the omitted continuations are named in notes. "
            "Cited as 'CPB [k]', k unique across the module."),
 'hinweis': ("The organism as tropism-machine, and the line drawn where "
             "this corpus ends: for Loeb, mind begins where learning "
             "begins — associative memory, imitable 'by machines like "
             "the phonograph', is the criterion of consciousness, and "
             "below it there is only orientation. The moth does not love "
             "the light and is not curious about it; it is oriented by "
             "it. The mock 'flying-into-the-flame centre' is the "
             "corpus's sharpest early warning against explaining "
             "behaviour by naming a module for it — and Loeb's "
             "light-seeking machines were the blueprint the first "
             "robot-builders read, down to Braitenberg's vehicles."),
 'sections': secs,
}

path = os.path.join(REPO, 'data', 'loeb.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s['units']) for s in secs], '=', k - 1, 'units')
for s in secs:
    print(f"[{s['id']}]")
    print('  >', s['units'][0]['txt'][:95])
    print('  <', s['units'][-1]['txt'][:95])
