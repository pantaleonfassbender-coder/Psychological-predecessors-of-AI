# -*- coding: utf-8 -*-
# Build data/koehler.json — Wolfgang Köhler, The Mentality of Apes,
# translated from the second revised German edition by Ella Winter
# (London: Kegan Paul; New York: Harcourt, Brace, 1927 — "revised and
# reset"), in the unaltered reprint of 1931. Source: Internet Archive
# in.ernet.dli.2015.187610 (Digital Library of India scan; djvu text,
# downloaded on demand into tools/.cache/). Four selections:
#   einleitung — Introduction §1 (pp. 1-4): the two interests, Thorndike's
#                'I failed to find any act that even seemed due to
#                reasoning', intelligence as the roundabout path;
#   doppelstock — Chapter IV (pp. 125-130): Rana's optical 'solution' and
#                Sultan's double stick, with the keeper's report;
#   zufall     — Chapter VII, 'Chance' (pp. 185-194): the chance theory
#                set out and refused, and the criterion of insight;
#   schluss    — the Conclusion complete (pp. 265-269).
# Page-bottom footnotes are cut out of the text stream and carried as
# notes; the square-bracketed paragraphs are Winter's rendering of the
# original's small type and are kept as printed. OCR emended against the
# sense.
# Usage: python tools/build-koehler.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'koehler.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/in.ernet.dli.2015.187610/'
        '2015.187610.The-Mentality-Of-Apes_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

E_A, E_B = 150, 290
T_A, T_B = 1068, 1164
D_A, D_B = 5432, 5635
Z_A, Z_B = 7883, 8278
S_A, S_B = 11312, 11488
assert lines[E_A - 1].startswith('I. Two sets of interests')
assert lines[E_B].startswith('2. The experiments were')
assert lines[T_A - 1].startswith('[Thorndike tested large numbers')
assert lines[T_B - 1].startswith('1 Animal Intelligence, New York')
assert lines[D_A - 1].startswith('Are the two sticks ever combined')
assert lines[D_B - 1].startswith('part, he made the trial at once.')
assert lines[Z_A - 1].startswith('The experiments described heretofore')
assert 'led at once to' in lines[Z_B - 1]
assert lines[S_A - 1].startswith('The chimpanzees manifest')
assert 'must be attributed' in lines[S_B - 1]

# --------------------------------------------------------------- filters
def is_head(s):
    if re.search(r'MENTALITY OF APES|^(INTRODUCTION|CONCLUSION)\b|IMPLEMENTS?\b|CHANCE|IMITATION|ROUNDABOUT METHODS', s) \
            and len(s) < 60 and not re.search(r'[a-z]{3}', re.sub(r'the mentality of apes', '', s)):
        return True
    return False

def is_noise(s):
    if not re.search(r'[A-Za-z]{2}', s) and len(s) < 8: return True
    if len(s) <= 5 and not re.search(r'[a-z]{3}', s): return True     # 'i go', 'J 94', '265 s'
    return False

FOOTMARK = re.compile(r"^(?:[12*x»]|')\s+[A-Z]")

def cleanup(p):
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

def harvest(a, b):
    """Paragraphs and footnotes. A footnote starts at a marker line and
    runs to the next running head."""
    paras, notes, buf = [], [], []
    in_foot, foot = False, []
    for ln in range(a, b + 1):
        s = lines[ln - 1].strip()
        if is_head(s):
            if in_foot:
                notes.append((len(paras), ' '.join(foot))); foot = []; in_foot = False
            continue
        if not s:
            if in_foot:
                continue
            if buf:
                paras.append(' '.join(buf)); buf = []
            continue
        if FOOTMARK.match(s) and not in_foot:
            if buf: paras.append(' '.join(buf)); buf = []
            in_foot, foot = True, [s]
            continue
        if in_foot:
            if not is_noise(s): foot.append(s)
        elif not is_noise(s):
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    if in_foot: notes.append((len(paras), ' '.join(foot)))
    paras = [cleanup(p) for p in paras if len(cleanup(p)) > 2]
    merged, index_map = [], []
    for p in paras:
        prev = merged[-1] if merged else None
        if prev is not None and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'‘“[')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
        index_map.append(len(merged) - 1)
    out_notes = [(index_map[pos - 1] if pos >= 1 else 0, cleanup(txt)) for pos, txt in notes]
    return merged, out_notes

# ---------------------------------------------------------------- fixes
FIXES = [
 # quotation marks: this printing spaces them ('“ everyday ”')
 (r'“\s+', '“'), (r'\s+”', '”'), (r'‘\s+', '‘'),
 (r'(^|[\s(\[—])" (?=[\w])', r'\1"'),
 (r'(?<=[\w.,!?;)]) "(?=[\s,.;:)\]—]|$)', '"'),
 (r'\b41 (?=everyday)', '“'), (r'\*\* (?=I failed)', '“'),
 (r'(?<=reasoning)/\' ', '.” '),
 (r'[“”]', '"'), (r'[‘’]', "'"),
 (r'\s+([;:,.!?])', r'\1'),
 # footnote markers left in the text
 (r'through the bars 1 When', 'through the bars. When'),
 (r'by himself, 1 it is', 'by himself, it is'),
 (r'into the other\. 1 \(Plate III \)', 'into the other. (Plate III.)'),
 (r'the same size\. 1 The solution', 'the same size. The solution'),
 (r'fitted together\. 2 Once', 'fitted together. Once'),
 (r'on theories\. 1$', 'on theories.'),
 (r'direction of the objective 1\.', 'direction of the objective.'),
 (r'a coherence 1 of', 'a coherence of'),
 (r'general principles 2,', 'general principles,'),
 (r'testing conditions 1,', 'testing conditions,'),
 (r'combine two sticks 1 only a Philistine', 'combine two sticks; only a Philistine'),
 (r'monkey-species 1\.', 'monkey-species.'),
 (r'longer space of time"\. x A great', 'longer space of time". A great'),
 (r'connects them again > \\ 1$', 'connects them again."'),
 # read against the dump
 (r'\btfce\b', 'the'), (r'starting-pomt', 'starting-point'), (r'\boifly\b', 'only'),
 (r'problem i;', 'problem 1;'), (r'has arisen but of', 'has arisen out of'),
 (r'twice thp length', 'twice the length'), (r'The w r hole', 'The whole'),
 (r'only \? little way', 'only a little way'), (r'\bm order\b', 'in order'),
 (r'\breaches the objective easity\b', 'reaches the objective easily'),
 (r'\bdiffer very much m length', 'differ very much in length'),
 (r'k a PPV state', 'happy state'), (r'a PPty them', 'apply them'),
 (r'\bwifi\b', 'will'), (r'\bpsjxhology\b', 'psychology'), (r'principals aie', 'principles are'),
 (r'\bm facts\b', 'in facts'), (r'put m a series', 'put in a series'),
 (r'it //\^begins', 'it begins'), (r'\bm the development\b', 'in the development'),
 (r'Apart from\. this', 'Apart from this'), (r'keep approximately m the', 'keep approximately in the'),
 (r'practical 11 result"', 'practical "result"'), (r'from \*\' genuine solutions', 'from "genuine solutions"'),
 (r'most sinking difference', 'most striking difference'), (r'described as \*\* genuine" tn clear', 'described as "genuine" in clear'),
 (r'an fond sensible', 'au fond sensible'), (r'aids to chance Secondly', 'aids to chance. Secondly'),
 (r'\bm either case\b', 'in either case'), (r'Oerstedt: Current and Magnet\. Thus', 'Oerstedt: Current and Magnet). Thus'),
 (r'half- under stood', 'half-understood'), (r'building- with-boxes', 'building-with-boxes'),
 (r'\bterm incognita\b', 'terra incognita'), (r'has not vet been', 'has not yet been'),
 (r"in this place, 'where", 'in this place, where'), (r'\(Gestalt\)|\[Gestalt\)', '(Gestalt)'),
 (r'THE MENTALITY OF APES', ''), (r'the mentality of apes', ''),
 (r'\bm\b(?= [a-z])', 'in'), (r'\bammal\b', 'animal'),
 (r'only\? little way', 'only a little way'),
 (r'we call "intelligent in contrast', 'we call "intelligent" in contrast'),
 (r'"intelligence "when', '"intelligence" when'),
 (r'half -ideal', 'half-ideal'), (r'F, Y\. K, etc\.', 'F, Y, K, etc.'), (r'K, R\. D, etc\.', 'K, R, D, etc.'),
 (r"\"molecular disorder\.''", '"molecular disorder."'), (r'p\. 88 seqq \)\]', 'p. 88 seqq.)]'),
 (r'"genuine solutions" In these', '"genuine solutions". In these'),
 (r'buildingwith-boxes', 'building-with-boxes'), (r'halfunder stood', 'half-understood'),
 (r'\(see the next chapter, such cases', '(see the next chapter), such cases'),
 (r'driven to it— but', 'driven to it — but'), (r"requ'rements", 'requirements'),
 (r'accidentallychosen', 'accidentally-chosen'), (r'thumb- piece', 'thumb-piece'),
 (r'\b41 (?=impulses)', '"'), (r'\(insight or not \?\) 2,', '(insight or not?),'),
 (r'\(insight or not\?\) 2,', '(insight or not?),'),
 (r'ca\*i be', 'can be'), (r'p\. 4S\.', 'p. 48.'), (r'door open\." 1$', 'door open."'),
 (r'door open\. " 1$', 'door open."'),
 (r'\{Behaviour Monographs, III, i, 1916\)', '(Behaviour Monographs, III, 1, 1916)'),
 (r'single stick,$', 'single stick.'),
 (r'\(his task\) The', '(his task). The'), (r'the two sticks There need', 'the two sticks. There need'),
 (r'never dare it If', 'never dare it. If'), (r'realizes its meaning$', 'realizes its meaning.'),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

def build(a, b):
    paras, notes = harvest(a, b)
    us = [{'txt': emend(p)} for p in paras]
    for tgt, txt in notes:
        body = emend(re.sub(r"^(?:[12*x»]|')\s+", '', txt))
        note = 'Page-bottom footnote: "' + body + '"'
        us[tgt]['note'] = (us[tgt]['note'] + ' — ' + note) if us[tgt].get('note') else note
    return us

einl = build(E_A, E_B)
thor = build(T_A, T_B)
dopp = build(D_A, D_B)
zuf = build(Z_A, Z_B)
schl = build(S_A, S_B)

def U(us, frag):
    hit = [u for u in us if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r}'
    return hit[0]

# ------------------------------------------------ footnote placement
# The harvester hangs a footnote on the paragraph running at the page
# foot; where the marker stands in an earlier paragraph — or two notes of
# one page were read as one — the notes are set by hand, their text
# checked against the page images (leaf = page + 5 early in the book,
# page + 3 from ch. IV on).
def move(us, src, dst):
    a, b = U(us, src), U(us, dst)
    assert a.get('note'), f'no note on {src!r}'
    b['note'] = ((b['note'] + ' — ') if b.get('note') else '') + a.pop('note')

def setnote(us, frag, *bodies):
    U(us, frag)['note'] = ' — '.join('Page-bottom footnote: "' + b + '"' for b in bodies)

# the p. 3 footnote marks 'intelligent' (the marker read as a lost quote)
assert U(einl, 'takes a roundabout path').pop('note').startswith('Page-bottom footnote: "See foot-note')
TR = ('Page-bottom footnote: "See foot-note, p. 219." [There, the translator\'s note: '
      '"The German word Einsicht is rendered by both \'intelligence\' and \'insight\' '
      'throughout this book."]')
U(einl, 'we call "intelligent" in contrast')['note'] = TR
# ch. I: the p. 22 note on the dog's detour belongs to a paragraph not carried
# and the p. 23 note, read with it as one, is the pointer to p. 219 that
# marks '(insight or not?)'
t0 = U(thor, 'completely visible to the animals')
assert t0.get('note', '').startswith('Page-bottom footnote: "Somewhat different experiments'), t0.get('note')
assert 'See foot-note, p. 219' in t0['note']
t0['note'] = TR
# the reference for the Thorndike quotation (p. 24) marks the paragraph
# that holds the quotation, not the closing one
ref = U(thor, 'Thorndike merely states').pop('note')
assert ref.endswith('p. 48."'), ref
v = U(thor, 'mere vestige of a lick')
v['note'] = ref
move(dopp, 'Sultan fishes with a double-stick', 'Plate III.')
setnote(dopp, 'Sultan fishes with a double-stick',
        'It can be shown that when the chimpanzee connects the double-stick he is '
        'guided by the relation between the two thicknesses of the tubes (compare '
        'Nachweis einfacher Strukturfunktionen, etc., Abh. d. Preuss. Akad. d. Wiss. '
        '1918, Phys.-Math. Kl., No. 2, p. 56 seqq.).')
setnote(dopp, 'never attempted to join tubes',
        'In those cases in which mere observation does not lead to a definite '
        'conclusion, a trial is, of course, made. Compare experiment of 6.8.')
move(zuf, 'Let those parts of the "solution"', 'economizing on facts')
U(zuf, 'economizing on facts')['note'] = (
    'Page-bottom footnote: "Cf. Nachweis einfacher Strukturfunktionen usw., '
    'Abh. d. Preuss. Akad. d. Wiss. 1918, No. 2, p. 40 seqq."')
U(zuf, 'Now I mention from the very beginning').pop('note')
setnote(zuf, 'a tendency to keep approximately',
        'In the case of animals directed by their sense of smell: in the direction '
        'of the strongest intensification of the smell.')
U(zuf, 'To anyone who is inclined to regard').pop('note')
setnote(zuf, 'Hence follows this criterion of insight',
        'The physicists have no word that fits exactly. We use the term "Coherence" '
        'from the theory of radiation, as being the least inappropriate.')
setnote(zuf, 'To anyone who is inclined to regard',
        'E. Wasmann, e.g. Die psychischen Fähigkeiten der Ameisen, 2nd ed., 1909, '
        'p. 108 seqq., has sharply defined this contrast. But he absolutely denies '
        'intelligence in animals, and further points to a logical theory of '
        'intelligent conduct (intelligence) in the case of man, which I cannot '
        'accept. O. Selz, Die Gesetze des geordneten Denkverlaufs, I., 1913, treats '
        'of reproductive thought in man from a point of view somewhat related to mine.')
move(schl, 'The positive result of the investigation', 'nearer to man in intelligence too')
move(schl, 'In the field of the experiments carried out', 'life for a longer space of time')
U(schl, 'life for a longer space of time')['note'] = 'Page-bottom footnote: "Cf. Appendix, p. 271 seqq."'
U(zuf, 'too individual to attract the attention already give')['note'] = (
    "'already give to any general principles' stands so in the printing (p. 186, "
    "checked against the page image); a word may have dropped in the setting.")

U(einl, 'I failed to find any act')['label'] = 'Thorndike as the foil'
U(einl, 'takes a roundabout path')['label'] = 'Intelligence as the roundabout way'
U(thor, 'completely visible to the animals')['label'] = 'Against the puzzle box: the hidden mechanism'
U(dopp, "Keeper's report")['label'] = "Sultan's double stick: the keeper's report"
U(dopp, 'With the triple pole')['label'] = 'The triple pole'
U(zuf, 'the succession is, after all, as accidental')['label'] = 'The chance theory, taken at its word'
U(zuf, 'Hence follows this criterion of insight')['label'] = 'The criterion of insight'
U(zuf, 'slowly scratched his head')['label'] = 'The pause'
U(zuf, 'only a Philistine')['label'] = 'The accident that led to insight'
U(schl, 'every intelligence test is a test')['label'] = 'Every test tests the experimenter'
U(schl, 'The lack of an invaluable technical aid')['label'] = 'Speech, images, and time'

einl[-1]['note'] = ((einl[-1]['note'] + ' — ') if einl[-1].get('note') else '') + (
    'The Introduction continues with §2, the nine chimpanzees of the Tenerife '
    'station (Tschego, Grande, Sultan, Konsul, Tercera, Rana, Chica; Nueva and '
    'Koko), and §3, the preliminary basket-and-string test with Sultan '
    '(pp. 4–9); not carried here.')
dopp[0]['note'] = ((dopp[0]['note'] + ' — ') if dopp[0].get('note') else '') + (
    "The selection opens after Rana's attempt, on the same page, to set two short "
    'sticks end to end as a jumping-pole — a solution for the eye only (p. 125).')

if '--dump' in os.sys.argv:
    for name, us in (('einl', einl), ('thor', thor), ('dopp', dopp), ('zuf', zuf), ('schl', schl)):
        print('=====', name)
        for i, u in enumerate(us):
            print(i + 1, '|', u['txt'])
            if u.get('note'): print('   NOTE:', u['note'])
    raise SystemExit

def numbered(us, k0):
    return [dict({'n': i + 1, 'k': k0 + i}, **u) for i, u in enumerate(us)]

s1 = numbered(einl, 1)
s1b = numbered(thor, 1 + len(s1))
s2 = numbered(dopp, 1 + len(s1) + len(s1b))
s3 = numbered(zuf, 1 + len(s1) + len(s1b) + len(s2))
s4 = numbered(schl, 1 + len(s1) + len(s1b) + len(s2) + len(s3))

out = {
 'id': 'koehler',
 'autor': 'Wolfgang Köhler',
 'titel': 'The Mentality of Apes (1917; English 1925, revised 1927) — selections',
 'jahr': 1917,
 'zitierweise': 'MA [k]',
 'quelle': ("Selections from Ella Winter's translation of the second revised "
            "German edition (London: Kegan Paul, Trench, Trubner; New York: "
            "Harcourt, Brace, 1927 — 'revised and reset'), in the unaltered "
            "reprint of 1931: Internet Archive in.ernet.dli.2015.187610 "
            "(Digital Library of India), OCR emended against the sense, "
            "doubtful points read from the page images. The German original "
            "appeared in 1917 (Intelligenzprüfungen an Anthropoiden), the "
            "first English edition in 1925. Carried: the Introduction §1 "
            "(pp. 1–4); from ch. I the bracketed critique of Thorndike's "
            "experiments (pp. 22–24); ch. IV pp. 125–130 (Sultan's double "
            "stick); ch. VII, 'Chance', pp. 185–194; the Conclusion complete "
            "(pp. 265–269). Square brackets are Winter's, marking the "
            "original's small type. Page-bottom footnotes are carried as "
            "notes on the paragraphs that hold their markers. Cited as "
            "'MA [k]', k unique across the five selections."),
 'hinweis': ("The counter-evidence inside the learning line. Köhler's apes do "
             "not assemble solutions out of chance movements stamped in by "
             "success — the scheme Thorndike's cats were built to show — but "
             "survey the field, pause, and produce the roundabout way whole: "
             "'the appearance of a complete solution with reference to the "
             "whole lay-out of the field' is his criterion of insight. He "
             "turns the method back on its author as well: Thorndike's puzzle "
             "boxes hid their mechanisms, so they could not have shown "
             "insight had it been there — and 'every intelligence test is a "
             "test, not only of the creature examined, but also of the "
             "experimenter himself.' Every later argument over whether a "
             "system 'really understands', and every benchmark built so that "
             "only pattern-matching could pass it, stands on this ground."),
 'sections': [
   {'id': 'einleitung', 'titel': 'Introduction §1 — the two interests, and intelligence as the roundabout way (pp. 1–4)', 'units': s1},
   {'id': 'thorndike', 'titel': "Ch. I — against Thorndike's experiments (pp. 22–24)", 'units': s1b},
   {'id': 'doppelstock', 'titel': "Ch. IV — Sultan's double stick (pp. 125–130)", 'units': s2},
   {'id': 'zufall', 'titel': "Ch. VII — 'Chance': the chance theory and the criterion of insight (pp. 185–194)", 'units': s3},
   {'id': 'schluss', 'titel': 'Conclusion, complete (pp. 265–269)', 'units': s4},
 ],
}

path = os.path.join(REPO, 'data', 'koehler.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s) for s in (s1, s1b, s2, s3, s4)], 'units')
