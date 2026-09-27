# -*- coding: utf-8 -*-
# Build data/morgan.json — C. Lloyd Morgan, An Introduction to
# Comparative Psychology (London: Walter Scott, 1894), first edition.
# Source: Internet Archive anintroductiont01morggoog (djvu text,
# downloaded on demand into tools/.cache/). One chapter, carried
# complete in three selections:
#   zugang  — Ch. III, Other Minds than Ours: the problem, and the
#             analogy of the chronometer and the kitchen clock;
#   methode — the doubly inductive method (Figs. 7 and 8 not
#             reproduced, each place marked), and the practical man
#             against the scientific one;
#   kanon   — the canon itself, the objections answered, and the
#             methods of levels, uniform reduction and variation
#             (Fig. 9 not reproduced); the diagram letters restored
#             against the page image (leaf = printed page + 26).
# The chapters that apply the canon are named, not carried. OCR
# emended against the sense. Usage: python tools/build-morgan.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'morgan.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/anintroductiont01morggoog/'
        'anintroductiont01morggoog_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

# ---------------------------------------------------------------- RAWFIX
RAWFIX = [
 (1962, 'observed phenomena', 'interpretation of these observed phenomena, and when it'),
 (2097, 'endowments', 'then should he suppose that their psychical endowments are'),
 (2605, 'thus stated', 'close this chapter. It may be thus stated: — In no case may'),
 (2607, 'psychical', 'higher psychical faculty, if it can be interpreted as the outcome'),
 (2845, 'reduced to zero', 'trated, the highest faculty 3 is in c reduced to zero, — in other'),
]
for n, must, new in RAWFIX:
    assert must in lines[n - 1], f'RAWFIX anchor missing at line {n}: {must!r} not in {lines[n-1]!r}'
    lines[n - 1] = new

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

def harvest(a, b, skips=()):
    paras, buf = [], []
    ln = a
    while ln <= b:
        hit = next(((sa, sb, nt) for sa, sb, nt in skips if sa <= ln <= sb), None)
        if hit:
            if buf: paras.append(' '.join(buf)); buf = []
            if hit[2]: paras.append('\x00NOTE:' + hit[2])
            ln = hit[1] + 1
            continue
        s = lines[ln - 1].strip()
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        elif not (is_head(s) or is_noise(s) or (digit_ratio(s) > .55 and len(s) > 3)):
            buf.append(s)
        ln += 1
    if buf: paras.append(' '.join(buf))
    out = []
    for p in paras:
        if p.startswith('\x00NOTE:'): out.append(p); continue
        p = cleanup(p)
        if len(p) > 2: out.append(p)
    merged = []
    for p in out:
        if p.startswith('\x00NOTE:'): merged.append(p); continue
        prev = merged[-1] if merged and not merged[-1].startswith('\x00NOTE:') else None
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
 (r'\bmodem\b', 'modern'), (r'word mind " in', 'word "mind" in'),
 (r'develop\* ment', 'development'), (r'In both h and we have', 'In both b and c we have'),
 (r'evolution\.\. I am', 'evolution. I am'), (r'an animal\. activity', 'an animal activity'),
 (r'\(i\) Given', '(1) Given'), (r'either \(i\) that', 'either (1) that'),
 (r'num\* ber', 'number'), (r'\btimepices\b', 'timepieces'),
 (r'\bhighiy\b', 'highly'), (r'to the kitchen clockj', 'to the kitchen clock,'),
 (r'difl&cult', 'difficult'), (r'\bfects\b', 'facts'),
 (r"ab'vci terms of c d", 'a b in terms of c d'),
 (r'subjective\* inductions', 'subjective inductions'),
 (r'\bdelicate thin the\b', 'delicate than the'),
 (r'\bafiford\b', 'afford'), (r'\bdehcate\b', 'delicate'),
 (r'\bthe pne accepted\b', 'the one accepted'),
 (r'\bi, 2, 3\b', '1, 2, 3'), (r'faculties i, 2, or 3', 'faculties 1, 2, or 3'),
 (r'faculty \(i\)', 'faculty (1)'), (r'\bimiform\b', 'uniform'),
 (r'In the diagram, \S{1,3} has not quite reached', 'In the diagram, b has not quite reached'),
 (r'In both \S{1,3} and \S{1,3} we have all three', 'In both b and c we have all three'),
 (r'may in h and c be', 'may in b and c be'),
 (r'that b represents', 'that b represents'),
 (r'animal \. activity', 'animal activity'),
 (r'\bMethod ofZevds\b', ''), (r'wholly \'different', 'wholly different'),
 (r'considera- tionis', 'considerations'), (r'\bconsiderationis\b', 'considerations'),
 (r"interpret all other minds", 'interpret all other minds'),
 (r'\^([A-Za-z])', r'\1'), (r'([A-Za-z])\^', r'\1'), (r'\^', ''),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

def units_from(paras):
    us = []
    for p in paras:
        if p.startswith('\x00NOTE:'):
            if us: us[-1]['note'] = p[6:]
            continue
        us.append({'txt': emend(p)})
    return us

# -------------------------------------------------------------- sections
zugang = units_from(harvest(1898, 2356))
methode = units_from(harvest(2358, 2591, skips=[
 (2401, 2412, 'Fig. 7 — the two inductions of the psychologist, objective '
              'and subjective, diagrammed — is not reproduced.'),
 (2439, 2446, 'Fig. 8 — the curve of living beings, its physical line '
              'unbroken, its psychical line dotted beyond the '
              'psychologist\'s own consciousness — is not reproduced.'),
]))
kanon = units_from(harvest(2593, 2879, skips=[
 (2713, 2786, 'Fig. 9 — the methods of levels, of uniform reduction and '
              'of variation, diagrammed — is not reproduced; the letters '
              'of the discussion that follows are restored against the '
              'page image.'),
]))

# the print's numbered problem-clauses are one paragraph
for i, u in enumerate(kanon):
    if u['txt'].endswith('correlated activities:'):
        for _ in range(2):
            nxt = kanon.pop(i + 1)
            u['txt'] += ' ' + nxt['txt']
            if nxt.get('note') and not u.get('note'): u['note'] = nxt['note']
        break
else:
    raise AssertionError('problem-clauses join failed')

# label the canon itself
hit = [u for u in kanon if 'In no case may we interpret an action' in u['txt']]
assert hit, 'canon unit missing'
hit[0]['label'] = 'The canon'

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
    ('zugang', 'The problem — other minds, and the chronometer analogy (pp. 36–47)', zugang),
    ('methode', 'The doubly inductive method (pp. 47–53)', methode),
    ('kanon', 'The canon and its defence (pp. 53–59)', kanon),
]:
    nu = numbered(us, k); k += len(us)
    secs.append({'id': sid, 'titel': titel, 'units': nu})

out = {
 'id': 'morgan',
 'autor': 'C. Lloyd Morgan',
 'titel': 'An Introduction to Comparative Psychology (1894) — selections',
 'jahr': 1894,
 'zitierweise': 'CP [k]',
 'quelle': ("Chapter III, Other Minds than Ours, carried complete from "
            "the first edition (London: Walter Scott, 1894), Internet "
            "Archive anintroductiont01morggoog, OCR emended against the "
            "sense and the diagram passage verified against the page "
            "image (leaf = printed page + 26). The chapter's three "
            "figures are not reproduced, each place marked. Cited as "
            "'CP [k]', k unique across the module; the canon itself "
            "carries a label. The chapters that apply the canon — "
            "instinct, imitation, the perception of relations — are "
            "named as the module's next step; the canon recurs there "
            "in the same words."),
 'hinweis': ("Morgan's canon, in its first book-length statement: never "
             "explain behaviour by a higher faculty when a lower one "
             "suffices — the founding rule against anthropomorphism, "
             "re-argued today wherever machine behaviour is described "
             "in mental terms. Around it, the chapter every debate on "
             "other minds still re-enacts: the chronometer that must "
             "read all other clockwork in terms of its own, and the "
             "warning that of the three methods of interpretation the "
             "least anthropomorphic is also the most difficult. The "
             "chapter's confidence gradient — fellow chronometers, the "
             "kitchen clock — runs through the colonial hierarchies of "
             "its decade ('civilised', 'primitive'); that frame is "
             "carried as printed, stated, not passed over."),
 'sections': secs,
}

path = os.path.join(REPO, 'data', 'morgan.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s['units']) for s in secs], '=', k - 1, 'units')
for s in secs:
    print(f"[{s['id']}]")
    print('  >', s['units'][0]['txt'][:95])
    print('  <', s['units'][-1]['txt'][:95])
