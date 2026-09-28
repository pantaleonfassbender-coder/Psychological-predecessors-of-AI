# -*- coding: utf-8 -*-
# Build data/bain.json — Alexander Bain, The Senses and the Intellect
# (London: Parker, 1855), first edition. Source: Internet Archive
# sensesintellectb00bain (Library of Congress copy; djvu text, downloaded
# on demand into tools/.cache/). Three selections:
#   wille        — Book I, 'Of the Instinctive Germ of Volition', §§26-32
#                  (pp. 289-298): spontaneous discharge, the volitional
#                  property of feeling, and the movement that happens to
#                  relieve a pain 'clutched in the embrace of the
#                  feeling' — the law of effect before the name;
#   kontiguitaet — Book II, ch. I, 'Law of Contiguity', §§1-2
#                  (pp. 318-321): the law stated, and the spontaneous
#                  movements confirmed by repetition;
#   adhaesion    — the same chapter, §4 (pp. 324-326): the currents that
#                  flow together through the brain fuse — adhesion as
#                  growth in the nerve fibres and cells.
# Page-bottom footnotes are cut out of the text stream and carried as
# notes on the paragraph that holds their marker. OCR emended against the
# sense; one doubtful point read from the page image (p. 290).
# Usage: python tools/build-bain.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'bain.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/sensesintellectb00bain/sensesintellectb00bain_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

W_A, W_B = 15402, 15849
K_A, K_B = 16640, 16790
A_A, A_B = 16937, 17010
assert lines[W_A - 1].startswith('26.  In  a  former  chapter')
assert 'volitional  stimulus  manifested  by  it.' in lines[W_B - 1]
assert 'HHHIS  associating  principle' in lines[K_A - 1]
assert lines[K_B - 1].startswith('excitement  of  the  feelings.')
assert lines[A_A - 1].startswith('4.  The  inward  process')
assert 'subtle  sequence.' in lines[A_B - 1]

# --------------------------------------------------------------- filters
def is_head(s):
    letters = re.sub(r'[^A-Za-z]', '', s)
    if len(letters) >= 6 and len(s) < 70:
        if sum(c.isupper() for c in letters) / len(letters) > .75:
            return True
    return False

NOISE = re.compile(r'^[\W\d]*$')
PAGENO = re.compile(r'^\s*\d{1,3}\s*$')

def is_noise(s):
    if NOISE.match(s): return True
    if not re.search(r'[A-Za-z]{2}', s) and len(s) < 8: return True
    if re.fullmatch(r'[A-Za-z]{1,2}\d?', s): return True     # signatures: 'U', 'tj2', 'Y'
    return False

FOOTMARK = re.compile(r"^\*\s+\S")

def cleanup(p):
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'\s+([;:,.!?])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

def harvest(a, b):
    """Paragraphs and footnotes. A footnote starts at a '*' marker line
    that opens a paragraph and runs to the next running head."""
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
            if not in_foot and buf:
                paras.append(' '.join(buf)); buf = []
            prev_blank = True
            continue
        if prev_blank and FOOTMARK.match(s) and not in_foot:
            if buf: paras.append(' '.join(buf)); buf = []
            in_foot, foot = True, [s]
            prev_blank = False
            continue
        if in_foot:
            if not is_noise(s): foot.append(s)
        elif not is_noise(s):
            buf.append(s)
        prev_blank = False
    if buf: paras.append(' '.join(buf))
    if in_foot: notes.append((len(paras), ' '.join(foot)))
    paras = [cleanup(p) for p in paras if len(cleanup(p)) > 2]
    merged, index_map = [], []
    for p in paras:
        prev = merged[-1] if merged else None
        if prev is not None and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'‘“')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
        index_map.append(len(merged) - 1)
    out_notes = [(index_map[pos - 1] if pos >= 1 else 0, cleanup(txt)) for pos, txt in notes]
    return merged, out_notes

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'^l\. HHHIS associating principle is the basis of Memory, Habit, J- and',
  '1. This associating principle is the basis of Memory, Habit, and'),
 (r'(\w)- (?=[a-z])', r'\1'),         # hyphenation across a page break
 (r'‘', "'"), (r'’', "'"), (r'“', '"'), (r'”', '"'),
 # the quotation marks of this printing are single and spaced: "' It is"
 (r"(^|[\s(—\[])' (?=[A-Za-z])", r"\1'"),
 (r'\bMiiller\b', 'Müller'), (r'\bM tiller\b', 'Müller'), (r'\bMuLLER\b', 'Müller'),
 (r'(?<=[a-z.,;)])\s?\*+(?=\s|$)', ''),
 (r"then of the other/ —", "then of the other.' —"),
 (r'motor apparatus/ — p\. 936-7\.', "motor apparatus.' — p. 936–7."),
 (r'in the limbs This voluntary', 'in the limbs. This voluntary'),        # page image, p. 290
 (r'\bsejDarateness\b', 'separateness'), (r'baJ letdancer', 'ballet-dancer'),
 (r'\bof some hind or other\b', 'of some kind or other'),
 (r'Active Potuers', 'Active Powers'), (r'serene emotions- 32\. There', 'serene emotions. 32. There'),
 (r'\bnervecentres\b', 'nerve-centres'),
 (r'disconnected, condition', 'disconnected condition'),
 (r"'Redintegration/ ", "'Redintegration,' "),
 (r'the\. exposition', 'the exposition'), (r'we term voluntary- Thus', 'we term voluntary. Thus'),
 (r'&c,', '&c.,'),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

def build(a, b):
    paras, notes = harvest(a, b)
    us = [{'txt': emend(p)} for p in paras]
    for tgt, txt in notes:
        body = emend(re.sub(r'^\*\s+', '', txt))
        note = 'Page-bottom footnote: "' + body + '"'
        us[tgt]['note'] = (us[tgt]['note'] + ' — ' + note) if us[tgt].get('note') else note
    return us

wille = build(W_A, W_B)
kont = build(K_A, K_B)
adh = build(A_A, A_B)

def U(us, frag):
    hit = [u for u in us if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r}'
    return hit[0]

def split(us, frag, at):
    u = U(us, frag)
    i = u['txt'].find(at)
    assert i > 0, f'split anchor missing: {at!r}'
    us.insert(us.index(u) + 1, {'txt': u['txt'][i:]})
    u['txt'] = u['txt'][:i].strip()

# The first footnote marks Müller's 'voluntary' (Bain: 'I should say
# spontaneous'); the second, printed on p. 290 but read after the next
# Müller extract, belongs to Bain's own paragraph on the balanced charge.
m1 = U(wille, 'It is evident that the ultimate source of voluntary')
assert m1['note'] == 'Page-bottom footnote: "I should say \'spontaneous.\'"', m1.get('note')
m2 = U(wille, 'The knowledge of the changes of position')
assert m2['note'].startswith('Page-bottom footnote: "Like the ass of Buridan'), m2.get('note')
U(wille, 'too absolutely stated')['note'] = m2.pop('note')

# §32 was run into §31 across a hyphen-like OCR tail ('emotions-')
split(wille, 'serene emotions.', '32. There are various actions')

# the law itself is set in larger type as its own paragraph
split(kont, 'Actions, Sensations, and States of Feeling, occurring',
      'There are various circumstances')

U(wille, 'In short, if the state of pain cannot')['label'] = 'The movement that relieves is kept going'
U(wille, 'An infant lying in bed has the painful sensation')['label'] = 'The infant, the chill, and the random spontaneity'
U(wille, 'To reduce the complicacy of this speculation')['label'] = 'The theory of volition in summary'
U(kont, 'Actions, Sensations, and States of Feeling, occurring')['label'] = 'The Law of Contiguity'
U(adh, 'the fact that these currents flow together')['label'] = 'Currents that flow together fuse'
U(adh, 'forming new cells')['label'] = 'Adhesion as growth'

wille[-1]['note'] = (
    'The chapter goes on to the special activities — locomotion, the voice, '
    'mastication — and, from §33, to speech (pp. 299–314); not carried here.')
kont[-1]['note'] = (
    '§3, on the agglutination of movements into trains and aggregates in '
    'handicraft and mechanical art — walking with the toes turned out, the '
    'succession of acts in eating, writing (pp. 321–324) — is not carried; '
    'the selection resumes with §4.')
adh[-1]['note'] = (
    '§5 goes on to the conditions that regulate the pace of acquisition — '
    'command of the organs, a natural force of adhesiveness unequally '
    'distributed, and repetition (pp. 326 ff.); not carried here.')

def numbered(us, k0):
    return [dict({'n': i + 1, 'k': k0 + i}, **u) for i, u in enumerate(us)]

s1 = numbered(wille, 1)
s2 = numbered(kont, 1 + len(s1))
s3 = numbered(adh, 1 + len(s1) + len(s2))

out = {
 'id': 'bain',
 'autor': 'Alexander Bain',
 'titel': 'The Senses and the Intellect (1855) — selections',
 'jahr': 1855,
 'zitierweise': 'SI [k]',
 'quelle': ("Selections from the first edition (London: John W. Parker and "
            "Son, 1855), Internet Archive sensesintellectb00bain (Library of "
            "Congress copy), OCR emended against the sense, one point read "
            "from the page image. Carried: Book I, 'Of the Instinctive Germ "
            "of Volition', §§26–32 (pp. 289–298, with Bain's extracts from "
            "Johannes Müller's Physiology); Book II, ch. I, 'Law of "
            "Contiguity', §§1–2 (pp. 318–321) and §4 (pp. 324–326). Bain's "
            "page-bottom footnotes are carried as notes; the omitted §3 is "
            "named where it falls. The section numbers in the text are "
            "Bain's own; cited as 'SI [k]', k unique across the three "
            "selections."),
 'hinweis': ("The pivot of the learning line. Bain's volition begins in "
             "random spontaneous movement; when one of those movements "
             "happens to relieve a pain, the feeling seizes it and keeps it "
             "going — 'clutched in the embrace of the feeling' — and "
             "repetition fixes the link. That is trial, error and "
             "reinforcement stated forty years before Thorndike's puzzle "
             "boxes. And the Law of Contiguity is given a physical "
             "reading: currents that flow together through the brain fuse, "
             "the fusion a growth in the nerve fibres and cells — "
             "connectionism before the name, and the neural hypothesis "
             "Ebbinghaus would call premature."),
 'sections': [
   {'id': 'wille', 'titel': 'Book I — Of the Instinctive Germ of Volition, §§26–32 (pp. 289–298)', 'units': s1},
   {'id': 'kontiguitaet', 'titel': 'Book II, ch. I — The Law of Contiguity, §§1–2 (pp. 318–321)', 'units': s2},
   {'id': 'adhaesion', 'titel': 'Book II, ch. I — Adhesiveness a special property of mind, §4 (pp. 324–326)', 'units': s3},
 ],
}

path = os.path.join(REPO, 'data', 'bain.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s1), len(s2), len(s3)], 'units')
for s in (s1, s2, s3):
    print('  >', s[0]['txt'][:95])
    print('  <', s[-1]['txt'][:95])
