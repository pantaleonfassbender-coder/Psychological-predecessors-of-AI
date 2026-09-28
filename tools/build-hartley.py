# -*- coding: utf-8 -*-
# Build data/hartley.json — David Hartley, Observations on Man, his Frame,
# his Duty, and his Expectations (1749), Part I, from the sixth edition,
# "corrected and revised" (London: Thomas Tegg and Son, 1834). Source:
# Internet Archive observationsonma00hartuoft (University of Toronto copy;
# djvu text, downloaded on demand into tools/.cache/).
#
# Why the 1834 printing: the first edition (Wellcome copy b30529049_0001)
# and the 1791 printing are set with the long s, ct-ligatures and
# italicised Propositions, which their OCR does not survive; the 1834
# edition is Hartley's text in modern type (nouns no longer capitalised,
# the long s gone). Wording checked against the first edition at every
# Proposition carried; where 1834 departs from 1749 the difference is
# noted on the unit.
#
# Four selections from Part I, ch. I:
#   einleitung   — the Introduction complete and the opening of ch. I
#                  (Newton's vibrations, Locke's association);
#   schwingungen — Prop. IV complete, Prop. VIII complete, Prop. IX's
#                  statement and demonstration (vibratiuncles);
#   assoziation  — Props. X and XI complete: the law of association for
#                  sensations and for vibrations;
#   bewegung     — Props. XXI and XXII complete: voluntary motion from
#                  association, the 'secondarily automatic', and the power
#                  of obtaining pleasure generated in children.
# Usage: python tools/build-hartley.py [--dump]
import io, json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'hartley.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/observationsonma00hartuoft/'
        'observationsonma00hartuoft_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

RANGES = {
 'einleitung':   [(1211, 1409)],
 'schwingungen': [(1563, 1607), (3146, 3238)],
 'assoziation':  [(3450, 3726)],
 'bewegung':     [(4807, 5218)],
}
assert lines[1211 - 1].startswith('Man  consists  of  two  parts')
assert lines[1409 - 1].startswith('the  service  of  future  inquirers.')
assert lines[1563 - 1].startswith('Prop.  IV.')
assert lines[1608 - 1].startswith('Prop.  V.')
assert lines[3146 - 1].startswith('Prop.  VIII.')
assert lines[3223 - 1].startswith('Prop.  IX.')
assert 'line  of  direction.' in lines[3238 - 1]
assert lines[3450 - 1].startswith('Prop.  X.')
assert lines[3727 - 1].startswith('Prop.  XII.')
assert lines[4807 - 1].startswith('Prop.  XXI.')
assert 'argument  for  their  truth.' in lines[5218 - 1]

# --------------------------------------------------------------- filters
def is_head(s):
    letters = re.sub(r'[^A-Za-z]', '', s)
    if len(letters) >= 4 and len(s) < 75:
        if sum(c.isupper() for c in letters) / len(letters) > .8:
            return True
    return False

def is_noise(s):
    if not re.search(r'[A-Za-z]{3}', s) and len(s) < 8: return True     # 'F', 'f2', '('
    return False

def cleanup(p):
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

def harvest(a, b):
    paras, buf = [], []
    for ln in range(a, b + 1):
        s = lines[ln - 1].strip()
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
            continue
        if is_head(s) or is_noise(s):
            continue
        buf.append(s)
    if buf: paras.append(' '.join(buf))
    paras = [cleanup(p) for p in paras]
    merged = []
    for p in paras:
        prev = merged[-1] if merged else None
        if prev is not None and not p.startswith(('Prop.', 'Cor.', 'CoR.')) and (
                re.match(r'^[a-z\)\],;:]', p) or re.search(r'[a-z,;—-]$', prev)):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'[“”]', '"'), (r'[‘’]', "'"),
 (r'\^c\.|8\(c\.|8\(C\.|8cc\.|SfC\.', '&c.'),
 (r'^CoR\.|^,\^OR\.', 'Cor.'),
 (r'\s+([;:,.!?])', r'\1'),
 (r'\bby hei7ig\b', 'by being'), (r'\bhy being\b', 'by being'),
 (r'\bJirst\b', 'first'), (r'\binfijiitesimal\b', 'infinitesimal'),
 (r'\bphaDnomena\b', 'phaenomena'), (r'\bPhcenomena\b', 'Phaenomena'), (r'\bphcenomena\b', 'phaenomena'),
 (r'\bphasnomena\b', 'phaenomena'), (r'\bsuflEicient\b', 'sufficient'), (r'\blamiliar\b', 'familiar'),
 (r'\bafiections\b', 'affections'), (r'\befiicient\b', 'efficient'), (r'\baffiard\b', 'afford'),
 (r'\bfseces\b', 'faeces'), (r'\bvoluntai\'y\b', 'voluntary'), (r'\bsynchronieally\b', 'synchronically'),
 (r'\bMther\b', 'Aether'),
 (r'feelings\.\.of the\. mind', 'feelings of the mind'), (r'\bpaijis\b', 'pains'),
 (r'\bov pain\b', 'or pain'), (r'\breferrinjr\b', 'referring'),
 (r'power oi imagination ox fancy', 'power of imagination or fancy'),
 (r'^The toill is', 'The will is'), (r'\bqucesita\b', 'quaesita'),
 (r'history and ~\\ analysis', 'history and analysis'), (r'theopathy, J and', 'theopathy, and'),
 (r'doctrines of\.vibrations', 'doctrines of vibrations'), (r'respectivelys they', 'respectively, they'),
 (r'\bwellattested\b', 'well-attested'), (r'imme- • diate', 'immediate'),
 (r'may he called\. Simple', 'may be called, Simple'), (r'\bvice versu\b', 'vice versa'),
 (r'\bconiSrmed\b', 'confirmed'), (r'\bvisrilance\b', 'vigilance'),
 (r'Vibratio7is', 'Vibrations'), (r'Vibr aliunde s', 'Vibratiuncles'),
 (r'8fC\.|8&c\.|8fc\.|\bSec\. (?=be vibrations)', '&c.'), (r'\bi, e\.', 'i. e.'),
 (r"obser\^'ations", 'observations'), (r"\\'ividness", 'vividness'), (r'from the \^ name', 'from the name'),
 (r'as a, h, c, does', 'as a, b, c, does'),
 # Prop. XI, read against the first edition (1749, pp. 68-72)
 (r"excite Bs miniature", "excite B's miniature"), (r'such as B, C, I\), &c\.', 'such as B, C, D, &c.'),
 (r'such as h, c, d, &c\. it is evident, that h has', 'such as b, c, d, &c. it is evident, that b has'),
 (r'will at last excite h, c, &c\.', 'will at last excite b, c, &c.'),
 (r'such as C or B\. And as B,', 'such as C or D. And as B,'), (r'so 6, when raised', 'so b, when raised'),
 (r'reach through \^ to C', 'reach through B to C'),
 (r'in its full extent, not vice versa', 'in its full extent, nor vice versa'),
 (r'semi -voluntary', 'semi-voluntary'), (r'sensations, -and lastly', 'sensations, and lastly'),
 (r'\bpreestablished\b', 'pre-established'), (r'will he generated early', 'will be generated early'),
 (r'He affirms then, " both', 'He affirms then, "both'),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

secs = {}
for sid, rs in RANGES.items():
    us = []
    for a, b in rs:
        us += [{'txt': emend(p)} for p in harvest(a, b)]
    secs[sid] = us

# ---------------------------------------------------------- repairs
def U(sid, frag):
    hit = [u for u in secs[sid] if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {sid} {frag!r}'
    return hit[0]

# the half-title 'THE / DOCTRINES OF VIBRATIONS / AND / ASSOCIATION' leaves a stray word
secs['einleitung'] = [u for u in secs['einleitung'] if u['txt'] != 'THE']
# Cor. V of Prop. XXI was run on to Cor. IV across the page break
u = U('bewegung', 'He affirms then, "both')
i = u['txt'].find('",^OR. V.')
assert i > 0
nxt = {'txt': 'Cor. V.' + u['txt'][i + len('",^OR. V.'):]}
u['txt'] = u['txt'][:i + 1]
secs['bewegung'].insert(secs['bewegung'].index(u) + 1, nxt)
assert U('bewegung', 'into the muscles."')

U('einleitung', 'The last is that substance, agent, principle')['note'] = (
    "The first edition (1749) reads 'that Substance, Agent, Principle, to which'; "
    "the '&c.' is the later editions'. So also 'speaking, &c. when attended to' "
    "below, where 1749 has 'Speaking, when attended to'.")
U('assoziation', 'nor vice versa')['note'] = (
    "'nor vice versa' with the first edition (p. 72); the 1834 printing, as read "
    "here, has 'not'.")
U('schwingungen', 'line of direction; and differ only')['note'] = None
secs['schwingungen'][-1]['note'] = (
    'Prop. IX continues with the demonstration from the kind, place and line of '
    'direction of the vibrations, the natural vibrations N, and the effect of '
    'repetition (pp. 37–41); not carried here.')
secs['bewegung'][0]['note'] = (
    'Props. XII–XX, between the association of ideas and this proposition — '
    'complex ideas, muscular motion, the automatic motions, and the corollaries '
    'of Prop. XX to which Hartley refers — (pp. 46–65) are not carried here.')
for u in (x for s in secs.values() for x in s):
    if u.get('note') is None: u.pop('note', None)

L = [
 ('einleitung', 'from their resemblance to the motions of automata', 'Automatic and voluntary motion'),
 ('einleitung', 'My chief design in the following chapter', "Newton's vibrations, Locke's association"),
 ('schwingungen', 'Prop. IV.', 'The doctrine of vibrations'),
 ('schwingungen', 'Prop. VIII.', 'Ideas as vestiges of sensations'),
 ('schwingungen', 'Prop. IX.', 'Vibratiuncles'),
 ('assoziation', 'Prop. X.', 'The law of association'),
 ('assoziation', 'Prop. XI.', 'Association in the medullary substance'),
 ('assoziation', 'whatever becomes of that of vibrations', 'Association, whatever becomes of vibrations'),
 ('bewegung', 'automatic motions of the secondary kind', 'Secondarily automatic'),
 ('bewegung', 'the manner in which we learn to speak', 'How a child learns to speak'),
 ('bewegung', 'play upon the harpsichord', 'The harpsichord'),
 ('bewegung', 'Prop. XXII.', 'The power of obtaining pleasure'),
 ('bewegung', 'contributes most to remove or assuage the pain', 'What relieves pain is confirmed by association'),
]
for sid, frag, lab in L:
    U(sid, frag)['label'] = lab

if '--dump' in sys.argv:
    for sid, us in secs.items():
        print('=====', sid)
        for i, u in enumerate(us):
            print(i + 1, '|', (u.get('label') or ''), '|', u['txt'])
            if u.get('note'): print('   NOTE:', u['note'])
    raise SystemExit

k = 1
out_secs = []
TITLES = {
 'einleitung': 'Introduction, and the opening of ch. I (pp. 1–6)',
 'schwingungen': 'Props. IV, VIII and IX — vibrations, ideas, vibratiuncles (pp. 8, 36–37)',
 'assoziation': 'Props. X and XI — the law of association (pp. 41–46)',
 'bewegung': 'Props. XXI and XXII — voluntary motion, the secondarily automatic, and pleasure (pp. 65–73)',
}
for sid, us in secs.items():
    units = []
    for i, u in enumerate(us):
        units.append(dict({'n': i + 1, 'k': k}, **u)); k += 1
    out_secs.append({'id': sid, 'titel': TITLES[sid], 'units': units})

out = {
 'id': 'hartley',
 'autor': 'David Hartley',
 'titel': 'Observations on Man (1749) — Part I, selections',
 'jahr': 1749,
 'zitierweise': 'OM [k]',
 'quelle': ("Part I, ch. I, from the sixth edition, 'corrected and revised' "
            "(London: Thomas Tegg and Son, 1834), Internet Archive "
            "observationsonma00hartuoft (University of Toronto copy), OCR "
            "emended against the sense. The first edition (London: S. "
            "Richardson, 1749; Internet Archive b30529049_0001, Wellcome "
            "Collection) is set with the long s, ligatures and italic "
            "Propositions that its OCR does not survive; the 1834 edition "
            "gives Hartley's text in modern type, nouns no longer "
            "capitalised. Every Proposition carried was read against the "
            "first edition; where the letters of the 1834 OCR fail (the "
            "algebra of Prop. XI) or the two printings differ, the first "
            "edition is followed and the unit says so. Carried: the "
            "Introduction and the opening of ch. I; Props. IV, VIII and the "
            "statement of IX; Props. X and XI complete; Props. XXI and XXII "
            "complete with their corollaries. Hartley's Proposition numbers "
            "stand in the text; cited as 'OM [k]', k unique across the four "
            "selections."),
 'hinweis': ("The root doctrine of the learning line. Hartley sets out, as "
             "numbered propositions, a physical mechanism of mind: sensations "
             "are vibrations of the 'infinitesimal medullary particles'; "
             "repeated, they leave 'vibratiuncles', the traces that are ideas; "
             "and whatever occurs together 'a sufficient number of times' "
             "comes to call up the rest. From that one law he derives the "
             "will: motions begin automatic, become voluntary by association, "
             "and with practice sink back into the 'secondarily automatic' — "
             "the harpsichordist who plays while holding a conversation. A "
             "child learns to speak because the sounds its attendants return "
             "gain 'an ever-growing balance', and the motion that relieves a "
             "pain is 'confirmed by association, to the exclusion of the "
             "rest'. Every later learning theory in this corpus refines this "
             "wager; Hartley himself says the doctrine of association stands "
             "'whatever becomes of that of vibrations'."),
 'sections': out_secs,
}
path = os.path.join(REPO, 'data', 'hartley.json')
json.dump(out, io.open(path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s['units']) for s in out_secs], 'units')
