# -*- coding: utf-8 -*-
# Build data/pavlov.json — I. P. Pavlov, Conditioned Reflexes: An
# Investigation of the Physiological Activity of the Cerebral Cortex,
# trans. and ed. G. V. Anrep (London: Oxford University Press, 1927).
# Lectures I and II carried complete.
#
# Two copies of the same 1927 printing are used, and why:
#   A  conditionedrefle0000ippa — clean OCR, the base text; read through
#      the item's stream view (its download node refuses the djvu text).
#      This copy lacks the leaf carrying pp. 16-17.
#   B  conditioned-reflexes-an-investigation-of-the-physiological-
#      activity-of-the-cerebral-cortex — complete, but a diagonal
#      'Digitized by …' watermark destroys a band of words on every page.
#      Only pp. 16-17 are taken from it, restored by hand against the
#      page images (leaves 29-30), which remain legible through the mark.
#
# Page-bottom footnotes that are bare references are dropped (Pavlov's
# bracketed author citations stay in the text); the one substantive
# footnote — Mendeleeff's cement — is carried as a note. Figure captions
# and figure-internal labels dropped, each figure named in a note.
# OCR emended against the sense.
# Usage: python tools/build-pavlov.py
import io, json, os, re, html, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'pavlov.txt')
if not os.path.exists(SRC):
    raw = urllib.request.urlopen(urllib.request.Request(
        'https://archive.org/stream/conditionedrefle0000ippa/'
        'conditionedrefle0000ippa_djvu.txt',
        headers={'User-Agent': 'psychpred'}), timeout=120).read().decode('utf-8', 'replace')
    m = re.search(r'<pre[^>]*>(.*?)</pre>', raw, re.S)
    io.open(SRC, 'w', encoding='utf-8').write(html.unescape(m.group(1)))
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

L1_A, L1_B = 508, 1181      # Lecture I body, after heading and synopsis
L2_A, L2_B = 1187, 1881     # Lecture II from p. 18 to its last sentence
assert 'THE cerebral hemispheres stand out' in lines[L1_A - 1]
assert 'interchangeable signification' in lines[L1_B - 1]
assert 'more difficult to obtain the same accuracy' in lines[L2_A - 1]
assert lines[1908].strip().startswith('LECTURE III')

# Blocks the scan splices into the text stream, cut by line range. A
# block with capture=True becomes a note (quoted), attached to the unit
# containing `attach`; otherwise `note` (if given) is attached instead.
CUTS = [
 # (a, b, anchor-in-block, attach-to-unit, capture, note)
 (1243, 1259, 'Fic. 1.', 'to a minimum.', False,
  'Fig. 1 — the apparatus for recording the salivary secretion: the '
  'hemispherical bulb over the fistula, the tube through the partition '
  'to the registering apparatus, and the vacuum bottle — is not '
  'reproduced.'),
 (1266, 1276, 'In almost all the experiments', 'to a minimum.', True, None),
 (1766, 1781, 'Secretion of', 'research by Dr. Eroféeva', False,
  "Dr. Eroféeva's record is not reproduced as a table: at each "
  'stimulation by the strong current — at the usual place and at a new '
  'place on the skin — the secretion flowed, and in all cases the motor '
  "reaction 'was that characteristic of an alimentary reflex; there was "
  "no slightest trace of any motor defence reflex.' After each "
  'stimulation the dog was allowed to eat food for a few seconds.'),
]
PENDING = []
for a, b, anchor, attach, capture, note in CUTS:
    block = ' '.join(lines[i - 1].strip() for i in range(a, b + 1))
    assert anchor in block, f'cut anchor missing at {a}: {anchor!r}'
    if capture:
        body = re.sub(r'^\d\s+', '', re.sub(r'\s+', ' ', block).strip())
        body = re.sub(r'(\w)- (?=[a-z])', r'\1', body)
        PENDING.append((attach, 'The page-bottom footnote here reads: "' + body + '"'))
    elif note:
        PENDING.append((attach, note))
    for i in range(a, b + 1):
        lines[i - 1] = ''

# pp. 16-17, from copy B, restored against the page images
P16_17 = [
 ("In the previous lecture I gave an account of the reasons which led us "
  "to adopt, for the investigation of the functions of the cerebral "
  "hemispheres, the purely objective method used for investigating the "
  "physiological activity of the lower parts of the nervous system. In "
  "this manner the investigation of the cerebral hemispheres is brought "
  "into line with the investigations conducted in other branches of "
  "natural science, and their activities are studied as purely "
  "physiological facts, without any need to resort to fantastic "
  "speculations as to the existence of any possible subjective state in "
  "the animal which may be conjectured on analogy with ourselves. From "
  "this point of view the whole nervous activity of the animal must be "
  "regarded as based firstly on inborn reflexes. These are regular causal "
  "connections between certain definite external stimuli acting on the "
  "organism and its necessary reflex reactions. Such inborn reflexes are "
  "comparatively few in number, and the stimuli setting them in action "
  "act close up, being as a rule the general physical and chemical "
  "properties of the common agencies which affect the organism. The "
  "inborn reflexes by themselves are inadequate to ensure the continued "
  "existence of the organism, especially of the more highly organized "
  "animals, which, when deprived of their highest nervous activity, are "
  "permanently disabled, and if left to themselves, although retaining "
  "all their inborn reflexes, soon cease to exist. The complex conditions "
  "of everyday existence require a much more detailed and specialized "
  "correlation between the animal and its environment than is afforded "
  "by the inborn reflexes alone. This more precise correlation can be "
  "established only through the medium of the cerebral hemispheres; and "
  "we have found that a great number of all sorts of stimuli always act "
  "through the medium of the hemispheres as temporary and "
  "interchangeable signals for the comparatively small number of "
  "agencies of a general character which determine the inborn reflexes, "
  "and that this is the only means by which a most delicate adjustment "
  "of the organism to the environment can be established. To this "
  "function of the hemispheres we gave the name of \"signalization.\""),
 ("Before passing on to describe the results of our investigation it is "
  "necessary to give some account of the purely technical side of the "
  "methods employed, and to describe the general way in which the "
  "signalizing activity of the hemispheres can be studied. It is obvious "
  "that the reflex activity of any effector organ can be chosen for the "
  "purpose of this investigation, since signalling stimuli can get "
  "linked up with any of the inborn reflexes. But, as was mentioned in "
  "the first lecture, the starting point for the present investigation "
  "was determined in particular by the study of two reflexes — the food "
  "or \"alimentary\" reflex, and the \"defence\" reflex in its mildest "
  "form, as observed when a rejectable substance finds its way into the "
  "mouth of the animal. As it turned out, these two reflexes proved a "
  "fortunate choice in many ways. Indeed, while any strong defence "
  "reflex, e.g. against such a stimulus as a powerful electric current, "
  "makes the animal extremely restless and excited; and while the sexual "
  "reflexes require a special environment — to say nothing of their "
  "periodic character and their dependence upon age — the alimentary "
  "reflex and the mild defence reflex to rejectable substances are "
  "normal everyday occurrences."),
 ("It is essential to realize that each of these two reflexes — the "
  "alimentary reflex and the mild defence reflex to rejectable "
  "substances — consists of two distinct components, a motor and a "
  "secretory. Firstly the animal exhibits a reflex activity directed "
  "towards getting hold of the food and eating it or, in the case of "
  "rejectable substances, towards getting rid of them out of the mouth; "
  "and secondly, in both cases an immediate secretion of saliva occurs, "
  "in the case of food, to start the physical and chemical processes of "
  "digestion and, in the case of rejectable substances, to wash them out "
  "of the mouth. We confined our experiments almost entirely to the "
  "secretory component of the reflex: the allied motor reactions were "
  "taken into account only where there were special reasons. The "
  "secretory reflex presents many important advantages for our purpose. "
  "It allows of an extremely accurate measurement of the intensity of "
  "reflex activity, since either the number of drops in a given time may "
  "be counted or else the saliva may be caused to displace a coloured "
  "fluid in a horizontally placed graduated glass tube. It would be much"),
]

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

SYMTOK = re.compile(r'^[\\/|^~*_{}<>«»·•¬£§+=)(-]+$')

def cleanup(p):
    p = ' '.join(t for t in p.split()
                 if not SYMTOK.match(t) or t in ('—', '–', '-'))
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'^[^\w"\'‘“(\[]+', '', p)
    p = re.sub(r'\s+([;:,.!?])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

YEAR = re.compile(r'\b1[789]\d\d\b')
MENDELEEFF = 'Mendeléeff’s cement'

def is_refnote(p):
    """A page-bottom bibliographic footnote: short, carries a year, opens
    with a footnote numeral or scanner debris before an initial/name."""
    if len(p) > 320: return False
    if MENDELEEFF in p: return False
    return bool(YEAR.search(p)) and bool(
        re.match(r'^\W{0,3}[\dí>]?\s?\|?\s?[A-Z]\.?\s?[A-Z,\w]', p)) and (
        p[:1].isdigit() or p[:1] in 'í>' or re.match(r'^[A-Z]\.\s', p))

def is_figure(p):
    if re.match(r'^(Fig|FIG|Fır|Fic)[\s.]', p): return True
    if '=' in p and len(p) < 160: return True
    if p.startswith('Each mark upwards'): return True
    return False

def harvest(a, b):
    paras, buf = [], []
    for ln in range(a, b + 1):
        s = lines[ln - 1].strip()
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        elif not (is_head(s) or is_noise(s)):
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    out, notes = [], []
    for p in paras:
        p = cleanup(p)
        if len(p) < 3: continue
        if p.startswith('A.P.'): continue                 # signature mark
        if MENDELEEFF in p:
            notes.append(('Mendeléeff! most useful', p)); continue
        if is_refnote(p) or is_figure(p): continue
        if len(p) < 40 and not re.search(r'[.!?”"\']$', p): continue
        out.append(p)
    merged = []
    for p in out:
        prev = merged[-1] if merged else None
        if prev is not None and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'‘“')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged, notes

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'‘', "'"), (r'’', "'"), (r'“', '"'), (r'”', '"'), (r'"\'', '"'), (r'\'"', '"'),
 (r'\bInthat\b', 'In that'), (r'\bAsa\b', 'As a'),
 (r'Pfliiger', 'Pflüger'),
 # footnote superscripts glued to names and words
 (r'\[Goltz and others\?\]', '[Goltz and others]'),
 (r'\[Fritsch and Hitzig"?\]', '[Fritsch and Hitzig]'),
 (r'\[Ferrier,\? H\. Munk °?\]', '[Ferrier, H. Munk]'),
 (r'Magnus,! continuing', 'Magnus, continuing'),
 (r'Sherrington\? upon', 'Sherrington upon'),
 (r'Richet,! who', 'Richet, who'),
 (r'Mendeléeff! most useful', 'Mendeléeff most useful'),
 (r'(?<=[a-z])\.1(?=\s|$)', '.'),
 (r'hope of-science', 'hope of science'),
 (r'present-day - physiological', 'present-day physiological'),
 # read against the dump
 (r'^C\. S\. Sherrington, The Integrative Action of the Nervous System, London, ', ''),
 (r'Tropisms;\? to', 'Tropisms; to'), (r'Bethe and Uexkill\?\]', 'Bethe and Uexküll]'),
 (r'Jennings\.\*', 'Jennings.'), (r'\(1898\),! as', '(1898), as'),
 (r'have gone — on now', 'have gone on now'), (r'\bfellowworkers\b', 'fellow-workers'),
 (r'behaviourists °—', 'behaviourists"—'), (r'starting point\. has', 'starting point has'),
 (r'réflexes', 'reflexes'), (r"system, 'and they", 'system, and they'),
 (r"animal is' satiated", 'animal is satiated'), (r'représent', 'represent'),
 (r'shows a: tendency', 'shows a tendency'), (r'animals, This is', 'animals. This is'),
 (r'environment, Thus we see', 'environment. Thus we see'),
 (r'I call it e " What-is-it\? " reflex', 'I call it the "What-is-it?" reflex'),
 (r"F'ood", 'Food'), (r'purely reflex\. i This', 'purely reflex. This'),
 (r'reflex—\* the signal reflex "—is', 'reflex—"the signal reflex"—is'),
 (r'since the\. point', 'since the point'), (r'The term "conditioned ° is', 'The term "conditioned" is'),
 (r"'\* conditioned \"", '"conditioned"'), (r'connection reflexes\." l There', 'connection reflexes." There'),
 (r'\bneryous\b', 'nervous'), (r'signalizing\.reflexes', 'signalizing reflexes'),
 (r'—t\.e\. a stimulus', '—i.e. a stimulus'), (r'same-occurs', 'same occurs'),
 (r'accomplish, The', 'accomplish. The'), (r'establishment-of', 'establishment of'),
 (r"to'stimuli", 'to stimuli'), (r"'' Whatis it\? \"", '"What-is-it?"'),
 (r'\baconditioned\b', 'a conditioned'), (r'few seconds\. i Similar', 'few seconds. Similar'),
 (r'\bobjeccive\b', 'objective'), (r'conditioned\. stimulus', 'conditioned stimulus'),
 (r'not\.a very', 'not a very'), (r'effected by\. surrounding', 'effected by surrounding'),
 (r"''defensive,\"", '"defensive,"'),
 # quote spacing of this OCR: '" fear,"' and '"parental "'
 (r'(^|[\s(—])" (?=[\w\'])', r'\1"'),
 (r'(?<=[\w,.!?]) "(?=[\s,.;:)—]|$)', '"'),
 (r'"unconditioned "could', '"unconditioned" could'),
 (r'"training; "and', '"training;" and'),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

# -------------------------------------------------------------- assemble
l1, n1 = harvest(L1_A, L1_B)
l2_tail, n2 = harvest(L2_A, L2_B)
l2 = list(P16_17)
assert l2_tail[0].startswith('more difficult to obtain'), l2_tail[0][:40]
l2[-1] += ' ' + l2_tail[0]
l2 += l2_tail[1:]

u1 = [{'txt': emend(p)} for p in l1]
u2 = [{'txt': emend(p)} for p in l2]

def add_note(u, txt):
    u['note'] = (u['note'] + ' — ' + txt) if u.get('note') else txt

def find(us, frag):
    hit = [u for u in us if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r} ({len(hit)})'
    return hit[0]

# page-break joins and paragraph splits the scan lost
a = find(u1, 'as reflex—that is to say, as determined.')
b = find(u1, 'Thoughts he regarded as reflexes')
a['txt'] += ' ' + b['txt']; u1.remove(b)
a = find(u2, 'to a minimum.')
i = a['txt'].find('To come to the general technique')
assert i > 0
u2.insert(u2.index(a) + 1, {'txt': a['txt'][i:]})
a['txt'] = a['txt'][:i].strip()

for anchor, seg in n1 + n2:
    add_note(find(u1 + u2, 'Mendeléeff most useful'),
             'The page-bottom footnote here gives the recipe: '
             '"Mendeléeff\'s cement: Colophonium, 50 grammes; ferric oxide, '
             '40 grammes; yellow beeswax, 25 grammes."')
for attach, note in PENDING:
    add_note(find(u1 + u2, attach), note)
add_note(find(u1, 'the treatise by Thorndyke'),
         "Sic: the translation spells the name 'Thorndyke'. The book is "
         "Thorndike's Animal Intelligence — carried in this corpus.")

u2[0]['note'] = ('Pages 16–17 are missing from the base copy and are taken '
                 'from a second copy of the same 1927 printing, restored by '
                 'hand against its page images (see the edition note).')

def label(us, frag, lab):
    hit = [u for u in us if frag in u['txt']]
    assert hit, f'label anchor missing: {frag!r}'
    hit[0]['label'] = lab

label(u1, 'Three hundred years ago Descartes', "Descartes' reflex, and the physiologist's own path")
label(u1, 'the fundamental and the most general function', 'Signalization')
label(u2, 'To this function of the hemispheres we gave the name', 'Inborn reflexes and signals')

def numbered(us, k0):
    return [dict({'n': i + 1, 'k': k0 + i}, **u) for i, u in enumerate(us)]

s1 = numbered(u1, 1)
s2 = numbered(u2, 1 + len(u1))

out = {
 'id': 'pavlov',
 'autor': 'Ivan P. Pavlov',
 'titel': 'Conditioned Reflexes (1927, trans. Anrep) — Lectures I and II',
 'jahr': 1927,
 'zitierweise': 'CR [k]',
 'quelle': ("Lectures I and II complete, from G. V. Anrep's translation "
            "(London: Oxford University Press, 1927; public domain in the "
            "United States). Base text: Internet Archive "
            "conditionedrefle0000ippa, whose scan lacks the leaf with pp. "
            "16–17; those two pages are taken from a second copy of the "
            "same printing (Internet Archive conditioned-reflexes-an-"
            "investigation-of-the-physiological-activity-of-the-cerebral-"
            "cortex, leaves 29–30), whose watermark damages every page and "
            "which was therefore restored by hand against the page images. "
            "Bare bibliographic footnotes dropped (Pavlov's bracketed "
            "author citations stay in the text); Mendeleeff's cement "
            "carried as a note; figures not reproduced. Cited as 'CR [k]', "
            "k unique across the two lectures. The Russian lectures of "
            "1924 are named, not carried."),
 'hinweis': ("The reflex made experimental system: the cerebral "
             "hemispheres studied 'as purely physiological facts, without "
             "any need to resort to fantastic speculations' about the "
             "animal's inner states. Descartes' reflex carried into the "
             "cortex; the hemispheres' fundamental function named "
             "'signalization' — reacting to 'innumerable stimuli of "
             "interchangeable signification'; and the salivary fistula, "
             "the counted drop and the sound-proof laboratory as the "
             "apparatus that turned learning into a measurable procedure. "
             "The conditioned reflex is the vocabulary in which learning "
             "could first be written as an algorithm."),
 'sections': [
   {'id': 'lecture1', 'titel': 'Lecture I — The objective method, the reflex, and signalization (pp. 1–15, complete)', 'units': s1},
   {'id': 'lecture2', 'titel': 'Lecture II — Technical methods; unconditioned and conditioned reflexes (pp. 16–32, complete)', 'units': s2},
 ],
}

path = os.path.join(REPO, 'data', 'pavlov.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s1), len(s2)], 'units')
for s in (s1, s2):
    print('  >', s[0]['txt'][:95])
    print('  <', s[-1]['txt'][:95])
