# -*- coding: utf-8 -*-
# Build data/james.json — William James, an anthology in two sources:
#   automata — "Are We Automata?", Mind IV (January 1879), pp. 1-22,
#              complete: the reply to Huxley's automaton address.
#              Source: the journal's public-domain printing, Internet
#              Archive sim_mind_1879-01_4_13.
#   habit    — The Principles of Psychology (New York: Holt, 1890),
#              ch. IV, Habit: the opening (plasticity, pp. 104-106) and
#              the ethical implications through the 'fly-wheel of
#              society' (pp. 120-121);
#   stream   — ch. IX, The Stream of Thought: the section 'Within each
#              personal consciousness, thought is sensibly continuous'
#              through the naming of the stream (pp. 237-239).
#              Source for both: Internet Archive principlesofpsyc01jameuoft
#              (Toronto copy of the 1891 printing, unaltered from 1890).
# Ch. V of the Principles, 'The Automaton-Theory', reworks the Mind
# paper, which therefore stands for it here. Page-bottom footnotes are
# carried as notes on the paragraph they interrupt. OCR emended against
# the sense.
# Usage: python tools/build-james.py
import io, json, os, re, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)

def load(name, url):
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return io.open(path, encoding='utf-8', errors='replace').read().splitlines()

MIND = load('james_mind.txt', 'https://archive.org/download/sim_mind_1879-01_4_13/'
            'sim_mind_1879-01_4_13_djvu.txt')
PP = load('james_pp.txt', 'https://archive.org/download/principlesofpsyc01jameuoft/'
          'principlesofpsyc01jameuoft_djvu.txt')

L = lambda lines, n: lines[n - 1]          # 1-based, as grep shows them
assert L(MIND, 37).startswith('EVERYONE is now acquainted')
assert 'impotently paralytic spectators' in L(MIND, 1464)
assert L(PP, 5128).startswith('When  we  look  at  living')
assert L(PP, 5925).startswith('Tliis  brings  us')
assert 'never  soften' in L(PP, 6000) and L(PP, 6001).startswith('again')
assert L(PP, 11399).startswith('3)')
assert 'subjective  life' in L(PP, 11511)

# --------------------------------------------------------------- filters
MIND_HEAD = re.compile(r'^(\d{1,2}\s+)?(Are we Automata\s?\?|On Discord\.)(\s+\d{1,2})?\s*$')
# running heads, also OCR-mangled ones: '106 P8TCH0L007.', 'EABIT. 121'
PP_HEAD = re.compile(r'^(\d{2,3}\s+)?[A-Z][A-Z0-9 .,]{4,40}\.?(\s+\d{2,3})?\s*$')

def is_noise(s):
    if re.match(r'^[\W\d]*$', s): return True
    if not re.search(r'[A-Za-z]{2}', s) and len(s) < 8: return True
    return False

FOOTMARK = re.compile(r"^(\d|\*|t|†)\s{1,3}\S")

def cleanup(p):
    p = re.sub(r'\s+', ' ', p)
    p = re.sub(r'(\w)- (?=[a-z])', r'\1', p)
    p = re.sub(r'\s+([;:,.!?])', r'\1', p)
    return p.strip()

def harvest(lines, a, b, head_rx, drop=()):
    """Paragraphs plus footnotes (a marker line opening a paragraph, run to
    the next running head); `drop` lists line ranges removed outright."""
    paras, notes, buf = [], [], []
    in_foot, foot = False, []
    prev_blank = True
    for ln in range(a, b + 1):
        if any(x <= ln <= y for x, y in drop): continue
        s = lines[ln - 1].strip()
        if head_rx.match(s):
            if in_foot:
                notes.append((len(paras), foot)); foot = []; in_foot = False
            prev_blank = True
            continue
        if not s:
            if in_foot: foot.append('')
            elif buf: paras.append(' '.join(buf)); buf = []
            prev_blank = True
            continue
        if prev_blank and FOOTMARK.match(s) and not in_foot and not re.match(r'^\d\.\s', s):
            if buf: paras.append(' '.join(buf)); buf = []
            in_foot, foot = True, [s]
            prev_blank = False
            continue
        if in_foot: foot.append(s)
        elif not is_noise(s): buf.append(s)
        prev_blank = False
    if buf: paras.append(' '.join(buf))
    if in_foot: notes.append((len(paras), foot))
    paras = [cleanup(p) for p in paras]
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
    out_notes = []
    for pos, foot in notes:
        tgt = index_map[pos - 1] if pos >= 1 else 0
        # split the page's footnotes at blank lines and at new markers
        parts, cur = [], []
        for s in foot:
            if (not s or FOOTMARK.match(s)) and cur:
                parts.append(' '.join(cur)); cur = []
            if s: cur.append(s)
        if cur: parts.append(' '.join(cur))
        out_notes.append((tgt, [cleanup(x) for x in parts if cleanup(x)]))
    return merged, out_notes

# ---------------------------------------------------------------- fixes
FIXES = [
 (r'(\w)- (?=[a-z])', r'\1'),
 (r'‘', "'"), (r'’', "'"), (r'“', '"'), (r'”', '"'),
 (r'(^|[\s(—])" (?=[\w\'])', r'\1"'), (r'(?<=[\w,.!?]) "(?=[\s,.;:)—]|$)', '"'),
 (r"(^|[\s(—])' (?=[\w])", r"\1'"), (r"(?<=[\w,.!?]) '(?=[\s,.;:)—]|$)", "'"),
 # Mind
 (r'Prof\. Huxley\? gave', 'Prof. Huxley gave'), (r'"Body and Mind"\?;', '"Body and Mind";'),
 (r"The Theory of Practice' The theory", 'The Theory of Practice. The theory'),
 (r'machines, Feelingis a', 'machines. Feeling is a'),
 (r'rival csthetic', 'rival aesthetic'), (r'«esthetic', 'aesthetic'), (r'\besthetic\b', 'aesthetic'),
 (r'thought\. to imagine', 'thought to imagine'), (r'overthrow that\. theory', 'overthrow that theory'),
 (r'\bprovlem\b', 'problem'), (r'as the true Zo;', 'as the true Ego;'),
 (r'\bcgnis fatuus\b', 'ignis fatuus'), (r'at all, I have heard', 'at all. I have heard'),
 (r'\| ?$', ''), (r'theory \| leaves', 'theory leaves'),
 # Principles
 (r'\btirst\b', 'first'), (r'\bdifierent\b', 'different'), (r'\bTlie\b', 'The'),
 (r'\bmodifjdng\b', 'modifying'), (r'\bbei\^ig\b', 'being'), (r'\bAVhen\b', 'When'),
 (r'\bluhich\b', 'which'), (r'\bbottoiii\b', 'bottom'), (r'plasticity\* of', 'plasticity of'),
 (r'\bTliis\b', 'This'), (r'\bgrow\^ to', 'grow to'), (r'\bundoubtinglj\b', 'undoubtingly'),
 (r'\bmachmes\b', 'machines'), (r'\b188-4\b', '1884'), (r'\bpersorml\b', 'personal'),
 (r'\bthovjght\b', 'thought'), (r'inter r\.uptions', 'interruptions'),
 (r'\^\?\*\?ne-gaps', 'time-gaps'), (r'\bquxility\b', 'quality'), (r'\bquahty\b', 'quality'),
 (r'\bpsyche logist\b', 'psychologist'), (r'but owe of the two', 'but one of the two'),
 (r'\bconcej\)tion\b', 'conception'), (r'mental st"\.te', 'mental state'),
 (r'\bot his own\b', 'of his own'), (r'let its call it', 'let us call it'),
 (r'\bconscioiisness\b', 'consciousness'), (r'\bhov/\b', 'how'), (r"\bafi'ec-? ?tions\b", 'affections'),
 (r'shows us how- much', 'shows us how much'), (r'\bshop,\'', "shop,'"),
 (r"\* chain '", "'chain'"), (r"\* stream '", "'stream'"), (r"\* shop,'", "'shop,'"),
 (r"'\s+Attention\s+!\s+'", "'Attention!'"), (r'\*\s+continuous\s+\'', "'continuous'"),
 (r'field\.\*', 'field.'), (r'time\."\s?\*', 'time."'), (r'gutter\."\s?t\b', 'gutter."'),
 (r'\bsociety\s{2,}', 'society '),
 # Mind, read against the dump and, where damaged, the page images
 (r'Automatontheory', 'Automaton-theory'), (r'\bnervecentres\b', 'nerve-centres'),
 (r'\bnerveaction\b', 'nerve-action'), (r'\bstandardbearer\b', 'standard-bearer'),
 (r'\bselfpreservation\b', 'self-preservation'), (r'hit-ormiss', 'hit-or-miss'),
 (r'\bhisown\b', 'his own'), (r'\bsocalled\b', 'so-called'), (r'\bnonexistence\b', 'non-existence'),
 (r'of man, In the beheaded', 'of man. In the beheaded'), (r'nature\. e We may', 'nature. We may'),
 (r'\bita matter\b', 'it a matter'), (r'boy or a girl, The ovum', 'boy or a girl. The ovum'),
 (r'certainly,"', 'certainly,'), (r'up or down-on', 'up or down on'),
 (r'\bwseful\b', 'useful'), (r'reactions, Now the', 'reactions. Now the'), (r'\btoa\b', 'to a'),
 (r'^BI a SA And aan ns ea Bee os eee Cra Wea Sareea ', ''),
 (r'be: best', 'be best'), (r'\bzs good\b', 'is good'), (r"of 'perfection", 'of perfection'),
 (r'with a view to choice Both', 'with a view to choice. Both'),
 (r'Unterscheidungsvermégen', 'Unterscheidungsvermögen'), (r'\bsud sponte\b', 'sua sponte'),
 (r'ignore the the rest', 'ignore the rest'), (r'unremitting / industry\. "~~"To begin', 'unremitting industry. To begin'),
 (r'did riot exist', 'did not exist'), (r'blind for rm of a single eye', 'blind for years of a single eye'),
 (r'consists\.solely', 'consists solely'), (r'of all the rest\.\?', 'of all the rest.'),
 (r'\bOut\.of\b', 'Out of'), (r'\barehitecture\b', 'architecture'),
 (r'\bdoorand window', 'door- and window'), (r'\btothe\b', 'to the'),
 (r'transfixed upon it\?', 'transfixed upon it.'), (r'\bAsthetic\b', 'Aesthetic'),
 (r'purpose of wesnthases Ma his work', 'purpose of his work'),
 (r'Selves, What his', 'Selves. What his'), (r'empirical Zo\b', 'empirical Ego'),
 (r'\bZe Sommeil\b', 'Le Sommeil'), (r'empirical Zyo\b', 'empirical Ego'),
 (r'awakened: in the subject', 'awakened in the subject'),
 (r'Unmégliche', 'Unmögliche'), (r'\bwahlet\b', 'wählet'),
 (r'to-suspect', 'to suspect'), (r"sleep 'after", 'sleep after'),
 (r'@\. priori', 'a priori'), (r'@ posteriori', 'a posteriori'), (r'@ priori', 'à priori'),
 (r'@ la Spencer', 'à la Spencer'), (r'agony\.2\.', 'agony.'), (r'Physiological Aisthetics', 'Physiological Aesthetics'),
 (r'\bdrainageprinciples\b', 'drainage principles'), (r'\bplaceimmediately\b', 'place immediately'),
 (r'appetite may\. instigate', 'appetite may instigate'),
 (r'"J¢ 7s essentially', '"It is essentially'), (r"^'In all these cases", 'In all these cases'),
 (r'_Comparison at choice', 'Comparison and choice'), (r'\bThid\.', 'Ibid.'),
 (r"714\. 3'Vol\. I\., pp\. 416 ff\. 1$", "714. — Vol. I., pp. 416 ff."),
 # Principles: quotes this OCR spaces or glues
 (r"'Mental Physiology 'we", "'Mental Physiology' we"), (r"'Attention! 'whereupon", "'Attention!' whereupon"),
 (r'omnibusand carhorses', 'omnibus- and car-horses'), (r"'continuous'as", "'continuous' as"),
 (r"'blind spot 'meet", "'blind spot' meet"), (r"'how \\ona 'in still", "'how long' is still"),
 (r"'chain'or 'train 'do", "'chain' or 'train' do"), (r"'river 'or a 'stream'are", "'river' or a 'stream' are"),
 (r'\baa weU\b', 'as well'),
 (r'\s\.\s?(?=[a-z])', ' '),
]

def emend(txt):
    for pat, rep in FIXES:
        txt = re.sub(pat, rep, txt)
    return re.sub(r'\s+', ' ', txt).strip()

def build(lines, a, b, head_rx, drop=()):
    paras, notes = harvest(lines, a, b, head_rx, drop)
    us = [{'txt': emend(p)} for p in paras]
    for tgt, parts in notes:
        for part in parts:
            body = emend(re.sub(r"^(\d{1,2}|\*|t|†)\s+", '', part))
            if len(body) < 4: continue
            note = 'Page-bottom footnote: "' + body + '"'
            us[tgt]['note'] = (us[tgt]['note'] + ' — ' + note) if us[tgt].get('note') else note
    return us

automata = build(MIND, 37, 1465, MIND_HEAD)
habit = build(PP, 5128, 5234, PP_HEAD) + build(PP, 5925, 6001, PP_HEAD)
stream = build(PP, 11399, 11511, PP_HEAD)

# ------------------------------------------------ footnote untangling
# Two footnote continuations crossed a page break without a marker and
# were read as text; the page images (leaves 8-9, 18) confirm the seams.
def U(us, frag):
    hit = [u for u in us if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r} ({len(hit)})'
    return hit[0]

def lift(host, start, end=None):
    t = host['txt']
    i = t.find(start)
    j = t.find(end, i) if end else len(t)
    assert 0 <= i < j, f'lift anchors wrong: {start!r} / {end!r}'
    piece = t[i:j].strip()
    host['txt'] = (t[:i].rstrip() + ' ' + t[j:].lstrip()).strip()
    return piece

def add_note(u, txt):
    u['note'] = (u['note'] + ' — ' + txt) if u.get('note') else txt

def foot(txt):
    return 'Page-bottom footnote: "' + txt + '"'

# p. 7: the teleology footnote spliced into the Darwin paragraph
h = U(automata, 'with even greater energy the')
piece = lift(h, '1J have treated this matter', 'consciousness of the creature itself')
add_note(h, foot(piece.replace('1J have treated', 'I have treated')
                      .replace('in_respect', 'in respect').replace('aiter Smith', 'after Smith')))

# pp. 9-10: the squint footnote ('If one cared …') continues on p. 10
h = U(automata, 'materially different from posed efficacious)')
cont = lift(h, 'posed efficacious)', None)
cont = (cont.replace('pointing to what en in cases of squint', 'pointing to what happens in cases of squint')
            .replace('rather i, $0 all may raise the? and now, for all have got the seed"—',
                     'rather cheap—"all may raise the flowers now, for all have got the seed"—'))
assert 'rather cheap' in cont and 'what happens' in cont, 'squint repair missed'
nxt = U(automata, 'sensations on the other, as Objects.')
nxt['txt'] = re.sub(r'^.*?(?=sensations on the other, as Objects\.)', '', nxt['txt'])
h['txt'] = h['txt'] + ' ' + nxt['txt']
note_host = U(automata, 'blind for years of a single eye')
note_host['note'] = note_host['note'].replace('selective attention (sup-"', 'selective attention (sup' + cont + '"')
note_host['note'] = re.sub(r'" — Page-bottom footnote: "might easily show', ' might easily show', note_host['note'])
automata.remove(nxt)
# the 'When I say Objects …' note belongs to the sentence its marker closes
src = U(automata, 'Let four men make a tour')
dst = U(automata, 'whose native objectivity shall be held more valid')
dst['note'] = src.pop('note')

# p. 18: the breathing footnote continues on p. 19 inside the text
h = U(automata, 'it is difficult to see what standard')
piece = lift(h, 'rather negative one of ease results.', 'is subserved.')
piece = re.sub(r'\s*iz SSeS SM\s*$', '', piece)
br = [u for u in automata if 'hardly any feeling but the' in u.get('note', '')]
assert len(br) == 1, 'breathing-footnote host missing'
br = br[0]
br['note'] = br['note'].replace('hardly any feeling but the"', 'hardly any feeling but the ' + piece + '"')
h['note'] = ''
h.pop('note')

# a paragraph running over the 'On Discord' page head
a = U(automata, 'lies wholly in the field of molecular physics.')
b = U(automata, 'Thither Science may retreat')
a['txt'] += ' ' + b['txt']; automata.remove(b)
# paragraph break lost behind 'unremitting industry.'
a = U(automata, 'unremitting industry. To begin')
i = a['txt'].find('To begin at the bottom')
automata.insert(automata.index(a) + 1, {'txt': a['txt'][i:]})
a['txt'] = a['txt'][:i].strip()

# scanner debris read as notes
for u in automata:
    if u.get('note'):
        parts = [p for p in u['note'].split(' — Page-bottom footnote: ')]
        keep = [p for p in parts if len(re.sub(r'Page-bottom footnote: |"', '', p)) > 14]
        u['note'] = ' — Page-bottom footnote: '.join(keep) if keep else None
        if not u['note']: u.pop('note')

# Principles, ch. IV: the veteran story ends the Carpenter quotation; the
# Huxley footnote belongs to it, the 'Der menschliche Wille' note to a
# quotation above the carried passage
v = U(habit, 'lost his mutton and potatoes')
i = v['txt'].find('Riderless cavalry-horses')
habit.insert(habit.index(v) + 1, {'txt': v['txt'][i:]})
v['txt'] = re.sub(r'\s*t$', '', v['txt'][:i].strip())
hux = habit[habit.index(v) + 1].pop('note', '')
v['note'] = foot("Huxley's 'Elementary Lessons in Physiology,' lesson xii.") + \
    ' — the veteran story is quoted from Huxley, carried in this corpus.'
# the plasticity footnote belongs to the sentence whose marker it answers
src = [u for u in habit if 'In the sense above explained' in u.get('note', '')]
assert len(src) == 1, 'plasticity footnote host missing'
src = src[0]
parts = src.pop('note').split(' — ')
plast = [p for p in parts if 'In the sense above explained' in p]
rest = [p for p in parts if 'In the sense above explained' not in p]
if rest: src['note'] = ' — '.join(rest)
tgt = U(habit, 'due to the plasticity of the organic materials')
ps = [p for p in tgt.pop('note', '').split(' — ') if p]
chapter_note = [p for p in ps if 'Popular Science Monthly' in p]
tgt['note'] = ' — '.join([p for p in ps if 'Popular Science Monthly' not in p] + [plast[0]])
if chapter_note: add_note(habit[0], chapter_note[0])
# the three reference footnotes answer markers in the opening paragraph;
# James names the source of the theory he answers
automata[0]['note'] = automata[1].pop('note')
add_note(automata[0],"The Belfast address is Huxley's 'On the Hypothesis that Animals "
         "are Automata' (1874) — carried complete in this corpus.")

# labels
def lab(us, frag, text):
    hit = [u for u in us if frag in u['txt']]
    assert hit, f'label anchor missing: {frag!r}'
    hit[0]['label'] = text

lab(automata, 'EVERYONE is now acquainted', 'The Conscious-Automaton-theory stated')
lab(automata, 'Of what use to a nervous system', 'The problem: the use of consciousness')
lab(automata, 'the essence of the Common-Sense-theory', 'The verdict')
lab(habit, 'When we look at living creatures', 'Habit and plasticity (pp. 104–106)')
lab(habit, 'brings us by a very natural transition', 'The ethical implications (pp. 120–121)')
lab(habit, 'enormous fly-wheel of society', 'The fly-wheel of society')
lab(stream, 'Within each personal consciousness', 'Thought is sensibly continuous (pp. 237–239)')
lab(stream, 'does not appear to itself chopped', 'The stream named')

# heading line of the stream section is carried as its label, not as text
stream = [u for u in stream if not re.match(r'^3\)\s*Within each personal consciousness', u['txt'])]
stream[0]['label'] = 'Thought is sensibly continuous (pp. 237–239)'

habit[-1]['note'] = ((habit[-1]['note'] + ' — ') if habit[-1].get('note') else '') + (
    'The chapter continues with the formation of personal habits and '
    "James's maxims for acquiring good ones (pp. 121–127), not carried here.")

def numbered(us, k0):
    return [dict({'n': i + 1, 'k': k0 + i}, **u) for i, u in enumerate(us)]

s1 = numbered(automata, 1)
s2 = numbered(habit, 1 + len(automata))
s3 = numbered(stream, 1 + len(automata) + len(habit))

out = {
 'id': 'james',
 'autor': 'William James',
 'titel': 'Anthology: Are We Automata? (1879) · from The Principles of Psychology (1890)',
 'jahr': 1879,
 'zitierweise': 'AWA [k] · PP [k]',
 'quelle': ("An anthology from two public-domain printings. 'Are We "
            "Automata?' complete, from Mind IV, no. 13 (January 1879), pp. "
            "1–22, Internet Archive sim_mind_1879-01_4_13; and from The "
            "Principles of Psychology (New York: Holt, 1890; Toronto copy "
            "of the unaltered 1891 printing, Internet Archive "
            "principlesofpsyc01jameuoft) two passages of ch. IV, Habit "
            "(pp. 104–106 and 120–121), and the section of ch. IX in which "
            "thought is shown 'sensibly continuous' and the stream is named "
            "(pp. 237–239). Ch. V of the Principles, 'The Automaton-Theory', "
            "reworks the Mind paper, which stands for it here. Page-bottom "
            "footnotes carried as notes. OCR emended against the sense. "
            "Cited as 'AWA [k]' for the Mind paper and 'PP [k]' for the "
            "Principles; k runs across the module, so every citation is "
            "unique."),
 'hinweis': ("The great reply. Huxley had made consciousness 'a simple "
             "passenger in the voyage of life'; James turns Darwin against "
             "him — consciousness has evolved, and organs that evolve have "
             "a use — and finds that use in selection: a brain of unstable "
             "equilibrium needs a fighter for ends to load its dice. The "
             "Principles add habit as plasticity (the nervous system's "
             "paths worn like a channel) and the stream: thought 'is "
             "nothing jointed; it flows'. Against the mechanist line of "
             "this corpus, James is the strongest nineteenth-century case "
             "that minds are not mere mechanism — built, characteristically, "
             "from the physiology of habit itself."),
 'sections': [
   {'id': 'automata', 'titel': 'Are We Automata? (Mind, 1879) — complete', 'units': s1},
   {'id': 'habit', 'titel': 'The Principles of Psychology, ch. IV — Habit (selections)', 'units': s2},
   {'id': 'stream', 'titel': 'The Principles of Psychology, ch. IX — The Stream of Thought (selection)', 'units': s3},
 ],
}

path = os.path.join(REPO, 'data', 'james.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s1), len(s2), len(s3)], 'units')
for s in (s1, s2, s3):
    print('  >', s[0]['txt'][:95])
    print('  <', s[-1]['txt'][:95])
