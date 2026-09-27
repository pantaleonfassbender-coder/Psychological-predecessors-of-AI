# -*- coding: utf-8 -*-
# Build data/mcdougall.json — William McDougall, Body and Mind: A History
# and a Defense of Animism (1911), from the 1918 printing (London:
# Methuen). Source: Internet Archive cu31924029080880 (Cornell copy;
# djvu text, downloaded on demand into tools/.cache/). Two selections:
#   verhalten — Chapter XIX complete (pp. 258-271): the inadequacy of
#               mechanical conceptions to explain animal and human
#               behaviour — the answer to the tropism doctrine;
#   schluss   — Chapter XXVI, the conclusion's reckoning (pp. 355-357):
#               the long argument summed up, and Animism preferred to
#               Parallelism; the four varieties of Animism that follow
#               are named, not carried.
# Page-bottom footnotes are cut out of the text stream (from a marker
# line to the next running head) and carried as notes on the paragraph
# they interrupt. OCR emended against the sense.
# Usage: python tools/build-mcdougall.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'mcdougall.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/cu31924029080880/cu31924029080880_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

XIX_A, XIX_B = 13123, 13792
XXVI_A, XXVI_B = 17836, 17936
assert lines[XIX_A - 1].startswith('WE have seen that modern physiology')
assert lines[13792].startswith('CHAPTER XX')
assert lines[XXVI_A - 1].startswith('IN this final chapter')
assert 'our acceptance.' in lines[XXVI_B - 1]

# --------------------------------------------------------------- filters
def is_head(s):
    letters = re.sub(r'[^A-Za-z]', '', s)
    if len(letters) >= 6 and len(s) < 70:
        if sum(c.isupper() for c in letters) / len(letters) > .75:
            return True
    return False

NOISE = re.compile(r'^[\W\d]*$')
PAGENO = re.compile(r'^\s*\d{1,3}[o0]?\s*$')

def is_noise(s):
    if NOISE.match(s): return True
    if not re.search(r'[A-Za-z]{2}', s) and len(s) < 8: return True
    return False

FOOTMARK = re.compile(r"^(\d{1,2}|[*^'’‘]{1,2}\^?|\^|'\^|\^\^)\s+\S")

def cleanup(p):
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'\s+([;:,.!?])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

def harvest(a, b):
    """Paragraphs and footnotes. A footnote starts at a marker line that
    opens a paragraph and runs to the next running head or page number."""
    paras, notes, buf = [], [], []
    in_foot, foot = False, []
    prev_blank = True
    for ln in range(a, b + 1):
        s = lines[ln - 1].strip()
        if is_head(s) or PAGENO.match(s):
            if in_foot:
                notes.append((len(paras), ' '.join(foot))); foot = []; in_foot = False
            prev_blank = True
            continue
        if not s:
            if in_foot:
                foot.append('\n')
            elif buf:
                paras.append(' '.join(buf)); buf = []
            prev_blank = True
            continue
        if prev_blank and FOOTMARK.match(s) and not in_foot:
            if buf: paras.append(' '.join(buf)); buf = []
            in_foot, foot = True, [s]
            prev_blank = False
            continue
        if in_foot:
            foot.append(s)
        elif not is_noise(s):
            buf.append(s)
        prev_blank = False
    if buf: paras.append(' '.join(buf))
    if in_foot: notes.append((len(paras), ' '.join(foot)))
    paras = [cleanup(p) for p in paras if len(cleanup(p)) > 2]
    # merge page-break splits
    merged, index_map = [], []
    for i, p in enumerate(paras):
        prev = merged[-1] if merged else None
        if prev is not None and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'‘“')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
        index_map.append(len(merged) - 1)
    # footnotes attach to the paragraph they follow
    out_notes = []
    for pos, txt in notes:
        tgt = index_map[pos - 1] if pos >= 1 else 0
        parts = [cleanup(x) for x in txt.split('\n') if cleanup(x)]
        out_notes.append((tgt, parts))
    return merged, out_notes

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'‘', "'"), (r'’', "'"), (r'“', '"'), (r'”', '"'),
 (r'\bParamceciuni\b', 'Paramoecium'), (r'\bAmceba\b', 'Amoeba'),
 (r'\bfimdamental\b', 'fundamental'), (r'\beifort\b', 'effort'),
 (r'\bpromotethe\b', 'promote the'), (r'\bEfiphenomenalism\b', 'Epiphenomenalism'),
 (r'\( i \)', '(1)'), (r'\bI\'lntelligence\b', "l'Intelligence"),
 (r'stimuli\.\^', 'stimuli.'), (r'Jennings \^ to', 'Jennings to'),
 (r"(?<=[a-z.,;)])\s?[\^*]+(?=\s|$)", ''), (r"(?<=[a-z.,])'(?= [a-z])", ''),
 # this OCR spaces its quotes: '" association-psychology," has'
 (r'(^|[\s(—])" (?=[\w\'])', r'\1"'),
 (r'(?<=[\w,.!?]) "(?=[\s,.;:)—]|$)', '"'),
 (r"\.''", '."'),
 # read against the dump
 (r'\bSoUtary\b', 'Solitary'), (r'\bstimuU\.', 'stimuli.'), (r"fashio'n", 'fashion'),
 (r'\bdifiSculties\b', 'difficulties'), (r'\bhunian\b', 'human'),
 (r'\bpossibihties\b', 'possibilities'), (r'simple\.sense', 'simple sense'),
 (r'the\.Attainment', 'the attainment'), (r'absurdum\. of', 'absurdum of'),
 (r'compounding -of', 'compounding of'), (r'the •current', 'the current'),
 (r'the -natural', 'the natural'), (r'\befiect\b', 'effect'),
 (r'materialrecipient', 'material recipient'), (r'facts, \(i\) that', 'facts, (1) that'),
 (r'\bitsproblems\b', 'its problems'), (r'Parallelists\) \^ without', 'Parallelists) without'),
 (r'infusoria\."i ', 'infusoria." '), (r'again; \' its', 'again; its'),
 (r'\{pp\. cit\.\)', '(op. cit.)'), (r'Jennings fascinating', "Jennings' fascinating"),
 (r'"total reactions "each', '"total reactions" each'), (r'"total "or', '"total" or'),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

def build(a, b):
    paras, notes = harvest(a, b)
    us = [{'txt': emend(p)} for p in paras]
    for tgt, parts in notes:
        for part in parts:
            body = emend(re.sub(r"^(\d{1,2}|[*^'’‘•]{1,2}\^?)\s+", '', part))
            if not body: continue
            note = 'Page-bottom footnote: "' + body + '"'
            us[tgt]['note'] = (us[tgt]['note'] + ' — ' + note) if us[tgt].get('note') else note
    return us

verhalten = build(XIX_A, XIX_B)

# ------------------------------------------------ footnote untangling
# Continuations of three footnotes crossed a page break without a marker
# and were read as text; each is cut out of its host paragraph and
# restored to its note.
def U(frag):
    hit = [u for u in verhalten if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r}'
    return hit[0]

def lift(host, start, end):
    """Remove host text from `start` up to (not incl.) `end`; return it."""
    t = host['txt']
    i, j = t.find(start), t.find(end)
    assert 0 <= i < j, f'lift anchors wrong: {start!r} / {end!r}'
    piece = t[i:j].strip()
    host['txt'] = (t[:i].rstrip() + ' ' + t[j:].lstrip()).strip()
    return piece

def extend_note(u, needle, tail):
    assert needle in u['note'], f'note needle missing: {needle!r}'
    u['note'] = u['note'].replace(needle + '"', needle + tail + '"', 1)

# Driesch (p. 261 f.): 'unmis-' + 'takable instances …'
host = U('The total reaction, although complex, is unitary.')
piece = lift(host, 'takable instances', 'while the sense-impression is a manifold')
host['txt'] = host['txt'].replace('is unitary. while the sense-impression',
                                  'is unitary, while the sense-impression')
dr = U('many purely instinctive actions are thus initiated')
extend_note(dr, 'it is necessary to point to unmis-', piece)
dr['note'] = dr['note'].replace('unmis-takable', 'unmistakable')

# Sherrington (p. 266): the reference to the scratch-reflex studies
host = U('The Integrative Action of the Nervous System')
piece = lift(host, '"The Integrative Action', 'evoked by the contemplation')
host['txt'] = re.sub(r'it is •? ?evoked', 'it is evoked', host['txt'])
sh = U('the scratch-reflex so brilliantly studied')
sh['note'] = ((sh['note'] + ' — ') if sh.get('note') else '') + \
    'Page-bottom footnote: "' + piece.replace('System "and', 'System" and') + '"'

# Busse and Driesch (p. 268 f.): the telegram-argument footnote continues
piece = lift(U('he may evince'), 'and distances, and that in each', 'greater cunning')
extend_note(U('the essential link in each case'),
            'may be seen in many positions and from many angles', ' ' + piece)

# paragraph break lost behind the Jennings quotation; its reference moves with it
j = U('so completely dominate behaviour, perhaps')
i = j['txt'].find('Now, this persistence of movement')
assert i > 0
verhalten.insert(verhalten.index(j) + 1, {'txt': j['txt'][i:]})
j['txt'] = j['txt'][:i].strip()
op = U('Thus we see that, at the very bottom of the evolutionary')
assert op.get('note', '').startswith('Page-bottom footnote: "Op. cit., p. 243."')
j['note'] = op.pop('note')

U('the clock-work stops without a struggle')['label'] = 'Persistence with varied effort'
U('A man receives from a friend a telegram')['label'] = 'The telegram: meaning as the essential link'
schluss = build(XXVI_A, XXVI_B)
schluss[-1]['note'] = ((schluss[-1].get('note', '') + ' — ') if schluss[-1].get('note') else '') + (
    'The chapter continues with the four varieties of Animism — the '
    "'meagre' Animism of interacting conscious elements, the "
    'transmission theory of James and Bergson, and McDougall\'s own soul '
    'as a sum of enduring capacities (pp. 357–372) — and is not carried '
    'further here.')

def numbered(us, k0):
    return [dict({'n': i + 1, 'k': k0 + i}, **u) for i, u in enumerate(us)]

s1 = numbered(verhalten, 1)
s2 = numbered(schluss, 1 + len(verhalten))

out = {
 'id': 'mcdougall',
 'autor': 'William McDougall',
 'titel': 'Body and Mind: A History and a Defense of Animism (1911) — selections',
 'jahr': 1911,
 'zitierweise': 'BM [k]',
 'quelle': ("Selections from the 1918 printing of the 1911 text (London: "
            "Methuen), Internet Archive cu31924029080880 (Cornell copy), "
            "OCR emended against the sense. Carried: Chapter XIX complete "
            "(pp. 258–271) and the conclusion's reckoning in Chapter XXVI "
            "(pp. 355–357). The page-bottom footnotes are carried as notes "
            "on the paragraphs they interrupt — among them McDougall's "
            "reference to Loeb's Die Bedeutung der Tropismen, the book this "
            "chapter answers. Cited as 'BM [k]', k unique across the two "
            "selections."),
 'hinweis': ("The last full-dress defence of the soul against mechanism "
             "before the machines arrived, carried as the automaton "
             "debate's counter-voice. Against the tropism doctrine "
             "McDougall sets two marks of behaviour that no machine "
             "shows — the 'total reaction' of the organism as a whole, and "
             "persistence with varied effort toward an end: 'the "
             "clock-work stops without a struggle if you thrust a spoke "
             "into its wheel.' And he names the link a stimulus-response "
             "scheme leaves out: meaning. Every later argument that "
             "goal-directed persistence is the mark of mind — and every "
             "reply that it can be engineered — begins here."),
 'sections': [
   {'id': 'verhalten', 'titel': 'Ch. XIX — The inadequacy of mechanical conceptions to explain behaviour (pp. 258–271, complete)', 'units': s1},
   {'id': 'schluss', 'titel': 'Ch. XXVI — The conclusion: Animism preferred to Parallelism (pp. 355–357)', 'units': s2},
 ],
}

path = os.path.join(REPO, 'data', 'mcdougall.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s1), len(s2)], 'units')
for s in (s1, s2):
    print('  >', s[0]['txt'][:95])
    print('  <', s[-1]['txt'][:95])
