# -*- coding: utf-8 -*-
# Build data/binet.json — Binet & Simon, The Development of Intelligence
# in Children, trans. Elizabeth S. Kite (Vineland, N.J.: The Training
# School, 1916), collecting the L'Annee Psychologique papers of 1905-1911.
# Source: Internet Archive developmentofint00binerich (djvu text,
# downloaded on demand into tools/.cache/). Four selections:
#   programm — the opening of "New Methods" (1905) complete: the problem,
#              the three methods, the measuring-scale idea, and the
#              definition of intelligence as judgment;
#   tests    — the 1905 instrument: general recommendations, test 1
#              ("Le Regard") complete, the thirty tests as the printed
#              list of titles, tests 27 and 30 complete, and the closing
#              scoring rubric (-, fraction, +, !) with the I/R/T/D notes;
#   skala    — from the 1908 paper: General Conditions of the Examination
#              and the classification of the tests by age, three to
#              thirteen years (the two-column list restored by hand from
#              the print's own page references);
#   niveau   — the estimate of results (1908): the weighing-machine
#              warning, the recording signs, the absurd replies grouped,
#              the impossibility of a single test-limit, and the rule of
#              the mental level with its compensating rule.
# Page-bottom footnotes are extracted by line range: two editorial and two
# authorial ones are carried as notes, mere references dropped. OCR
# emended against the sense. Usage: python tools/build-binet.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'binet.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/developmentofint00binerich/'
        'developmentofint00binerich_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

# ------------------------------------------------- footnote extraction
# (a, b, attach): lines a..b leave the text stream; with attach=None they
# are dropped, otherwise their text becomes a note on the unit containing
# the attach substring. The surrounding sentence then merges across the
# gap. Anchors are asserted.
FOOTNOTES = [
 (2180, 2182, None, 'One of us (Binet)'),
 (2226, 2229, 'idiocy, imbecility, and moronity', "note: Binet's"),
 (2407, 2411, None, 'One of us (Binet)'),
 (2413, 2416, 'coordination in the movement of the head', 'note: We have'),
 (3373, 3374, None, 'Cf.'),
 (3521, 3521, None, 'Cf.'),
 (15151, 15182, 'ranged according to the ages', 'These tests are not'),
 (15566, 15566, None, 'psychologique'),
 (15614, 15614, None, 'final rule'),
]
PENDING_NOTES = []
for a, b, attach, anchor in FOOTNOTES:
    seg = re.sub(r'\s+', ' ', ' '.join(lines[i - 1].strip() for i in range(a, b + 1)))
    assert anchor in seg, f'footnote anchor missing at {a}: {anchor!r} not in {seg[:90]!r}'
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
    HEADGUARD = (re.compile(r'^General Conditions of the Examination$'),
                 re.compile(r'^I\. The Psychological Method$'))
    for p in out:
        prev = merged[-1] if merged else None
        headish = prev is not None and any(h.match(prev) for h in HEADGUARD)
        if prev is not None and not headish and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

def group(a, b):
    return ' '.join(harvest(a, b))

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'(\w)- (?=[a-z])', r'\1'),
 # the scan's li/ll -> U decay
 (r'\bUttle\b', 'little'), (r'\bhttle\b', 'little'), (r'\bUke\b', 'like'),
 (r'\bUkely\b', 'likely'), (r'repUes', 'replies'), (r'repUed', 'replied'),
 (r'rephed', 'replied'), (r'repHes', 'replies'), (r'intelHgence', 'intelligence'),
 (r'intelUgence', 'intelligence'), (r'InteUigence', 'Intelligence'),
 (r'IntelUgence', 'Intelligence'), (r'\bbeheve\b', 'believe'),
 (r'\bbeUeve\b', 'believe'), (r'aUenists', 'alienists'),
 (r'estabUsh', 'establish'), (r'pubUsh', 'publish'), (r'appHed', 'applied'),
 (r'famiharize', 'familiarize'), (r'\bhke\b', 'like'), (r'\bUne\b', 'line'),
 (r'\bUst\b', 'list'), (r'reahzed', 'realized'), (r'reaUzed', 'realized'),
 (r'Hkely', 'likely'), (r'quaUties', 'qualities'), (r'dehcacy', 'delicacy'),
 (r'estabhsh', 'establish'), (r'deUneation', 'delineation'),
 (r'unskillful', 'unskillful'),
 # word-level shrapnel seen in the ranges carried
 (r'\bS3niipathetic\b', 'sympathetic'), (r'\bdecajdng\b', 'decaying'),
 (r'would \\>e possible', 'would be possible'), (r'\\>e', 'be'),
 (r'\bchnic\b', 'clinic'), (r'\bHttle\b', 'little'),
 (r'\^ould\b', 'would'), (r'char\^icter', 'character'),
 (r'\bmoronity\^?', 'moronity'), (r"'Hhe", '"the'), (r'\bdeHneation\b', 'delineation'),
 (r'\bthe  intelhgence\b', 'the intelligence'), (r'intelhgence', 'intelligence'),
 (r'\bsuperposable\b', 'superposable'),
 (r'\bmoronity\b,?\s*\^?\s*correspond', 'moronity correspond'),
 (r"''Try", '"Try'), (r"''", '"'),
 (r'\bfordinarily\b', 'for ordinarily'),
 (r'his subject\^', 'his subject.'), (r'\bgrstde\b', 'grade'),
 (r'\bAhstradt\b', 'Abstract'), (r'\brepl5ring\b', 'replying'),
 (r'\bnon- sensical\b', 'nonsensical'), (r'\bunwilhngness\b', 'unwillingness'),
 (r'\bwilhngness\b', 'willingness'),
 (r'\bconunence\b', 'commence'), (r'\bKESULTS\b', 'RESULTS'),
 (r'\bRESUiiTS\b', 'Results'), (r'\bemmierations\b', 'enumerations'),
 (r'\bimpUes\b', 'implies'), (r'\bserioug\b', 'serious'),
 (r'\bjive figures\b', 'five figures'), (r'\bdifi&culty\b', 'difficulty'),
 (r'\bdifficulty that could arise\b', 'difficulty that could arise'),
 (r"\^'bafouillage\"", '"bafouillage"'), (r"\^'", '"'),
 (r'\bhap-hazard\b', 'haphazard'), (r'his bravely master defends', 'his bravely master defends'),
 (r'\bone\^s\b', "one's"), (r"streams\.'\^", "streams."),
 (r'\breahty\b', 'reality'), (r'\breaHty\b', 'reality'),
 (r'\bestabUshed\b', 'established'), (r'\bestablished\b', 'established'),
 (r'\b6i this classification\b', 'of this classification'),
 (r'\bdesigned only\b', 'designed only'),
 (r'\bwill \'always\b', 'will always'),
 (r'\bgraph method\b', 'graphic method'),
 (r'\binteUigence\b', 'intelligence'), (r'\bintegrity\b', 'integrity'),
 (r'\bhierarchy\b', 'hierarchy'),
 # second round, read against the print
 (r'only, \^?f We', 'only. We'), (r'/We shall', 'We shall'), (r'state\., Furthermore', 'state. Furthermore'),
 (r'\bthreeyear\b', 'three-year'), (r'partial V aptitudes', 'partial aptitudes'),
 (r'frauds\. Y In order', 'frauds. In order'),
 (r'^I\. The Psychological Method The', 'The'),
 (r"it '\S* the result of long investigations", 'it is the result of long investigations'),
 (r'after- E wards', 'afterwards'), (r'\bobhged\b', 'obliged'),
 (r"indeed,' be", 'indeed, be'), (r'time\. f It seems', 'time. It seems'),
 (r'judgment, j What', 'judgment. What'), (r'faculty, j/the', 'faculty, the'),
 (r'importance J; to us', 'importance to us'), (r'intelHgent', 'intelligent'),
 (r"suggestion\.'", 'suggestion.'), (r'pecuhar', 'peculiar'),
 (r'sign minus — \)', 'sign minus (—)'),
 (r'the fraction in use is J\.', 'the fraction in use is ½.'),
 (r'one can have i, or J, etc\.', 'one can have ¼, or ¾, etc.'),
 (r'with the sign or —', 'with the sign + or —'),
 (r'for the streams\. Criticism', 'for the streams." Criticism'),
 (r"\*' 'Tis Hke", '"\'Tis like'), (r'not kind\. "', 'not kind."'),
 (r'not well\. "', 'not well."'), (r"one's hat\. \"", "one's hat.\""),
 (r'master defends\. "', 'master defends."'),
 (r'For the height/', 'For the height'),
 (r'adopted\.\^?\*?\^?$', 'adopted.'),
 (r'and is marked\.$', 'and is marked =.'),
 (r'this One has been passed', 'this one has been passed'),
 # caret shrapnel last
 (r'\^([A-Za-z])', r'\1'), (r'([A-Za-z])\^', r'\1'), (r'\^', ''),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

LABELS = [
 (re.compile(r'^I\. The Psychological Method$'), 'I. The Psychological Method'),
 (re.compile(r'^General Conditions of the Examination$'), 'General Conditions of the Examination'),
 (re.compile(r'^1\.\s*"?Le\s+Regard'), '1. "Le Regard"'),
 (re.compile(r'^27\.\s*Reply\s+to\s+an\s+Abstract\s+Question'), '27. Reply to an Abstract Question'),
 (re.compile(r'^30\.\s*(Ahstradt|Definitions)'), '30. Definitions of Abstract Terms'),
 (re.compile(r'^II\.\s*Necessity\s+of\s+Making'), 'Necessity of Making an Estimate of Results'),
]

def units_from(paras, first_label=None):
    us, label = [], first_label
    for p in paras:
        matched = False
        for rx, lab in LABELS:
            if rx.match(p):
                label = lab; matched = True; break
        if matched and label is not None and len(p) < 70:
            continue
        u = {'txt': emend(p)}
        if label: u['label'] = label; label = None
        us.append(u)
    return us

def gunit(txt, label, note=None):
    u = {'txt': emend(txt), 'label': label}
    if note: u['note'] = note
    return u

def post_split(us, marker):
    """Split one unit at a paragraph break the scan lost."""
    for i, u in enumerate(us):
        j = u['txt'].find(marker)
        if j > 0:
            rest = {'txt': u['txt'][j:].strip()}
            if u.get('note'): rest['note'] = u.pop('note')
            u['txt'] = u['txt'][:j].strip()
            us.insert(i + 1, rest)
            return us
    raise AssertionError(f'post_split found nothing: {marker!r}')

def post_join(us, prev_end, count=1):
    """Fold the next `count` units into the one ending with prev_end."""
    for i in range(len(us) - 1):
        if us[i]['txt'].endswith(prev_end):
            for _ in range(count):
                nxt = us.pop(i + 1)
                us[i]['txt'] += ' ' + nxt['txt']
                for f in ('label', 'note'):
                    if nxt.get(f) and not us[i].get(f):
                        us[i][f] = nxt[f]
            return us
    raise AssertionError(f'post_join found nothing: {prev_end!r}')

# -------------------------------------------------------------- sections
programm = units_from(harvest(1994, 2328))
post_split(programm, 'Furthermore, in the definition of this state')
post_split(programm, 'In order to recognize the inferior states')
post_split(programm, 'It seems to us that in intelligence there is a fundamental faculty')

TESTLIST = ('1. Le Regard. 2. Prehension Provoked by a Tactile Stimulus. '
 '3. Prehension Provoked by a Visual Perception. 4. Recognition of Food. '
 '5. Quest of Food Complicated by a Slight Mechanical Difficulty. '
 '6. Execution of Simple Commands and Imitation of Simple Gestures. '
 '7. Verbal Knowledge of Objects. 8. Verbal Knowledge of Pictures. '
 '9. Naming of Designated Objects. 10. Immediate Comparison of Two Lines '
 'of Unequal Lengths. 11. Repetition of Three Figures. 12. Comparison of '
 'Two Weights. 13. Suggestibility. 14. Verbal Definition of Known '
 'Objects. 15. Repetition of Sentences of Fifteen Words. 16. Comparison '
 'of Known Objects from Memory. 17. Exercise of Memory on Pictures. '
 '18. Drawing a Design from Memory. 19. Immediate Repetition of Figures. '
 '20. Resemblances of Several Known Objects Given from Memory. '
 '21. Comparison of Lengths. 22. Five Weights to be Placed in Order. '
 '23. Gap in Weights. 24. Exercise upon Rhymes. 25. Verbal Gaps to be '
 'Filled. 26. Synthesis of Three Words in One Sentence. 27. Reply to an '
 'Abstract Question. 28. Reversal of the Hands of a Clock. 29. Paper '
 'Cutting. 30. Definitions of Abstract Terms.')
for probe in ('Prehension  Provoked  by  a  Tactile', 'Suggestibility',
              'Verbal  Definition  of  Known', 'Reversal  of  the  Hands'):
    assert any(probe in l for l in lines[2400:3520]), f'test title missing: {probe}'

tests = units_from(harvest(2332, 2375))
tests += units_from(harvest(2377, 2432))
tests.append(gunit(TESTLIST, 'The thirty tests of 1905, in the order of the print',
    note=('The print describes each of the thirty in full — procedure and '
          'remarks; carried complete here are test 1 (the lowest rung of '
          'the scale), test 27 and test 30 (its highest); the rest are '
          'named, not carried.')))
tests += units_from(harvest(3354, 3410))
tests += units_from(harvest(3501, 3511))
tests += units_from(harvest(3513, 3574))
# the four sample sentences belong to one printed passage
post_join(tests, 'They are among those of medium difficulty.', count=4)

AGES = [
 ('Three years', 'Show eyes, nose, mouth (p. 184). Name objects in a '
  'picture (p. 188). Repeat 2 figures (p. 187). Repeat a sentence of 6 '
  'syllables (p. 186). Give last name (p. 194).'),
 ('Four years', 'Give sex (p. 195). Name key, knife, penny (p. 195). '
  'Repeat 3 figures (p. 196). Compare 2 lines (p. 196).'),
 ('Five years', 'Compare 2 boxes of different weights (p. 196). Copy a '
  'square (p. 198). Repeat a sentence of 10 syllables (p. 186). Count 4 '
  'sous (p. 200). Put together two pieces in a "game of patience" (p. 198).'),
 ('Six years', 'Repeat a sentence of 16 syllables (p. 186). Compare two '
  'figures from an esthetic point of view (p. 202). Define by use only, '
  'some simple objects (p. 202). Execute 3 simultaneous commissions '
  '(p. 205). Give one\'s age (p. 206). Distinguish morning and evening (p. 206).'),
 ('Seven years', 'Indicate omissions in drawings (p. 207). Give the '
  'number of fingers (p. 209). Copy a written sentence (p. 209). Copy a '
  'triangle and a diamond (p. 209). Repeat 5 figures (p. 210). Describe '
  'a picture (p. 210). Count 13 single sous (p. 210). Name 4 pieces of '
  'money (p. 211).'),
 ('Eight years', 'Read selection and retain two memories (p. 211). Count '
  '9 sous, 3 single and 3 double (p. 214). Name four colors (p. 215). '
  'Count backward from 20 to 0 (p. 215). Compare 2 objects from memory '
  '(p. 216). Write from dictation (p. 216).'),
 ('Nine years', 'Give the date complete — day, month, day of the month, '
  'year (p. 217). Name the days of the week (p. 218). Give definitions '
  'superior to use (p. 205). Retain 6 memories after reading (p. 220). '
  'Make change, 4 sous from 20 sous (p. 218). Arrange 5 weights in order (p. 220).'),
 ('Ten years', 'Name the months (p. 221). Name 9 pieces of money '
  '(p. 221). Place 3 words in 2 sentences (p. 222). Answer 3 '
  'comprehension questions (p. 224). Answer 5 comprehension questions (p. 226).'),
 ('Eleven years', 'Criticize sentences containing absurdities (p. 227). '
  'Place 3 words in 1 sentence (p. 229). Find more than 60 words in 3 '
  'minutes (p. 229). Give abstract definitions (p. 230). Place '
  'disarranged words in order (p. 231).'),
 ('Twelve years', 'Repeat 7 figures (p. 232). Find 3 rhymes (p. 232). '
  'Repeat a sentence of 26 syllables (p. 230). Interpret pictures '
  '(p. 193). Problem of facts (p. 233).'),
 ('Thirteen years', 'Paper cutting (p. 234). Reversed triangle (p. 235). '
  'Give differences of meaning (p. 235).'),
]
for frag in ('Show  eyes,  nose,  mouth', 'Give  sex', 'Name  the  months',
             'Find  3  rhymes', 'Paper  cutting'):
    assert any(frag in l for l in lines[15195:15335]), f'age-grid anchor missing: {frag}'

skala = units_from(harvest(15083, 15196))
post_join(skala, 'will very often need to refer to it.')   # "(For discussion see pages indicated)"
for lab, txt in AGES:
    skala.append(gunit(txt, lab))
skala[-1]['note'] = ('The print restores this list in two columns; the '
                     'column interleaving of the scan for ages ten to '
                     'thirteen has been reordered against the page '
                     'references. The revision of 1911 redistributes '
                     'several tests and extends the scale — the module\'s '
                     'named next step.')
skala += units_from(harvest(15334, 15346))

niveau = units_from(harvest(15348, 15422))
niveau.append(gunit(group(15424, 15495),
    'The absurd replies — examples deserving the exclamation point'))
niveau += units_from(harvest(15497, 15623))

# attach the extracted footnotes
allus = programm + tests + skala + niveau
for target, seg in PENDING_NOTES:
    seg = emend(cleanup(seg))
    hit = [u for u in allus if target in u['txt']]
    assert len(hit) >= 1, f'note target not found: {target!r}'
    if not hit[0].get('note'): hit[0]['note'] = seg
    else: hit[0]['note'] += ' — ' + seg

# the forward pointer the print gives at the compensating rule
rule = [u for u in niveau if 'compensating rule' in u['txt']]
assert rule, 'compensating-rule unit missing'
rule[0]['note'] = ('The print\'s footnote here points forward: "For final '
                   'rule see p. 278" — the revision of 1911, this '
                   'module\'s named next step.')

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
    ('programm', 'The problem and the definition — "New Methods" (1905), the opening complete', programm),
    ('tests', 'The instrument of 1905 — recommendations, the thirty tests, the scoring', tests),
    ('skala', 'The scale of 1908 — conditions of the examination, and the tests age by age', skala),
    ('niveau', 'The mental level (1908) — recording, absurdities, and the rule', niveau),
]:
    nu = numbered(us, k); k += len(us)
    secs.append({'id': sid, 'titel': titel, 'units': nu})

out = {
 'id': 'binet',
 'autor': 'Alfred Binet · Théodore Simon',
 'titel': 'The Development of Intelligence in Children (1905–1911; Kite\'s English of 1916) — selections',
 'jahr': 1905,
 'zitierweise': 'DIC [k]',
 'quelle': ("Selections from Elizabeth S. Kite's translation (Vineland, "
            "N.J.: The Training School, 1916; public domain), Internet "
            "Archive developmentofint00binerich, OCR emended against the "
            "sense. Carried: the opening of 'New Methods for the "
            "Diagnosis of the Intellectual Level of Subnormals' (1905) "
            "complete, with the definition of intelligence as judgment; "
            "from the 1905 instrument the general recommendations, test "
            "1 complete, the printed list of the thirty tests, tests 27 "
            "and 30 complete, and the scoring rubric; from 'The "
            "Development of Intelligence in the Child' (1908) the "
            "General Conditions of the Examination, the classification "
            "of the tests by age (three to thirteen, the scan's "
            "two-column shred restored against the print's page "
            "references), and the Estimate of Results through the rule "
            "of the mental level. Two editorial and two authorial "
            "page-bottom footnotes are carried as notes; the French "
            "papers of 1905–1911 in L'Année Psychologique are named, "
            "not carried; the 1911 revision (ch. V of the volume) is "
            "the module's named next step. Paragraph numbering k runs "
            "across the four selections, so a citation 'DIC [k]' is "
            "unique."),
 'hinweis': ("The intelligence test itself, and with it the ancestral "
             "form of every benchmark: graded tasks, age norms, a "
             "scoring rubric (plus, minus, fraction — and the "
             "exclamation point for the absurd reply), protocol "
             "discipline for the examiner, and a rule for computing the "
             "mental level. Binet's own warning is carried with it: it "
             "is 'not an automatic method comparable to a weighing "
             "machine' — the results 'have no value if deprived of all "
             "comment; they need to be interpreted.'"),
 'sections': secs,
}

path = os.path.join(REPO, 'data', 'binet.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s['units']) for s in secs], '=', k - 1, 'units')
for s in secs:
    print(f"[{s['id']}]")
    print('  >', s['units'][0]['txt'][:95])
    print('  <', s['units'][-1]['txt'][:95])
