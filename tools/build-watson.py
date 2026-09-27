# -*- coding: utf-8 -*-
# Build data/watson.json — John B. Watson, "Psychology as the
# Behaviorist Views It", Psychological Review 20 (1913), pp. 158-177,
# carried complete. Source: the journal's public-domain printing,
# Internet Archive sim_psychological-review_1913-03_20_2 (the March
# issue; djvu text, downloaded on demand into tools/.cache/). The
# microfilm scan interleaves gutter debris between pages — filtered by
# length and shape; running heads and page numbers dropped. The
# page-bottom footnotes are carried as notes on the paragraph they
# close. OCR emended against the sense.
# Usage: python tools/build-watson.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'watson.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/sim_psychological-review_1913-03_20_2/'
        'sim_psychological-review_1913-03_20_2_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

A, B = 4806, 6008   # the article body, after the byline, to its last line

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
    p = re.sub(r'^[^\w"\'‘“(\[]+', '', p)
    p = re.sub(r'\s+([;:,.!?])', r'\1', p)
    p = re.sub(r'\s+', ' ', p).strip()
    return p

FOOT = re.compile(r'^\d\s+[^.\d]')      # '1 That is, …' — not '1. Human …'

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
        # microfilm gutter debris: short shapeless fragments between pages
        if len(p) < 15: continue
        if len(p) < 40 and not re.search(r'[.!?”"\']$', p): continue
        out.append(p)
    merged = []
    for p in out:
        prev = merged[-1] if merged else None
        if FOOT.match(p):
            merged.append(p); continue
        if prev is not None and not FOOT.match(prev) and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'‘“')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'\bmeans toanend\b', 'means to an end'),
 (r'\bamoebz\b', 'amoebae'), (r'\bamoebe\b', 'amoebae'),
 (r"\bstates\.!\.", 'states.'), (r'states\.!', 'states.'),
 (r'further\*and', 'further and'),
 (r'‘', "'"), (r'’', "'"), (r'“', '"'), (r'”', '"'),
 (r"''", '"'), (r'""', '"'),
 (r'\bzodlogy\b', 'zoology'), (r'\berther\b', 'either'),
 (r'conditions\.\.', 'conditions.'), (r'\bterins\b', 'terms'),
 (r'\btothem\b', 'to them'), (r'\bout findings\b', 'our findings'),
 (r'\bFora\b', 'For a'), (r'yellowand', 'yellow and'),
 (r'went to Tortugas had never', 'went to Tortugas I had never'),
 (r'_In the main', 'In the main'),
 (r"\. 'Their food", '. Their food'), (r"\. 'The ", '. The '),
 (r'1\. ¢\.,', 'i. e.,'), (r'Von Uexkill', 'von Uexküll'),
 (r'method\.\!', 'method.'), (r'parallelism\.\!', 'parallelism.'),
 (r'machinery\!', 'machinery'), (r"adjustment\.'", 'adjustment.'),
 (r'\[I interchange', 'I interchange'),
 (r"untrained\.'", 'untrained.'),
 (r'(\w)\.\!', r'\1.'), (r"in content terms\.'", 'in content terms.'),
 (r'\^([A-Za-z])', r'\1'), (r'([A-Za-z])\^', r'\1'), (r'\^', ''),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

# -------------------------------------------------------------- assemble
paras = harvest(A, B)
units, notes_attached = [], 0
for p in paras:
    if FOOT.match(p):
        seg = emend(re.sub(r'^\d\s+', '', p))
        if units:
            note = 'Page-bottom footnote here: "' + seg + '"'
            if units[-1].get('note'):
                units[-1]['note'] += ' — Further footnote: "' + seg + '"'
            else:
                units[-1]['note'] = note
            notes_attached += 1
        continue
    units.append({'txt': emend(p)})

# ------------------------------------------------ footnote untangling
# The microfilm scan splices the page-bottom footnotes into the text
# stream. Each repair below finds its unit by substring (asserted),
# heals the sentence, and carries the footnote as a note.
def U(frag):
    hit = [u for u in units if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r}'
    return hit[0]

def cut(u, a, b, glue=' '):
    """Remove the span from a to b (exclusive of b's text) in u's txt."""
    i, j = u['txt'].find(a), u['txt'].find(b)
    assert 0 <= i < j, f'cut anchors wrong: {a!r} / {b!r}'
    u['txt'] = (u['txt'][:i] + glue + u['txt'][j:]).replace('  ', ' ').strip()

def note(u, txt):
    p = 'Page-bottom footnote here: "' + txt + '"'
    u['note'] = (u['note'] + ' — ' + p) if u.get('note') else p

def drop(u):
    units.remove(u)

# fn 1 (p. 159), glued to the paragraph's tail
u = U('whose behavior we have been studying.')
i = u['txt'].find(' 1 That is, either directly')
assert i > 0
u['txt'] = u['txt'][:i]
note(u, 'That is, either directly upon the conscious state of the '
        'observer or indirectly upon the conscious state of the '
        'experimenter.')

# fn (p. 166) on imageless thought, spliced mid-sentence
u = U('There is no longer 1Jn this connection')
cut(u, ' 1Jn this connection', 'any guarantee')
note(u, 'In this connection I call attention to the controversy now on '
        'between the adherents and the opposers of imageless thought. '
        "The 'types of reactors' (sensory and motor) were also matters "
        'of bitter dispute. The complication experiment was the source '
        'of another war of words concerning the accuracy of the '
        "opponents' introspection.")

# fn (p. 166 f.) — Warren; its marker closes the parallelism paragraph,
# its body is split across the page into the next unit
u = U('thoroughgoing parallelism.')
note(u, 'My colleague, Professor H. C. Warren, by whose advice this '
        'article was offered to the Review, believes that the '
        'parallelist can avoid the interaction terminology completely '
        'by exercising a little care.')
a = U('without running into the absurd')
a.pop('note', None)
b = U('to the Review, believes that the parallelist')
i = b['txt'].find('terminology of Beer')
assert i > 0
a['txt'] += ' ' + b['txt'][i:]
drop(b)

# the psychological way of phrasing runs straight into its quotation
a = U('I may choose the psychological way and say')
b = U('does the animal see these two lights as I do')
a['txt'] += ' ' + b['txt']
drop(b)

# fn (p. 170) — the ant and the pencil; marker at the wavelength
# paragraph, body split across the page
u = U('He wishes to establish the fact whether wave-length')
note(u, 'He would have exactly the same attitude as if he were '
        'conducting an experiment to show whether an ant would crawl '
        'over a pencil laid across the trail or go round it.')
a = U('if the subject could give it,')
a.pop('note', None)
b = U('there is no need of going to extremes')
i = b['txt'].find('there is no need')
a['txt'] += ' ' + b['txt'][i:]
drop(b)

# fn (p. 172 f.) — the language method, spliced mid-sentence
u = U('all the work upon the senses can be consistently')
cut(u, ' 17 should prefer', 'carried forward along the lines')
note(u, 'I should prefer to look upon this abbreviated method, where '
        'the human subject is told in words, for example, to equate two '
        'stimuli; or to state in words whether a given stimulus is '
        'present or absent, etc., as the language method in behavior. '
        'It in no way changes the status of experimentation. The method '
        'becomes possible merely by virtue of the fact that in the '
        'particular case the experimenter and his animal have systems '
        'of abbreviations or shorthand behavior signs (language), any '
        'one of which may stand for a habit belonging to the repertoire '
        'both of the experimenter and his subject. To make the data '
        'obtained by the language method virtually the whole of '
        'behavior — or to attempt to mould all of the data obtained by '
        'other methods in terms of the one which has by all odds the '
        'most limited range — is putting the cart before the horse '
        'with a vengeance.')

# fn (p. 173) — crude pictures; marker at 'mental machinery'
u = U('discussing the mental machinery')
note(u, 'They are often undertaken apparently for the purpose of '
        'making crude pictures of what must or must not go on in the '
        'nervous system.')

# fn (p. 173 f.) — Galtonian imagery; body strayed into its own unit
u = U('At present the only statements we have of them are in content')
u.pop('note', None)
note(u, 'There is need of questioning more and more the existence of '
        'what the psychologist calls imagery. Until a few years ago I '
        'thought that centrally aroused visual sensations were as clear '
        'as those peripherally aroused. I had never accredited any '
        'other kind. However, closer examination leads me to deny in '
        'my own case the presence of imagery in the Galtonian sense. '
        'The whole doctrine of the centrally aroused image is, I '
        'believe, at present, on a very insecure foundation. Angell as '
        'well as Fernald reach the conclusion that an objective '
        'determination of image type is impossible. It would be an '
        'interesting confirmation of their experimental work if we '
        'should find by degrees that we have been mistaken in building '
        'up this enormous structure of the centrally aroused sensation '
        '(or image).')
drop(U('calls imagery. Until a few years ago'))

# the long footnote of pp. 174-176 — the larynx hypothesis and the
# Thorndike addendum — swallowed three pages of the text stream
a = U('Our minds have been so warped')
i = a['txt'].find('we are not able')
assert i > 0
head = a['txt'][:i] + ('we are not able to carry forward investigations '
       'along all of these lines by the behavior methods which are in '
       'use at the present time.')
tail_u = U('In extenuation I should like to call attention')
j = tail_u['txt'].find('In extenuation')
assert j >= 0
a['txt'] = head + ' ' + tail_u['txt'][j:]
drop(tail_u)
a['label'] = 'The situation squarely met'
note(a, "The hypothesis that all of the so-called 'higher thought' "
        'processes go on in terms of faint reinstatements of the '
        'original muscular act (including speech here) and that these '
        'are integrated into systems which respond in serial order '
        '(associative mechanisms) is, I believe, a tenable one. It '
        'makes reflective processes as mechanical as habit. The scheme '
        'of habit which James long ago described — where each return '
        'or afferent current releases the next appropriate motor '
        "discharge — is as true for 'thought processes' as for overt "
        "muscular acts. Paucity of 'imagery' would be the rule. In "
        'other words, wherever there are thought processes there are '
        'faint contractions of the systems of musculature involved in '
        'the overt exercise of the customary act, and especially in '
        'the still finer systems of musculature involved in speech. If '
        'this is true, and I do not see how it can be gainsaid, imagery '
        'becomes a mental luxury (even if it really exists) without '
        'any functional significance whatever. If experimental '
        'procedure justifies this hypothesis, we shall have at hand '
        'tangible phenomena which may be studied as behavior material. '
        'I should say that the day when we can study reflective '
        'processes by such methods is about as far off as the day when '
        'we can tell by physico-chemical methods the difference in the '
        'structure and arrangement of molecules between living '
        'protoplasm and inorganic substances. The solutions of both '
        'problems await the advent of methods and apparatus. — After '
        'writing this paper I heard the addresses of Professors '
        'Thorndike and Angell, at the Cleveland meeting of the American '
        'Psychological Association. I hope to have the opportunity to '
        'discuss them at another time. I must even here attempt to '
        'answer one question raised by Thorndike. Thorndike (see this '
        'issue) casts suspicions upon ideo-motor action. If by '
        'ideo-motor action he means just that and would not include '
        'sensori-motor action in his general denunciation, I heartily '
        'agree with him. I should throw out imagery altogether and '
        'attempt to show that practically all natural thought goes on '
        'in terms of sensori-motor processes in the larynx (but not in '
        "terms of 'imageless thought') which rarely come to "
        'consciousness in any person who has not groped for imagery in '
        'the psychological laboratory. This easily explains why so many '
        'of the well-educated laity know nothing of imagery. I doubt '
        'if Thorndike conceives of the matter in this way. He and '
        'Woodworth seem to have neglected the speech mechanisms. It '
        'has been shown that improvement in habit comes unconsciously. '
        'The first we know of it is when it is achieved — when it '
        "becomes an object. I believe that 'consciousness' has just as "
        'little to do with improvement in thought processes. Since, '
        'according to my view, thought processes are really motor '
        'habits in the larynx, improvements, short cuts, changes, '
        'etc., in these habits are brought about in the same way that '
        'such changes are produced in other motor habits. This view '
        'carries with it the implication that there are no reflective '
        'processes (centrally initiated processes): the individual is '
        'always examining objects, in the one case objects in the now '
        'accepted sense, in the other their substitutes, viz., the '
        'movements in the speech musculature. From this it follows '
        'that there is no theoretical limitation of the behavior '
        'method. There remains, to be sure, the practical difficulty, '
        'which may never be overcome, of examining speech movements in '
        'the way that general bodily behavior may be examined.')
for frag in ('After writing this paper I heard the addresses',
             'Thorndike (see this issue) casts suspicions'):
    drop(U(frag))

# labels: the opening definition, and the printed Summary
units[0]['label'] = 'The opening definition'
hit = [u for u in units if u['txt'].startswith('1. Human psychology has failed')]
assert hit, 'summary start missing'
hit[0]['label'] = 'Summary'

out = {
 'id': 'watson',
 'autor': 'John B. Watson',
 'titel': 'Psychology as the Behaviorist Views It (1913) — complete',
 'jahr': 1913,
 'zitierweise': 'PBV [n]',
 'quelle': ("The paper of 1913 complete: Psychological Review 20, pp. "
            "158–177, in the journal's public-domain printing (Internet "
            "Archive sim_psychological-review_1913-03_20_2, the March "
            "issue — Watson was the Review's editor), OCR emended against "
            "the sense; the microfilm scan's gutter debris, running heads "
            "and page numbers dropped. The page-bottom footnotes are "
            "carried as notes on the paragraphs they close. Cited as "
            "'PBV [n]'. Titchener's reply of 1914 (Internet Archive "
            "jstor-984126) and Angell's protest in the same issue are "
            "named, not carried."),
 'hinweis': ("The behaviorist manifesto, complete: 'a purely objective "
             "experimental branch of natural science' whose goal is 'the "
             "prediction and control of behavior', with 'no dividing "
             "line between man and brute' — the psychology most ready "
             "to be mechanised, and the one the automaton debate warned "
             "against. Watson's opening paragraph is among the most "
             "quoted in the discipline's history; the paper's quieter "
             "passages — the confession about the animal work, the "
             "scepticism about 'associative memory' as a criterion — "
             "answer Loeb and Morgan across this corpus's own shelves."),
 'sections': [
   {'id': 'text', 'titel': 'The manifesto (pp. 158–177, complete)',
    'units': [dict({'n': i + 1, 'k': i + 1}, **u) for i, u in enumerate(units)]},
 ],
}

path = os.path.join(REPO, 'data', 'watson.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', len(units), 'units,', notes_attached, 'footnotes attached')
print('  >', units[0]['txt'][:95])
print('  <', units[-1]['txt'][:95])
