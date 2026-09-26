# -*- coding: utf-8 -*-
# Build data/thorndike.json — Thorndike, Animal Intelligence (1911),
# selections. Source: the 1911 collected volume (Macmillan), Internet
# Archive animalintellige00thorgoog, djvu OCR (downloaded on demand into
# tools/.cache/). Three sections:
#   stand  — ch. II opening: the standpoint of the 1898 monograph
#            (against anecdote, for experiment);
#   method — Description of Apparatus, the cats in the puzzle boxes (the
#            famous stamping-in passage), and the time-curve as record —
#            cut before the curve listings themselves (the figures are
#            not reproduced);
#   laws   — ch. VI, Laws and Hypotheses for Behavior, complete: the
#            laws of effect and exercise formally stated and defended.
# k continues across the two chapter-II sections so that 'AI, ch. II [k]'
# is unambiguous. OCR emended against the sense via FIXES (each with an
# expected count); running heads, page numbers and figure captions
# dropped; the volume's few footnotes are not carried.
# Usage: python tools/build-thorndike.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'thorndike.txt')
if not os.path.exists(SRC):
    url = ('https://archive.org/download/animalintellige00thorgoog/'
           'animalintellige00thorgoog_djvu.txt')
    urllib.request.urlretrieve(url, SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

HEAD = re.compile(
    r'^\s*(\d{1,3}\s+)?(Animal I\w+ce|Experi\w* Study of Associative Processes|'
    r'Laws and Hypotheses (for|far) Behavio.*?|Digitized by.*)\s*(\d{1,3})?\s*$', re.I)
NOISE = re.compile(r'^\s*(\d{1,3}|[ivxlIVXL]+|[A-Za-z]|Figure\s+\S+\.?|Sin A\.|Awagt.m A\.)\s*$')

def harvest(a, b):
    """Paragraphs from source lines a..b (1-based, inclusive)."""
    paras, buf = [], []
    for raw in lines[a - 1:b]:
        s = raw.strip()
        if HEAD.match(s) or NOISE.match(s):
            continue
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    out = []
    DROP = re.compile(r'^(CHAPTER\b|\*|\^|>|Animal Intelligence ;)')
    for p in paras:
        p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
        p = re.sub(r'\s+', ' ', p).strip()
        if len(p) > 1 and not DROP.match(p): out.append(p)
    return out

# Section heads inside the harvested ranges become labels on the
# following paragraph rather than paragraphs of their own.
LABELS = {
    'Description of Apparatus', 'Experiments with Cats',
    'Laws of Behavior in General',
    'Provisional Laws of Acquired Behavior or Learning',
    'The Adequacy of the Laws of Exercise and Effect',
}

def fold_labels(paras):
    out, pend = [], None
    for p in paras:
        joined = None
        for l in LABELS:
            if p == l: joined = l
        # two-line heads arrive split: try joining with the next
        if p in ('Provisional Laws of Acquired Behavior or', 'The Adequacy of the Laws of Exercise and'):
            pend = p; continue
        if pend is not None:
            cand = pend + ' ' + p
            if cand in LABELS: joined = cand
            else: out.append({'txt': pend + ' ' + p})
            pend = None
            if joined: pend2 = joined
            else: continue
        if joined:
            out.append({'label': joined}); continue
        out.append({'txt': p})
    merged = []
    for x in out:
        if 'label' in x and 'txt' not in x:
            merged.append({'_lab': x['label']}); continue
        if merged and '_lab' in (merged[-1] or {}):
            lab = merged.pop()['_lab']
            merged.append({'txt': x['txt'], 'label': lab})
        else:
            merged.append(x)
    return [m for m in merged if 'txt' in m]

FIXES = [
    (r'\bFinaUy\b', 'Finally', 1),
    (r'\baccoimt\b', 'account', None),
    (r'\bhimger\b', 'hunger', None),
    (r'\bHimger\b', 'Hunger', None),
    (r'situatioQ s 341 depends', 'situation depends', 1),
    (r'\{e,g\.', '(e.g.', None),
    (r'\bknawable\b', 'knowable', 1),
    (r'\bdosed\b', 'closed', None),
    (r'\bdosdy\b', 'closely', None),
    (r'\biq>\B', 'up', None),
    (r'accompan\)d\w*', 'accompanying', 1),
    (r'situation\^', 'situation,', None),
    (r'\(2\^ inches', '(2½ inches', 1),
    (r'\btaJien\b', 'taken', 1),
    (r'\btJi(\w+)', r'th\1', None),
    (r'\btJte\b', 'the', None),
    (r'\bthai\b', 'that', None),
    (r'\bwilly\b', 'will,', None),
    (r'\bequaly\b', 'equal,', None),
    (r'\bsituationy\b', 'situation,', None),
    (r'\bresponsey\b', 'response,', None),
    (r'\babsdssa\b', 'abscissa', None),
    (r'\bim ?\^? ?ptdse\b', 'impulse', None),
    (r'\bimptdse\b', 'impulse', None),
    (r'impulse\^', 'impulse,', None),
    (r'\bimless\b', 'unless', None),
    (r'\bimderstand\b', 'understand', None),
    (r'K the interval', 'If the interval', 1),
    (r'\bi hr\.', '1 hr.', 1),
    (r'all but 1 1 and 13', 'all but 11 and 13', 1),
    (r'No\. I\. 8-10', 'No. 1. 8–10', 1),
    (r'Experimer[A-Za-z]* Study of Associative Processes \d+\s*', '', None),
    (r'\bBehavioh\b', 'Behavior', None),
    (r'\bnatiure\b', 'nature', None),
    (r'\bimexplained\b', 'unexplained', 1),
    (r'\bimder\b', 'under', None),
    (r'\bimtil\b', 'until', None),
    (r'\bimcommonly\b', 'uncommonly', 1),
    (r'\bdaw\b', 'claw', 1),
    (r'\bsituortion\b', 'situation', None),
    (r'\bsituor- ?tion\b', 'situation', None),
    (r'6-63\^ months', '6–6½ months', 1),
    (r'5-1 1 months', '5–11 months', 1),
    (r'\bmodem\b', 'modern', None),
    (r'Andial', 'Animal', None),
]

def emend(paras):
    text = '\n'.join(p['txt'] for p in paras)
    for pat, rep, expect in FIXES:
        n = len(re.findall(pat, text))
        if expect is not None:
            assert n == expect or n == 0, (pat, n)
    for p in paras:
        for pat, rep, _ in FIXES:
            p['txt'] = re.sub(pat, rep, p['txt'])
    return paras

def polish(paras):
    """Post-clean: strip footnote carets, drop figure/table debris, merge
    footnote-split continuations (lowercase starts) into the previous
    paragraph, and fold the printed list of the cats' ages into one unit."""
    DEBRIS = re.compile(r'^(Fio\.|Tia\.|Table I|No\. Cats|bC |-T r|\d+\w{0,4}A\.)')
    out = []
    for p in paras:
        t = re.sub(r'\s*\^', '', p['txt']).strip()
        if DEBRIS.match(t) or len(t) < 28 and not re.match(r'^No\. I', t):
            continue
        p = dict(p, txt=t)
        if out and re.match(r'^[a-z]', t) and not p.get('label'):
            out[-1]['txt'] += ' ' + t
        elif out and re.match(r'^No\. \d', t) and re.search(r'months\.$', out[-1]['txt']):
            out[-1]['txt'] += ' ' + t
        else:
            out.append(p)
    return out

stand = emend(polish(fold_labels(harvest(1105, 1490))))
method = emend(polish(fold_labels(harvest(1491, 1552) + [''] + harvest(1706, 2036))))
laws = emend(polish(fold_labels(harvest(15225, 15617))))

# Hand repairs where the OCR shredded a line beyond pattern fixes: each
# asserts its target so silent drift is impossible.
def repair(secs, frag, replacement):
    for sec in secs:
        for p in sec:
            if frag in p['txt']:
                p['txt'] = p['txt'].replace(frag, replacement)
                return
    raise AssertionError('repair target not found: ' + frag)

sections = [stand, method, laws]

def numbered(paras, k0):
    us = []
    for i, p in enumerate(paras):
        u = {'n': i + 1, 'k': k0 + i, 'txt': p['txt']}
        if p.get('label'): u['label'] = p['label']
        if p.get('note'): u['note'] = p['note']
        us.append(u)
    return us

# the title line of the chapter is dropped if it survived the filters
if stand and stand[0]['txt'].startswith('Animal Intelligence ;'):
    stand = stand[1:]
if method and method[-1]['txt'].rstrip().endswith(': —'):
    method[-1]['note'] = 'The table that follows in the print is not reproduced.'

u_stand = numbered(stand, 1)
u_method = numbered(method, 1 + len(stand))
u_laws = numbered(laws, 1)

out = {
 'id': 'thorndike',
 'autor': 'Edward L. Thorndike',
 'titel': 'Animal Intelligence (1911) — selections',
 'jahr': 1911,
 'zitierweise': 'AI, ch. II/VI [k]',
 'quelle': ("Selections from Animal Intelligence: Experimental Studies (New York: "
            "Macmillan, 1911), from the Internet Archive scan "
            "animalintellige00thorgoog, OCR emended by hand against the sense. "
            "Chapter II reprints the monograph of 1898; its paragraph numbering "
            "here runs across both selections, so that a citation 'AI, ch. II [k]' "
            "is unique. From chapter VI the two law-stating subsections are carried "
            "complete (Laws of Behavior in General; Provisional Laws of Acquired "
            "Behavior or Learning); the chapter's long defence of their adequacy "
            "is named as the module's next step. Box A's description is carried; the "
            "parallel specifications of boxes B–K are omitted, and the volume's "
            "figures, time-curve plates and footnotes are not reproduced; the "
            "printed list of the cats' ages is folded into a single paragraph. "
            "Public domain."),
 'hinweis': ("The corpus's most direct line into present-day AI: the puzzle boxes, "
             "the stamping-in of successful impulses, and the formal statement of "
             "the laws of effect and exercise that reinforcement learning names as "
             "its ancestry."),
 'sections': [
   {'id': 'stand', 'titel': 'Ch. II — The standpoint of the monograph (1898)',
    'units': u_stand},
   {'id': 'method', 'titel': 'Ch. II — Apparatus, the cats, and the time-curve',
    'units': u_method},
   {'id': 'laws', 'titel': 'Ch. VI — The laws of behavior stated',
    'units': u_laws},
 ],
}

path = os.path.join(REPO, 'data', 'thorndike.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s) for s in sections], 'units')
for s in sections:
    for p in s[:2]: print('  >', p['txt'][:90])
