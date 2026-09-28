# -*- coding: utf-8 -*-
# Build data/hull_aptitude.json — Clark L. Hull, Aptitude Testing
# (Yonkers-on-Hudson: World Book Company, 1928; Measurement and Adjustment
# Series, ed. Lewis M. Terman). Source: Internet Archive
# aptitudetesting00hull (Harold B. Lee Library copy; djvu text, downloaded
# on demand into tools/.cache/). US public domain since 1 January 2024.
# Three selections:
#   stichprobe — ch. I, pp. 1-5: the test of life itself, and the test as a
#                'judicious sampling of human behavior';
#   grenze     — ch. VIII, pp. 273-278: the correlation coefficient against
#                forecasting efficiency, and why the yield of test batteries
#                is always limited (Table 61 rendered as lists);
#   maschine   — ch. XI, pp. 355-356, machines for scoring tests automatically,
#                and ch. XIV, pp. 487-490, 'A machine which makes aptitude
#                forecasts automatically'.
# Tables, formulas and the army-test specimens were read from the page
# images (leaf = page + 19) and are restored by hand; OCR otherwise
# emended against the sense.
# Usage: python tools/build-hull-aptitude.py [--dump]
import io, json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'hull_apt.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/aptitudetesting00hull/aptitudetesting00hull_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

def L(n, frag):
    assert frag in lines[n - 1], (n, frag, lines[n - 1])
    return n

RANGES = {
 'stichprobe': [(L(813, 'THE most accurate method'), L(996, 'remaining words of the language.'))],
 'grenze':     [(L(13174, 'The yield of aptitude batteries'), L(13182, 'given in Table 60.')),
                (L(13256, 'The low forecasting efficiency'), L(13409, 'almost without value.'))],
 'maschine':   [(L(16954, 'MACHINES FOR SCORING'), L(16980, 'human inaccuracy.')),
                (L(23390, 'Another system of making'), L(23491, 'guidance for the masses'))],
}

HEAD = re.compile(r'^(\d+\s*)?(Aptitude Testing|Introduction|Composition and Yield of Test Batteries|'
                  r'Combining Tests to Secure Maximum Efficiency|Administering Preliminary Test Battery)'
                  r'(\s*\d+)?$|^\d{1,3}$')

def is_head(s):
    s2 = re.sub(r'[_|]', '', s).strip()
    if HEAD.match(s2): return True
    letters = re.sub(r'[^A-Za-z]', '', s2)
    return len(letters) >= 6 and len(s2) < 75 and sum(c.isupper() for c in letters) / len(letters) > .8

def is_noise(s):
    return not re.search(r'[A-Za-z]{3}', s) and len(s) < 10

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
        if merged and (re.match(r'^[a-z\)\],;:]', p) or re.search(r'[a-z,;—-]$', merged[-1])):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

FIXES = [
 (r'[“”]', '"'), (r'[‘’]', "'"),
 (r'\s+([;:,!?]|\.(?!\d))', r'\1'),
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'\beconomie loss\b', 'economic loss'), (r'there is\. arising', 'there is arising'),
 (r'which rs not at the same time', 'which is not at the same time'),
 (r'^_ Many methods', 'Many methods'), (r'\bjadvocated\b', 'advocated'), (r"'value, some", 'value, some'),
 (r"'certain others", 'certain others'), (r'/These tests', 'These tests'), (r'/ such as', 'such as'),
 (r'\| (?=[a-z])', ''), (r'aptitude "psychologist', "aptitude psychologist"),
 (r'\bformule\b', 'formulae'), (r'\bcodrdinated\b', 'coördinated'),
]

def emend(t):
    for a, b in FIXES:
        t = re.sub(a, b, t)
    return re.sub(r'\s+', ' ', t).strip()

secs = {}
for sid, rs in RANGES.items():
    us = []
    for a, b in rs:
        us += [{'txt': emend(p)} for p in harvest(a, b)]
    secs[sid] = us

# ------------------------------------------------------------ repairs
def U(sid, frag):
    hit = [u for u in secs[sid] if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {sid} {frag!r}'
    return hit[0]

def fix(u, old, new):
    assert old in u['txt'], (old, u['txt'][:80])
    u['txt'] = u['txt'].replace(old, new)

IMG = ' Read from the page image.'

# --- ch. I
S = secs['stichprobe']
u = U('stichprobe', 'Human-aptitude testing is not essentially')
fix(u, "'The thing, sampled", 'The thing sampled')
fix(u, ' atta A psychological test 1s', ' A psychological test is')
fix(u, 'indwidual', 'individual'); fix(u, "'This will", 'This will')
i = u['txt'].find('A psychological test is')
S.insert(S.index(u) + 1, {'txt': u['txt'][i:]}); u['txt'] = u['txt'][:i].strip()
u = U('stichprobe', 'disarranged-sentence test')
i = u['txt'].find('such as:') + len('such as:')
j = u['txt'].find('He is directed')
spec = {'txt': ('oranges yellow are . . . true — false / noise cannon never make a . . . '
                'true — false / to life water is necessary . . . true — false / leaves the '
                'trees in lose their fall . . . true — false / forget trifling friends '
                'grievances never . . . true — false'),
        'note': 'The five specimen sentences of the army test, set as printed (p. 4).' + IMG}
rest = {'txt': u['txt'][j:]}
u['txt'] = u['txt'][:i]
k = S.index(u); S[k + 1:k + 1] = [spec, rest]
for x in S:
    x['txt'] = x['txt'].replace('codrdination', 'coördination').replace('THE most accurate', 'The most accurate')

# --- ch. VIII: the section is rebuilt around the tables and formulas that
# broke its OCR; the prose units come from the harvest, the rest from the
# page images (pp. 273-278).
G = {x['txt'][:40]: x for x in secs['grenze']}
def g(frag):
    return U('grenze', frag)
yield_ = g('The yield of aptitude batteries')
yield_['note'] = ('Table 60, which converts R into per cent of forecasting efficiency E, and '
                  'Figure 36, its graph (p. 274), are not reproduced.')
striking = {'txt': ('Perhaps the most striking point about this table is the remarkably small '
    'forecasting efficiencies corresponding to R values below .50. The same general tendency '
    'may be seen in the fact that the forecasting efficiency arises as much (20 points) between '
    'correlations .98 and 1.00 as between correlations .00 and .60! It is important to observe '
    'that this zone of extremely low forecasting efficiency is exactly the zone where practically '
    'all modern aptitude correlations fall. To the enthusiastic user of tests this may be somewhat '
    'disappointing, but the sooner these facts are fully realized the better for all.'),
    'note': 'The paragraph runs across Table 60 and Figure 36 (pp. 273–275).' + IMG}
low = g('The low forecasting efficiency of modern tests'); low['txt'] = low['txt'].rstrip(' |')
question = g('What is a high and what is a low correlation?')
fn1 = g('This statement assumes that the correlation coefficients')['txt']
fn1 = fn1[fn1.find('1 This statement') + 2:]
fn2 = g('It should also be added that tests showing')['txt'].rstrip(" '")
scale = {'txt': ('Below .45 or .50, practically useless for differential prognosis. / From .50 to .60, '
                 'of some value / From .60 to .70, of considerable value / From .70 to .80, of '
                 'decided value but rarely found / Above .80, not obtained by present methods'),
         'note': 'Page-bottom footnote: "' + fn1 + ' ' + fn2 + '"'}
why = {'txt': ('In view of the low forecasting efficiency of aptitude tests, the question as to its '
               'cause naturally arises. The answer has considerable significance, not only for the '
               'present but for the future possibilities of aptitude testing as well.')}
agg = g('If we could isolate and measure separately')['txt']
agg = agg[:agg.find(' 1 This statement')]
tail = g('weighted by the nature of the behavior involved')['txt']
tail = tail[tail.find('weighted by the nature'):]
aggregates = {'txt': agg + ' ' + tail,
              'note': 'So the text; in Table 61 as printed, Test (1) carries determiner III with weight 3.'}
table = {'txt': ('Table 61. Showing a typical test-aptitude situation in terms of determiners. Every '
    'determiner of the aptitude is touched by one or more of the tests, yet the battery yields an '
    'R of only .53. — Aptitude (0): I 2, III 4, V 2, VI 3, VIII 1, XI 1, XIII 3. Test (1): III 3, '
    'IV 4, V 1, X 2. Test (2): VI 3, VII 4, VIII 1, XII 2. Test (3): I 5, II 3, III 1, VII 2. '
    'Test (4): IV 3, IX 4, XI 2, XIII 1.'),
    'note': 'The table (p. 277) given as lists: each determiner with its weight.' + IMG}
reality = g('The reality of the conditions described above')
coeffs = {'txt': ('The various correlation coefficients as computed from the determiners by formula, '
    'page 231, are as follows: r01 = +.385; r02 = +.275, r12 = .00; r03 = +.338, r13 = +.087, '
    'r23 = +.233; r04 = +.137, r14 = +.400, r24 = .00, r34 = .00.'),
    'note': 'The coefficients (p. 278).' + IMG}
final = g('These correlation coefficients are fairly typical')
fix(final, 'equation,! the', 'equation, the')
final['note'] = ('Page-bottom footnote: "It is also a matter of considerable theoretical interest to '
    'observe that despite the fact that no negative determiner is to be found in Table 61, the '
    'regression equation contains a negative weight for test No. 4. Assuming all means and '
    'standard deviations to be unity, the equation is: X̄0 = .171 + .376 X1 + .215 X2 + .256 X3 '
    '− 009 X4 [so printed, for −.009]. The moral of this is, of course, that the regression '
    'equation, just as partial correlation (pages 250 ff.), may be an utterly misleading instrument '
    'for purposes of theoretical analysis of aptitude determiners. But if the multiple-regression '
    'equation is regarded as primarily a practical estimating or forecasting device, all of the '
    'mystery of this negative weight vanishes. It means that test No. 4 can contribute more to the '
    'yield of the battery as a whole by receiving a negative weight. An inspection of Table 61 '
    'suggests that this probably results from the fact that by weighting test No. 4 negatively '
    'there will result a tendency to neutralize in test No. 1 the influence of the irrelevant '
    'determiner IV, since this determiner appears prominently in both tests. Clearly test No. 1 '
    'would be much stronger with the influence of this irrelevant determiner eliminated." '
    '(p. 278, read from the page image)')
secs['grenze'] = [yield_, striking, low, question, scale, why, aggregates, table, reality, coeffs, final]
for x in secs['grenze']:
    x['txt'] = x['txt'].replace('multipleregression', 'multiple-regression')

# --- the machines
u = U('maschine', 'This would represent Fic. 60.')
i = u['txt'].find(' Fic. 60.'); j = u['txt'].find(' a huge amount of labor')
cap = u['txt'][i:j].strip().replace('Fic. 60.', 'Fig. 60.')
u['txt'] = u['txt'][:i] + u['txt'][j:]
u['note'] = ('Figure 60 (p. 488), reproduced as this module\'s plate; its legend: "' + cap[len('Fig. 60. '):] + '" — The '
             'numbers in parentheses refer to the chapter bibliography, not carried.')
u = U('maschine', 'The youth whose potential aptitudes are thus')
fix(u, 'thus 490 im Aptitude Testing recorded', 'thus recorded')
for x in secs['maschine']:
    x['txt'] = x['txt'].replace("'The test scores", 'The test scores').replace("'These may", 'These may')
U('maschine', 'Pressey has recently exhibited')['note'] = (
    'From ch. XI, "Administering the preliminary test battery to a trial group of subjects", under the heading "Machines for '
    'scoring multiple-choice tests automatically" (pp. 355–356).')
U('maschine', 'Another system of making aptitude predictions')['note_pre'] = None

L_ = [
 ('stichprobe', 'the test of life itself', 'The test of life itself'),
 ('stichprobe', 'Testing in all the applied sciences', 'Psychological testing a judicious sampling of human behavior'),
 ('stichprobe', 'A psychological test is the measurement', 'The test as a sample of behavior'),
 ('grenze', 'exactly the zone where practically', 'The zone where all modern correlations fall'),
 ('grenze', 'Below .45 or .50, practically useless', 'What is a high and what is a low correlation?'),
 ('grenze', 'In view of the low forecasting efficiency', 'Why the yield from test batteries is always limited'),
 ('grenze', 'absolutely all of the determiners', 'All the determiners, and almost no value'),
 ('maschine', 'Pressey has recently exhibited', 'Machines for scoring tests automatically'),
 ('maschine', 'Another system of making aptitude predictions', 'A machine which makes aptitude forecasts automatically'),
 ('maschine', 'ringing a bell to call the attendant', 'The card of forecasts'),
 ('maschine', 'vocational guidance for the masses', 'Every large school system'),
]
for sid, frag, lab in L_:
    U(sid, frag)['label'] = lab
for s in secs.values():
    for x in s:
        x.pop('note_pre', None)

if '--dump' in sys.argv:
    for sid, us in secs.items():
        print('=====', sid)
        for i, u in enumerate(us):
            print(i + 1, '|', u.get('label',''), '|', u['txt']); u.get('note') and print('   NOTE:', u['note'])
    raise SystemExit

TITLES = {
 'stichprobe': 'Ch. I — the test of life, and the test as a sample of behavior (pp. 1–5)',
 'grenze': 'Ch. VIII — forecasting efficiency, and why the yield of test batteries is always limited (pp. 273–278)',
 'maschine': 'Chs. XI and XIV — machines that score tests and make aptitude forecasts (pp. 355–356, 487–490)',
}
k, out_secs = 1, []
for sid, us in secs.items():
    units = []
    for i, u in enumerate(us):
        units.append(dict({'n': i + 1, 'k': k}, **u)); k += 1
    out_secs.append({'id': sid, 'titel': TITLES[sid], 'units': units})

out = {
 'id': 'hull_aptitude',
 'autor': 'Clark L. Hull',
 'titel': 'Aptitude Testing (1928) — selections',
 'jahr': 1928,
 'zitierweise': 'AT [k]',
 'quelle': ("Selections from the first printing (Yonkers-on-Hudson: World Book Company, 1928; "
            "Measurement and Adjustment Series, ed. Lewis M. Terman), Internet Archive "
            "aptitudetesting00hull (Harold B. Lee Library copy), public domain in the United "
            "States since 1 January 2024. OCR emended against the sense; the army-test "
            "specimens, Table 61, the correlation coefficients and the regression equation were "
            "read from the page images and are restored by hand, Table 61 given as lists. "
            "Carried: ch. I, pp. 1–5; ch. VIII, pp. 273–278 (Table 60 and Figure 36 not "
            "reproduced); the machines for scoring tests from ch. XI, pp. 355–356; and the "
            "forecasting machine that closes ch. XIV and the book's text, pp. 487–490. Cited as "
            "'AT [k]', k unique across the three selections."),
 'hinweis': ("The measured mind turned into an apparatus. Hull defines the test as a "
             "'judicious sampling of human behavior', measures his own instruments without "
             "illusion — batteries correlating below .45 or .50 are 'practically useless', and "
             "a battery may touch every determiner of an aptitude and still be 'almost without "
             "value' — and then designs the machine: test scores punched on paper tape, forty "
             "or fifty forecasting formulae on a metal band 'somewhat resembling a music roll', "
             "a card stamped with the forecasts for 'all the chief type occupations of the "
             "world', and a bell to call the attendant. Prediction handed to a machine, with its "
             "author's own measure of how little the predictions can know."),
 'sections': out_secs,
}
path = os.path.join(REPO, 'data', 'hull_aptitude.json')
json.dump(out, io.open(path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s['units']) for s in out_secs], 'units')
