# -*- coding: utf-8 -*-
# Build data/galton.json — Galton, Inquiries into Human Faculty and its
# Development (London: Macmillan, 1883), first edition. Source: Internet
# Archive inquiriesintohu00galtgoog (djvu text, downloaded on demand into
# tools/.cache/). Four selections:
#   prog        — the Introduction complete (pp. 1-2), and the paragraph of
#                 p. 24 whose footnote coins the word "eugenics" (the
#                 footnote carried as a note, in full);
#   composite   — Composite Portraiture complete (pp. 8-19);
#   imagery     — Mental Imagery: the questionnaire and its returns
#                 (pp. 83-93) and the closing passage on generic images and
#                 the use of the faculty (pp. 108-113); the middle of the
#                 chapter (pp. 93-108) is omitted and said so;
#   psychometric— Psychometric Experiments complete (pp. 185-203); the
#                 three tables are not reproduced, each place marked.
# The numbered survey returns and the octile scale are carried grouped, one
# unit per printed group. Running heads and page numbers dropped; OCR
# emended by hand against the sense, the worst passages verified against
# the page images (leaf = page + 19).
# Usage: python tools/build-galton.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
SRC = os.path.join(CACHE, 'galton.txt')
if not os.path.exists(SRC):
    urllib.request.urlretrieve(
        'https://archive.org/download/inquiriesintohu00galtgoog/'
        'inquiriesintohu00galtgoog_djvu.txt', SRC)
lines = io.open(SRC, encoding='utf-8', errors='replace').read().splitlines()

# ---------------------------------------------------------------- RAWFIX
# Whole-line repairs for shredded OCR, each verified against the page image
# or reconstructed from the immediate sense. (line_no, must_contain, new).
RAWFIX = [
 (560, 'differences in different', 'differences in different families and races, to learn how'),
 (569, 'may have shown', 'far history may have shown the practicability of sup-'),
 (576, 'collateml', 'with collateral considerations that a straightforward'),
 (577, 'step', 'step-by-step inquiry did not seem to be the most'),
 (825, 'photographic', 'method; it was this — (1) I collected photographic'),
 (826, 'persons', 'portraits of different persons, all of whom had been'),
 (870, 'now use', 'of that which I now use are different and complex.'),
 (881, 'traits in common', 'peculiarities. There are so many traits in common in'),
 (920, 'discover that they disagreed', 'was, to discover that they disagreed. I have even'),
 (955, 'Stuart Poole', 'for me by Mr. R. Stuart Poole from the collection in'),
 (967, 'got rid of', 'dental momentary expressions are got rid of, which'),
 (973, 'composites', 'The next pair of composites (full face and profile)'),
 (992, 'When did you do this portrait', "casually. She said, 'When did you do this portrait of A? how"),
 (993, 'never thought they were so like', 'like she is to B! Or is it B? I never thought they were so like'),
 (997, "for certain", 'is one of the family for certain, but I don\'t know which.\'"'),
 (1004, 'on our own basis', 'our individuality, and to stand on our own basis, and'),
 (1056, 'race might most easily', 'English race might most easily be improved. It is'),
 (1091, 'breeding true', 'breeding true to their kind have become established,'),
 (1127, 'ideal expression', 'medley group results in an ideal expression.'),
 (1231, 'auperpo', 'required, at the same time that it superposes the'),
 (3655, 'llustrate', 'results might illustrate the essential differences be-'),
 (3656, 'of different men', 'tween the mental operations of different men, that'),
 (3657, 'origin of visions', 'they might give some clue to the origin of visions,'),
 (3664, 'steps to find out', 'earlier tentative steps to find out what I desired to'),
 (3683, 'first group', 'The first group of the rather long series of queries'),
 (3696, 'sharpest definition', 'same time, or is the place of sharpest definition at any one'),
 (3697, 'contracted', 'moment more contracted than it is in a real scene?'),
 (3701, 'distinct and natural', 'on the table, quite distinct and natural?"'),
 (3705, 'likely class of men', 'world, as they were the most likely class of men to'),
 (3706, 'answers concerning', 'give accurate answers concerning this faculty of'),
 (3713, 'novelists', 'visualising, to which novelists and poets continually'),
 (3720, 'men of science', 'majority of the men of science to whom I first applied'),
 (3721, 'unknown', 'protested that mental imagery was unknown to them,'),
 (3722, 'fantastic in', 'and they looked on me as fanciful and fantastic in'),
 (3726, 'really', 'supposing that the words "mental imagery" really'),
 (3727, 'everybody supposed them', 'expressed what I believed everybody supposed them'),
 (3728, 'to mean', 'to mean. They had no more notion of its true nature'),
 (3751, 'Many men and', 'disposition to prevail. Many men and a yet larger'),
 (3758, 'habitually saw', 'that they habitually saw mental imagery, and that'),
 (3759, 'of colour', 'it was perfectly distinct to them and full of colour.'),
 (3761, 'more I pressed', 'The more I pressed and cross-questioned them, pro-'),
 (3762, 'incredulous', 'fessing myself to be incredulous, the more obvious'),
 (3811, 'psychological questions', 'worthy replies to psychological questions. Many'),
 (3812, 'children', 'persons, especially women and intelligent children,'),
 (3813, 'introspe', 'take pleasure in introspection, and strive their very'),
 (3814, 'their menta', 'best to explain their mental processes. I think that'),
 (3817, 'to priests', 'ing themselves to priests.'),
 (3823, 'bility', 'bility; and the other is that scientific men, as a class,'),
 (4049, 'quotations clearly show', 'These quotations clearly show the great variety of'),
 (4050, 'natural powers of visual', 'natural powers of visual representation, and though'),
 (4066, 'Treating these', 'powers of Englishmen. Treating these according to'),
 (4067, 'statistics', 'the method described in the chapter of statistics, we'),
 (4747, 'easily explained', 'such purpose, as may be easily explained by an example.'),
 (4750, 'would be likely', 'What is the idea that the word "boat" would be likely'),
 (4769, 'barge', 'wherry, barge, launch, punt, or dingy. Much more did'),
 (4772, 'suppressing mental', 'habit of suppressing mental imagery must therefore'),
 (4776, 'characterise men', 'characterise men who deal much with abstract ideas;'),
 (4844, 'intellectual faculties', 'visualising power and the intellectual faculties than'),
 (4903, 'intellectual operations', 'to the higher intellectual operations. A visual image'),
 (4904, 'form of mental', 'is the most perfect form of mental representation,'),
 (4905, 'objects', 'wherever the shape, position, and relations of objects'),
 (4906, 'in space are concerned', 'in space are concerned. It is of importance in every'),
 (4923, 'picture galleries', 'they carry whole picture galleries in their minds.'),
 (4924, 'education tends to repress', 'Our bookish and wordy education tends to repress'),
 (7916, 'as much', 'ences, in order that it might retain as much freshness'),
 (8184, 'impression of', 'without our memory retaining any impression of its'),
 (8270, 'do', 'we had each of us forgotten. Our recollections do'),
 (8271, 'Actors and incidents', 'not tally. Actors and incidents that seem to have'),
 (8272, 'primary importance', 'been of primary importance in those events to the'),
 (8273, 'utterly forgotten', 'one have been utterly forgotten by the other. The'),
 (8274, 'in truth', 'recollections of our earlier years are, in truth, very'),
 (8278, 'associated ideas were', 'My associated ideas were for the most part due to'),
 (8279, 'experiences', 'my own unshared experiences, and the list of them'),
 (8294, 'Therefore one sees', 'experiments. Therefore one sees clearly, and I may'),
 (8295, 'measurably', 'say, one can see measurably, how impossible it is'),
 (8300, 'may convey', 'any given word in it may convey, will differ widely'),
 (8520, 'will be seen', 'It will be seen from the Table that out of the 48'),
 (8522, 'occurred in each', 'of them occurred in each of the four trials; of the 57'),
 (8530, 'other associations', 'the 19 other associations first formed in quite recent'),
 (8534, 'decrease of', 'mine the decrease of fixity as the date of their first'),
 (8535, 'remote', 'formation becomes less remote.'),
 (8539, 'wholly due', 'of the series, is wholly due to a visual memory of'),
 (8540, 'about this', 'places seen in manhood. I will not speak about this'),
 (8589, 'several trials', 'After several trials I found that the associated'),
 (8590, 'three main groups', 'ideas admitted of being divided into three main groups.'),
 (8592, 'First there is', '1. First there is the imagined sound of words, as in verbal'),
 (8597, 'the next group', '2. In the next group there was every other kind of sense'),
 (8606, 'last of the three groups', 'gether, visual imagery. 3. The last of the three groups'),
 (8628, 'King David', '"King David" occurred to me on one occasion in each'),
 (8635, 'So much for', 'So much for the character of the association;'),
 (8649, 'next as to that', 'next as to that of the words. I found, after the'),
 (8875, 'in excess', 'haps 20 in excess of what would have been expected'),
 (8877, 'wholly due', 'wholly due to visual imagery of scenes with which I'),
 (8929, 'grasp them', 'monly we grasp them very imperfectly, and cling to'),
 (9011, 'and that the mind', 'stock of ideas is narrowly limited, and that the mind'),
]
for n, must, new in RAWFIX:
    assert must in lines[n - 1], f'RAWFIX anchor missing at line {n}: {must!r} not in {lines[n-1]!r}'
    lines[n - 1] = new

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

def harvest(a, b, skips=()):
    """Paragraphs from djvu lines a..b. skips: (a2, b2, note) line ranges
    dropped whole; the note becomes a sentinel attached to the previous
    kept unit."""
    paras, buf = [], []
    ln = a
    while ln <= b:
        hit = next(((sa, sb, nt) for sa, sb, nt in skips if sa <= ln <= sb), None)
        if hit:
            if buf: paras.append(' '.join(buf)); buf = []
            paras.append('\x00NOTE:' + hit[2])
            ln = hit[1] + 1
            continue
        s = lines[ln - 1].strip()
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        elif not (is_head(s) or is_noise(s) or (digit_ratio(s) > .55 and len(s) > 3)):
            buf.append(s)
        ln += 1
    if buf: paras.append(' '.join(buf))
    out = []
    for p in paras:
        if p.startswith('\x00NOTE:'): out.append(p); continue
        p = cleanup(p)
        if len(p) > 2: out.append(p)
    merged = []
    for p in out:
        if p.startswith('\x00NOTE:'): merged.append(p); continue
        prev = merged[-1] if merged and not merged[-1].startswith('\x00NOTE:') else None
        if prev is not None and (
                re.match(r'^[a-z\)\],;:]', p) or
                (re.search(r'[a-z,;—-]$', prev) and p[:1] not in '"\'')):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

def group(a, b, drop=()):
    """Harvest a range and join every paragraph into one text block."""
    ps = [p for p in harvest(a, b) if not p.startswith('\x00NOTE:')]
    ps = [p for p in ps if not any(re.match(d, p) for d in drop)]
    return ' '.join(ps)

# ---------------------------------------------------------------- fixes
FIXES = [
 # line-break hyphens that survive into merged units
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'\bdifl[fF]er', 'differ'), (r'\bdifier', 'differ'), (r'\bdiff er', 'differ'),
 (r'diflSculty|difiiculty|diflBculty|difl&culty', 'difficulty'),
 (r'suflScient|suflicient|suflEicient|sufl&cient', 'sufficient'),
 (r'oflScer|oflBcer', 'officer'), (r'efl[fF]ort', 'effort'),
 (r'efl[fF]ect|\befiect\b', 'effect'), (r'afl[fF]ord', 'afford'),
 (r'\bwiU\b', 'will'), (r'\bstiU\b', 'still'), (r'\bsmaU\b', 'small'),
 (r'\bfuU\b', 'full'), (r'\baU\b', 'all'), (r'\bcaU\b', 'call'),
 (r'\bweU\b', 'well'), (r'\bUght\b', 'light'), (r'\bviUa\b', 'villa'),
 (r'\bUke\b', 'like'), (r'\bihe\b', 'the'), (r'\bIhe\b', 'The'),
 (r'\bmodem\b', 'modern'), (r'\bveiy\b', 'very'), (r'\baud\b', 'and'),
 (r'&mily|feimily', 'family'), (r'\bfamished\b', 'furnished'),
 (r'\bfiEtces\b', 'faces'), (r'\bEeassured\b', 'Reassured'),
 (r'\bKoyal\b', 'Royal'), (r'\bimtil\b', 'until'), (r'\bimder\b', 'under'),
 (r'\bthipk\b', 'think'), (r'\bthai\b', 'that'), (r'\blyould\b', 'would'),
 (r'\bpraxjtice\b', 'practice'), (r'\bdiminislied\b', 'diminished'),
 (r'\bwhicb\b', 'which'), (r'\bffiwt\b', 'fact'), (r'\babsolutdy\b', 'absolutely'),
 (r'\baad\b', 'and'), (r'\bhimdred\b', 'hundred'), (r'\bindiBtinct\b', 'indistinct'),
 (r'l\)reakfa8t', 'breakfast'), (r'\bmisly\b', 'misty'),
 (r'SuboctUe', 'Suboctile'), (r'\bOciile\b|\bOctik\b|\bOcHle\b', 'Octile'),
 (r'\bQuartiU\b|\bQuoriile\b', 'Quartile'), (r'\bscena\b', 'scene.'),
 (r'\brebollect\b', 'recollect'), (r'\biniages\b', 'images'),
 (r'\bca31\b', 'call'), (r'\ba ttitudinise\b', 'attitudinise'),
 (r'\befiective\b', 'effective'), (r"lady\^s", "lady's"),
 (r'/Strategists', 'Strategists'), (r'\bPr4cis\b', 'Précis'),
 (r'\bancl\b', 'and'), (r'j\)f\b', 'of'), (r'\bleafit\b', 'least'),
 (r'\bfonn\b', 'form'), (r'\bair this\b', 'all this'), (r'\btf&d\b', 'and'),
 (r'\bprecautiona\b', 'precautions'), (r'\bunoettain\b', 'uncertain'),
 (r'\bnot fell to be\b', 'not felt to be'), (r'fact&', 'facts.'),
 (r'\bqaestions\b', 'questions'), (r'\breaUty\b', 'reality'),
 (r'\barc carried\b', 'are carried'), (r'\bleaxn\b', 'learn'),
 (r'famiUes', 'families'), (r'practicabiKty', 'practicability'),
 (r'\bwaa\b', 'was'), (r'\bWe ore\b', 'We are'), (r't3rpe', 'type'),
 (r'\baa\b', 'as'), (r'\bcentiral\b', 'central'), (r'\biypes\b', 'types'),
 (r'\bportaits\b', 'portraits'), (r'\\dth', 'with'),
 (r'hal\^enny', 'halfpenny'), (r'l\^\^psed', 'lapsed'),
 (r'bri\^tness', 'brightness'), (r'\be\^\. ', 'e.g. '),
 (r'breakfast- table', 'breakfast-table'), (r'\bfouroared\b', 'four-oared'),
 (r'\brewritten\b', 're-written'), (r'\bhalfconscious\b', 'half-conscious'),
 (r'\bftequently\b', 'frequently'), (r'parrot-Uke', 'parrot-like'),
 (r'n\^achine', 'machine'), (r'jBrequent', 'frequent'),
 (r'i;han', 'than'), (r'\bfax\b', 'far'), (r'\btrialfl\b', 'trials'),
 (r'Q,bstract', 'abstract'), (r'pre- Bsnted', 'presented'),
 (r'feelings- It', 'feelings. It'), (r'\s\.been\b', ' been'),
 (r'\btheir \) - J relative\b|\btheir J relative\b', 'their relative'),
 (r'\bJ being\b', 'being'), (r'the\* yet', 'the yet'),
 (r'\bbom\b', 'born'), (r'ple;\^ant', 'pleasant'),
 (r'association\* Verbal', 'association. Verbal'),
 (r'\bdegree f to\b', 'degree to'), (r'\bminds„', 'minds,'),
 (r'\bobtained The\b', 'obtained. The'), (r'\brepeat The\b', 'repeat. The'),
 (r'\breal object I feel\b', 'real object. I feel'),
 (r'\boriginal Definition\b', 'original. Definition'),
 (r'\breal scene 1\b', 'real scene?'), (r'\bclass-list$', 'class-list.'),
 (r'\bmemory,- may\b', 'memory, may'), (r'\bthem i though\b', 'them; though'),
 (r'\band J conduct\b', 'and conduct'), (r'\{tableau\)', '(tableau)'),
 (r'" tableau "', '"tableau"'), (r'" abasement "', '"abasement"'),
 (r'" a basement,"', '"a basement,"'), (r'" David "', '"David"'),
 (r'" abbey,"', '"abbey,"'), (r'" aborigines,"', '"aborigines,"'),
 (r'" abyss,"', '"abyss,"'), (r'" abasement,"', '"abasement,"'),
 (r'" abhorrence,"', '"abhorrence,"'), (r'" ablution,"', '"ablution,"'),
 (r'" afternoon,"', '"afternoon,"'), (r'" ability,"', '"ability,"'),
 (r'" abnormal,"', '"abnormal,"'), (r'" histrionic "', '"histrionic"'),
 (r'" carriage,"', '"carriage,"'), (r'" abhorrence "', '"abhorrence"'),
 (r'" eugenic "', '"eugenic"'), (r'\(l\)', '(1)'), (r'\balL\b', 'all.'),
 (r'\bwhich 1 now\b', 'which I now'), (r'\bdegree,\]', 'degree,'),
 (r'\s1\^(?=\s)', ''), (r"'English race", 'English race'),
 (r'suflEicient', 'sufficient'), (r'\bstep -by -step\b', 'step-by-step'),
 # second round, read against the print
 (r'to \^\. time', 'to time'), (r'\bi/ scrutinised', 'scrutinised'),
 (r'\beaxUer\b', 'earlier'), (r'light coining', 'light coming'),
 (r'\blineSy\b', 'lines,'), (r'\bintb\b', 'into'),
 (r'agreement and to leave', 'agreement, and to leave'),
 (r'\bI tave often\b', 'I have often'), (r'\bimduly\b', 'unduly'),
 (r'\bcaxe much\b', 'care much'), (r'iUustration', 'illustration'),
 (r'exhibited on several occasion\W*$', 'exhibited on several occasions.'),
 (r'\b1869, 1 have\b', '1869, I have'), (r'\bhaVing\b', 'having'),
 (r'\\with', 'with'), (r'set questions, The first', 'set questions. The first'),
 (r'\bentir ely\b', 'entirely'), (r'themselves,\. sent', 'themselves, sent'),
 (r'\bfrom 1 so many\b', 'from so many'), (r'a much, easier', 'a much easier'),
 (r'trust-, worthy', 'trustworthy'), (r'sharp I mental', 'sharp mental'),
 (r'especiaUy', 'especially'), (r'highly -generalised', 'highly-generalised'),
 (r'\bof hom\b', 'of whom'), (r"knew from' other", 'knew from other'),
 (r'breakfast - table', 'breakfast-table'), (r'\bbreakfasttable\b', 'breakfast-table'),
 (r'1\. Illumination, —', '1. Illumination. —'), (r'actual scene t\b', 'actual scene?'),
 (r'Dim, imperfect 94\.', 'Dim, imperfect. 94.'), (r'generalised, image', 'generalised image'),
 (r'under control 95\.', 'under control. 95.'),
 (r'as a mental image" which', 'as a "mental image" which'),
 (r"''see\"", '"see"'), (r"''mind's eye\.\"", '"mind\'s eye."'),
 (r'\bany part 97\.', 'any part. 97.'), (r'spontaneous ft vision', 'spontaneous vision'),
 (r'Highest — Brilliant', 'Highest. — Brilliant'),
 (r'bright First Octile', 'bright. First Octile'),
 (r'(Quartile|Suboctile), —', r'\1. —'), (r'an\.object', 'an object'),
 (r'under control Lowest', 'under control. Lowest'),
 (r'skiff\. wherry', 'skiff, wherry'), (r'" boat "', '"boat"'),
 (r'associations V will', 'associations will'), (r'Modem Tactics', 'Modern Tactics'),
 (r"that \^' there are", 'that "there are'), (r'the\.carpenter', 'the carpenter'),
 (r'physicists who I contrive', 'physicists who contrive'),
 (r'\bimexpected\b', 'unexpected'), (r'operationa After', 'operations. After'),
 (r'made namely', 'made, namely'), (r'\bfoimd\b', 'found'),
 (r'that is at about the rate', 'that is, at about the rate'),
 (r"care\. ' On throwing", 'care. On throwing'), (r'\btwowheeled\b', 'two-wheeled'),
 (r'\bbellwires\b', 'bell-wires'), (r'\bthemu It\b', 'them. It'),
 (r'I entirely dissent$', 'I entirely dissent.'),
 (r"'\^ Forgetfulness", 'Forgetfulness'), (r'\baboik\b', 'about'),
 (r"and' they were", 'and they were'), (r'and it 7 may', 'and it may'),
 (r'refer to\. common', 'refer to common'), (r'by the scrawl I was', 'by the scrawl. I was'),
 (r'\b1\^ the large\b', 'the large'), (r'and I shows, I think', 'and shows, I think'),
 (r'on the\. memory, are I by', 'on the memory, are by'),
 (r'"abasement " series', '"abasement" series'), (r'\betc, which\b', 'etc., which'),
 (r'has\.been', 'has been'), (r'their - J relative', 'their relative'),
 (r"and ' nimbleness", 'and nimbleness'),
 # caret shrapnel, after every caret-bearing specific fix above
 (r'\^([A-Za-z])', r'\1'), (r'([A-Za-z])\^', r'\1'),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

LABELS = [
 (re.compile(r'^Description o[pf] the Composites\.?$'), 'Description of the Composites'),
]

def units_from(paras):
    us, label = [], None
    for p in paras:
        if p.startswith('\x00NOTE:'):
            if us: us[-1]['note'] = p[6:]
            continue
        lab = next((l for rx, l in LABELS if rx.match(p)), None)
        if lab: label = lab; continue
        u = {'txt': emend(p)}
        if label: u['label'] = label; label = None
        us.append(u)
    return us

def gunit(txt, label, note=None):
    u = {'txt': emend(txt), 'label': label}
    if note: u['note'] = note
    return u

def post_join(us, prev_end, next_start):
    """Join a unit split by a page break the merge rule could not bridge."""
    for i in range(1, len(us)):
        if us[i - 1]['txt'].endswith(prev_end) and us[i]['txt'].startswith(next_start):
            us[i - 1]['txt'] += ' ' + us[i]['txt']
            for f in ('label', 'note'):
                if us[i].get(f) and not us[i - 1].get(f):
                    us[i - 1][f] = us[i][f]
            del us[i]
            return us
    raise AssertionError(f'post_join found nothing: {prev_end!r} / {next_start!r}')

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

# -------------------------------------------------------------- sections
# prog: Introduction complete + the eugenics coinage of p. 24
prog = units_from(harvest(541, 584))
prog[0]['label'] = 'Introduction (pp. 1–2, complete)'
assert 'the cultivation' in lines[1446] and 'eugenic' in lines[1447], 'coinage anchor moved'
assert 'The word eugenics would sufficiently express' in lines[1490], 'footnote anchor moved'
prog.append({
 'txt': ('I do not propose to enter further into the anthropometric '
         'differences of race, for the subject is a very large one, and '
         'this book does not profess to go into detail. Its intention is '
         'to touch on various topics more or less connected with that of '
         'the cultivation of race, or, as we might call it, with "eugenic" '
         'questions, and to present the results of several of my own '
         'separate investigations.'),
 'label': 'From "Bodily Qualities", p. 24 — the word "eugenics" is coined here',
 'note': ('The footnote to this sentence coins the word, and is carried in '
          'full: "That is, with questions bearing on what is termed in '
          'Greek, eugenes, namely, good in stock, hereditarily endowed '
          'with noble qualities. This, and the allied words, eugeneia, '
          'etc., are equally applicable to men, brutes, and plants. We '
          'greatly want a brief word to express the science of improving '
          'stock, which is by no means confined to questions of judicious '
          'mating, but which, especially in the case of man, takes '
          'cognisance of all influences that tend in however remote a '
          'degree to give to the more suitable races or strains of blood '
          'a better chance of prevailing speedily over the less suitable '
          'than they otherwise would have had. The word eugenics would '
          'sufficiently express the idea; it is at least a neater word '
          'and a more generalised one than viriculture, which I once '
          'ventured to use."'),
})

# composite: the chapter complete, pp. 8-19
composite = units_from(harvest(818, 1241))

# imagery: pp. 83-93, then pp. 108-113; the middle omitted and said so
imagery = units_from(harvest(3646, 3685))
imagery.append(gunit(group(3687, 3701),
    'The questions on illumination, definition and colouring, with the '
    'breakfast-table instruction'))
imagery += units_from(harvest(3703, 3882))
imagery.append(gunit(group(3888, 3890), 'Vividness of Mental Imagery'))
imagery.append(gunit(group(3894, 3928), 'Cases where the faculty is very high (returns 1–12)'))
imagery.append(gunit(group(3932, 3970), 'Cases where the faculty is mediocre (returns 46–54)'))
imagery.append(gunit(group(3978, 4047), 'Cases where the faculty is at the lowest (returns 89–100)'))
imagery += units_from(harvest(4049, 4070))
imagery.append(gunit(group(4076, 4117),
    'The scale of visualising power, Highest to Lowest',
    note=('The chapter continues — colour representation, exaggeration, '
          'blindfold chess-players, the faculty in different sexes, ages '
          'and races, its heredity and educability (pp. 93–108) — and that '
          'stretch is not carried in this selection; it resumes below at '
          'the flexibility of imagery.')))
imagery += units_from(harvest(4709, 4940))

# psychometric: the chapter complete, tables noted
psychometric = units_from(harvest(7819, 9015, skips=[
 (8058, 8164, 'Table I — the recurrent associations counted in quadruplets, '
              'triplets, doublets and singles — is not reproduced.'),
 (8308, 8519, 'Table II — the associations by the period of life of their '
              'first formation — is not reproduced.'),
 (8663, 8858, 'Table III — the quality of the words against that of the '
              'ideas in immediate association — is not reproduced.'),
]))
# paragraph breaks the scan lost or invented
post_split(psychometric, 'On throwing these results into a common')
post_split(psychometric, '3. The last of the three groups')
post_join(psychometric, 'associations of the', '"abbey" series')
post_join(psychometric, 'measurable degree,', 'the large effect')

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
    ('prog', 'The program — Introduction, and the word coined on p. 24', prog),
    ('composite', 'Composite portraiture (pp. 8–19, complete)', composite),
    ('imagery', 'Mental imagery — the questionnaire and its returns (pp. 83–93, 108–113)', imagery),
    ('psychometric', 'Psychometric experiments (pp. 185–203, complete)', psychometric),
]:
    nu = numbered(us, k); k += len(us)
    secs.append({'id': sid, 'titel': titel, 'units': nu})

out = {
 'id': 'galton',
 'autor': 'Francis Galton',
 'titel': 'Inquiries into Human Faculty and its Development (1883) — selections',
 'jahr': 1883,
 'zitierweise': 'IHF [k]',
 'quelle': ("Selections from the first edition (London: Macmillan, 1883), "
            "Internet Archive inquiriesintohu00galtgoog, OCR emended by "
            "hand against the sense and the worst passages verified "
            "against the page images. Carried: the Introduction complete; "
            "the paragraph of p. 24 whose footnote coins the word "
            "'eugenics', with the footnote in full; Composite Portraiture "
            "complete (pp. 8–19); Mental Imagery in selections (the "
            "questionnaire and the returns of the hundred, pp. 83–93, and "
            "the closing passage on generic images and the use of the "
            "faculty, pp. 108–113, the omitted middle named in a note); "
            "and Psychometric Experiments complete (pp. 185–203, the "
            "three tables not reproduced, each place marked). The "
            "numbered survey returns and the octile scale are carried "
            "grouped, one unit per printed group. Paragraph numbering k "
            "runs across the four selections, so a citation 'IHF [k]' is "
            "unique. Public domain."),
 'hinweis': ("Statistical portraits of the mind: association timed with a "
             "chronograph, imagery surveyed by questionnaire, faces "
             "averaged photographically — and, in the composites of "
             "criminals, an early negative result: the individual "
             "villainies cancel and no criminal type survives the "
             "averaging. The word 'eugenics' is coined in this book, and "
             "its program is carried here in Galton's own words, stated, "
             "not passed over."),
 'sections': secs,
}

path = os.path.join(REPO, 'data', 'galton.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s['units']) for s in secs], '=', k - 1, 'units')
for s in secs:
    print(f"[{s['id']}]")
    print('  >', s['units'][0]['txt'][:95])
    print('  <', s['units'][-1]['txt'][:95])
