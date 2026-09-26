# Build data/network.json: paragraph-level co-occurrence of the top content
# terms across all shipped English texts, for the Atlas view.
import io, json, re, math
from collections import Counter, defaultdict

REPO = 'C:/Users/leofa/OneDrive/Desktop/Psych Predecessors/repo'
works = json.load(io.open(f'{REPO}/data/works.json', encoding='utf-8'))
shipped = [w for w in works if w['status'] == 'shipped']

STOP = set('''a an the and or but nor for yet so of in on at by to from with without into unto upon
over under above below between among through during before after again further then once here there
when where why how all any both each few more most other some such no not only own same than too
very can will just should now is are was were be been being have has had having do does did doing
would could may might must shall this that these those i you he she it we they them his her its our
their your my me him us who whom which what whose as if because while until although though since
whether either neither also thus hence therefore moreover however indeed rather quite perhaps even
ever never always often sometimes one two three four five first second third much many little less
least own self same so-called et cetera viz ie eg ib id etc part parts chapter chapters
hath doth haue bee vpon vnto onely selfe thereof wherein whereby whereof therein thereto herein
shal wil doe mee wee bene beene yea nay ye thy thou thee sayd haply
say says said saying tell told call called calls calling make makes made making let lets go goes
went gone come comes came take takes taken took give gives given gave get gets got put puts see
sees seen saw seem seems seemed appear appears appeared find finds found know knows known knew
think thinks thought am against about almost along already although always
another any anything anywhere back cannot certain certainly consequently down during else
elsewhere enough every everything everywhere far forth great greater greatest good better best
last latter former like likewise long longer means merely might more most namely near nearly
neither never nevertheless new next none nothing now nowhere off often once only order other
others otherwise ought out over own per rather round several shall should side since small so some
something sometime sometimes somewhat somewhere still such than that the their them themselves
then thence there thereafter thereby therefore therein these they this those through throughout
thru thus to together too toward towards under until up upon us used using various very via was
way we well were what whatever when whence whenever where whereas whereupon wherever
whither whoever whole whose why within would yet whereas due real thing things fact case cases
respect regard point view manner kind sort way ways word instance example true truth false
place places time times form forms subject object present different general particular
proper certain follow follows following followed itself himself herself themselves oneself myself yourself moreover besides namely accordingly whatever whoever wherein whereby anything nothing'''.split())

def toks(txt):
    ws = re.findall(r"[a-zA-Z][a-zA-Z'-]{3,}", txt.lower())
    out = []
    for w in ws:
        w = w.strip("'-")
        if len(w) < 4 or w in STOP: continue
        out.append(w)
    return out

# collect per-unit token sets
units = []          # (workId, linie, secId, n, tokset)
freq = Counter()
wfreq = defaultdict(Counter)   # term -> work -> count
for w in shipped:
    t = json.load(io.open(f"{REPO}/data/{w['datei']}.json", encoding='utf-8'))
    for s in t['sections']:
        for u in s['units']:
            ts = set(toks(u['txt']))
            units.append((w['id'], w['linie'], s['id'], u['n'], ts))
            for x in ts:
                freq[x] += 1
                wfreq[x][w['id']] += 1

# merge naive plurals into singular
vocab = set(freq)
merged = {}
for x in list(freq):
    if x.endswith('s') and not x.endswith('ss') and x[:-1] in vocab:
        merged[x] = x[:-1]
def canon(x): return merged.get(x, x)
freq2 = Counter(); wfreq2 = defaultdict(Counter)
for x, c in freq.items():
    freq2[canon(x)] += c
for x, wc in wfreq.items():
    for wid, c in wc.items(): wfreq2[canon(x)][wid] += c

# top terms: require presence, favour cross-work spread a little
def score(x):
    return freq2[x] * (1 + 0.35 * (len(wfreq2[x]) - 1))
top = sorted(freq2, key=score, reverse=True)[:72]
tset = set(top)

# co-occurrence over canonical tokens
co = Counter()
cites = defaultdict(list)     # term -> [work, sec, n]
for wid, linie, sid, n, ts in units:
    cts = sorted(set(canon(x) for x in ts) & tset)
    for x in cts:
        # keep at most two citations per work, so the panel spans the corpus
        if sum(1 for c in cites[x] if c[0] == wid) < 2:
            cites[x].append([wid, sid, n])
    for i in range(len(cts)):
        for j in range(i + 1, len(cts)):
            co[(cts[i], cts[j])] += 1

N = len(units)
LINIE_OF = {w['id']: w['linie'] for w in shipped}
nodes = []
for x in top:
    wc = wfreq2[x]
    # dominant line by counts
    lc = Counter()
    for wid, c in wc.items(): lc[LINIE_OF[wid]] += c
    dom = lc.most_common(1)[0][0]
    spread = len(wc)
    nodes.append({'id': x, 'f': freq2[x], 'linie': dom, 'works': dict(wc),
                  'spread': spread, 'cites': cites[x]})

edges = []
for (a, b), c in co.items():
    if c < 2: continue
    # PMI-ish weight to rank
    pmi = math.log((c * N) / (freq2[a] * freq2[b]))
    edges.append({'s': a, 't': b, 'c': c, 'w': round(c * max(pmi, 0.05), 2)})
edges.sort(key=lambda e: -e['w'])
edges = edges[:420]

# bridge terms: appear in >= 4 works, ranked by spread then freq
bridges = [n['id'] for n in sorted(nodes, key=lambda n: (-n['spread'], -n['f'])) if n['spread'] >= 4][:12]

out = {'n_units': N, 'nodes': nodes, 'edges': edges, 'bridges': bridges}
json.dump(out, io.open(f'{REPO}/data/network.json', 'w', encoding='utf-8'), ensure_ascii=False)
import os
print('units', N, '| nodes', len(nodes), '| edges', len(edges))
print('top12:', [n['id'] for n in nodes[:12]])
print('bridges:', bridges)
