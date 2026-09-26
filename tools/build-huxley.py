# -*- coding: utf-8 -*-
# Build data/huxley.json — T. H. Huxley, "On the Hypothesis that Animals
# are Automata, and its History" (1874), complete. Source: Collected
# Essays, vol. I: Method and Results (Macmillan), Internet Archive
# methodandresult01huxlgoog, djvu OCR (downloaded on demand into
# tools/.cache/), the essay at printed pp. 199-250. Running heads, page
# numbers and signature marks dropped (including the badly shredded
# variants: AX7T0MATISM, ANDCAL); the address's footnotes are not
# carried, except that the reference for the long Bonnet quotation is
# kept as a note on its closing paragraph. The small-caps heading of
# Bonnet's quoted chapter becomes a label. OCR emended against the sense
# via FIXES; the print's quote-marks, mangled to ** and '' by the OCR,
# are normalised to plain double quotes.
# Usage: python tools/build-huxley.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'huxley.txt')
if not os.path.exists(SRC):
    url = ('https://archive.org/download/methodandresult01huxlgoog/'
           'methodandresult01huxlgoog_djvu.txt')
    urllib.request.urlretrieve(url, SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

A, B = 7714, 9776   # essay body: after the title block, before essay VI

NOISE = re.compile(r'^\s*(\d{1,3}|[ivxlIVXL]+|[A-Za-z]|\[1874\]|17)\s*$')
FOOT = re.compile(r'^\s*1\s+\S|^\s*1\s*$|HikUer|Prima Lintcc')

def is_head(s):
    return (re.search(r'A\w*T[0O][MK]AT[I1]SM', s) and len(s) < 45) or \
           s.startswith('Digitized by') or \
           re.match(r'^\s*(ON THE HYPOTHESIS|ARE AUTOMATA)', s)

paras, buf = [], []
for raw in lines[A - 1:B]:
    s = raw.strip()
    if is_head(s) or NOISE.match(s) or FOOT.match(s):
        continue
    if not s:
        if buf: paras.append(' '.join(buf)); buf = []
    else:
        buf.append(s)
if buf: paras.append(' '.join(buf))

clean = []
for p in paras:
    if p.startswith('^'):   # footnote block (its lowercase continuations merge into it upstream)
        continue
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'\s*\^', '', p)
    p = re.sub(r'\b\d{1,3} AN\w* A\w*T[0O][MK]AT[I1]SM[ yv]*', ' ', p)  # inline head remnant
    p = re.sub(r"^[\*']{1,3}\s*", '"', p)                          # OCR'd opening quote-marks
    p = re.sub(r'\s+', ' ', p).strip()
    if len(p) > 1: clean.append(p)

# two footnotes arrive without their caret markers: the Malebranche
# footnote's shredded continuation, and the Locke note on Descartes'
# illustration — drop both, as footnotes are not carried
clean = [p for p in clean if 'Malebran' not in p and not p.startswith('Locke {Human')]

merged = []
for p in clean:
    cont = re.match(r'^[a-z\)\],;:]', p) or \
        (merged and re.search(r'[a-z,]$', merged[-1]) and not p.startswith('"'))
    if merged and cont:
        merged[-1] += ' ' + p
    else:
        merged.append(p)

FIXES = [
    (r'\bmodem\b', 'modern'), (r'— \^?', '— '),
    (r'\bwiU\b', 'will'), (r'\bHaUer\b', 'Haller'), (r'\bcaUed\b', 'called'),
    (r'\baU\b', 'all'), (r'\bshaU\b', 'shall'), (r'\bfuU\b', 'full'),
    (r'\bstiU\b', 'still'), (r'\bweU\b', 'well'), (r'\bwm\b', 'will'),
    (r"''", '"'),
    (r"de TAme", "de l'Ame"),
    (r'\breceiyed\b', 'received'), (r'\bpropoeitioii\b', 'proposition'),
    (r'\bextomal\b', 'external'), (r'\baD7\b', 'any'),
    (r'\bdetenoination\b', 'determination'),
    (r'Akothbr Hypothesis concerkiko thb Mechakibm', 'Another Hypothesis concerning the Mechanism'),
    (r'OF iDEAti', 'of Ideas'),
    (r"brain, '", 'brain,'),
    (r'\bmoliecular\b', 'molecular'),
    (r'UnderstaTiding', 'Understanding'),
    (r'Book 11\., chap\. viii\. 37\) naea', 'Book II., chap. viii., § 37) uses'),
    (r'\{Human', '(Human'),
    ('�', '—'),
]
for i, p in enumerate(merged):
    for pat, rep in FIXES:
        p = re.sub(pat, rep, p)
    merged[i] = re.sub(r'\s+', ' ', p).strip()

# The small-caps heading of Bonnet's quoted chapter arrives as two
# fragments; fold them into a label on the first quoted paragraph, and
# keep the quotation's printed reference as a note where it belongs.
units, label, note_for = [], None, None
for p in merged:
    if p.startswith('"Another Hypothesis concerning the Mechanism') or p == 'of Ideas':
        label = 'Bonnet: "Another Hypothesis concerning the Mechanism of Ideas"'
        continue
    if re.match(r'^\S{0,5}ai d[ce] Ps', p):
        note_for = 'Indifferent towards any determination'
        continue
    u = {'txt': p}
    if label: u['label'] = label; label = None
    units.append(u)
for u in units:
    if 'Essai de Psychologie " at length' in u['txt']:
        u['note'] = ("Huxley's footnote gives the source of the quotation: Bonnet, "
                     "Essai de psychologie, ch. xxvii.")
        break

units = [{'n': i + 1, 'k': i + 1, **u} for i, u in enumerate(units)]

out = {
 'id': 'huxley',
 'autor': 'Thomas Henry Huxley',
 'titel': 'On the Hypothesis that Animals are Automata, and its History (1874)',
 'jahr': 1874,
 'zitierweise': 'Aut. [n]',
 'quelle': ("The address of 1874 complete, from Collected Essays, vol. I: Method "
            "and Results (London: Macmillan), printed pp. 199–250; Internet "
            "Archive scan methodandresult01huxlgoog, OCR emended by hand against "
            "the sense. The address's footnotes are not carried, except that the "
            "reference for the long Bonnet quotation is kept as a note; the "
            "print's quotation marks are normalised; the paragraph numbers are "
            "this site's own. Public domain."),
 'hinweis': ("The automaton theory at full strength: Descartes's beast-machine "
             "retold and defended, the frog experiments as evidence, and the "
             "conclusion that we ourselves are conscious automata — consciousness "
             "a collateral product of the body's working. The debate about "
             "machine minds begins here, as a debate about our own."),
 'sections': [
   {'id': 'text', 'titel': 'The address, complete', 'units': units},
 ],
}

path = os.path.join(REPO, 'data', 'huxley.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', len(units), 'units')
print(' first:', units[0]['txt'][:100])
print(' last :', units[-1]['txt'][-120:])
short = [u['n'] for u in units if len(u['txt']) < 60]
print(' short:', short)
