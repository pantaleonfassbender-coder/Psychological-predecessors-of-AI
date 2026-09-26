# -*- coding: utf-8 -*-
# Build data/fechner.json — Fechner, Elemente der Psychophysik (Leipzig:
# Breitkopf und Härtel, 1860), selections, German with an unofficial
# working translation made for this site (CC0). The English translation
# of 1966 is in copyright and was not consulted — the module is a
# clean-room translation directly from the 1860 printing.
#
# Sources (downloaded on demand into tools/.cache/): vol. I, Internet
# Archive elementederpsych001fech; vol. II, Internet Archive 10255089.
# The 1860 printing is set in Antiqua, and its OCR is good; it is
# emended against the sense, the displayed formulas restored by hand
# (the OCR renders γ, β and the fraction bars as y, ß/8/$ and £).
#
# Three sections:
#   vorw    — the Vorwort complete (vol. I): the programme, Weber named
#             as the father of psychophysics;
#   begriff — vol. I, ch. II complete: Begriff und Aufgabe der
#             Psychophysik — the exact science of the functional
#             relations between body and soul defined;
#   formel  — vol. II, from ch. XVI: the Fundamentalformel and the
#             Massformel through γ = k log (β/b) and its immediate
#             interpretation; the chapter's further consequences and
#             ch. XVII's mathematical derivation are named, not carried.
# Usage: python tools/build-fechner.py [--dump]
import io, json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)

def src(name, url):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        urllib.request.urlretrieve(url, p)
    return io.open(p, encoding='utf-8', errors='replace').read().splitlines()

L1 = src('fechner1.txt', 'https://archive.org/download/elementederpsych001fech/elementederpsych001fech_djvu.txt')
L2 = src('fechner2.txt', 'https://archive.org/download/10255089/10255089_djvu.txt')

HEAD = re.compile(r'^\s*(\d{1,3}\s+)?(VORWORT\.?|Vorwort\.?|INHALT\.?|'
                  r'(IL?|II)\.\s+Begriff\s+und\s+Aufgabe.*|Begriff\s+und\s+Aufgabe.*|'
                  r'XVI\.\s+Die\s+Fundamentalformel.*|Die\s+Fundamentalformel\s+und\s+Massformel\.?|'
                  r'Fechner,\s+Elemente.*|Digitized by.*)\s*(\d{1,3})?\s*$')
NOISE = re.compile(r'^\s*(\d{1,3}|[ivxlIVXL*]+|[A-Za-z]|\*\d)\s*$')

def harvest(lines, a, b):
    paras, buf = [], []
    for raw in lines[a - 1:b]:
        s = re.sub(r'\s+', ' ', raw).strip()
        if HEAD.match(s) or NOISE.match(s): continue
        core = re.sub(r'\s', '', s)
        if core and sum(c.isalpha() for c in core) / len(core) < .5 and len(core) > 3 \
           and not re.search(r'[=()]', s):
            continue                       # page-furniture shards
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(s)
    if buf: paras.append(' '.join(buf))
    out = []
    for p in paras:
        p = re.sub(r'(\w)- (?=[a-zäöüß])', r'\1', p)
        p = re.sub(r'\s+', ' ', p).strip()
        if len(p) > 2: out.append(p)
    merged = []
    for p in out:
        if merged and (re.match(r'^[a-zäöüß\)\],;:]', p) or
                       re.search(r'[a-zäöüß,;]$', merged[-1])):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

FIXES = [
    ('�', '—'),
    # --- Vorwort / ch. II: plain OCR damage, emended against the sense
    (r'\bRegründung\b', 'Begründung'), (r'\blrrthümer\b', 'Irrthümer'),
    (r'\ber fahrungs massige\b', 'erfahrungsmässige'),
    (r'\bwTollte\b', 'wollte'), (r'\bFöderung\b', 'Förderung'),
    (r'in dieser Schritt\b', 'in dieser Schrift'), (r'\bGonflict\b', 'Conflict'),
    (r'\bpsychophysiche\b', 'psychophysische'),
    (r'\bGonstanz\b', 'Constanz'), (r'\bBelation\b', 'Relation'),
    (r'\bVoraussetztung\b', 'Voraussetzung'), (r'\bwerdon\b', 'werden'),
    (r'\bder Beiz\b', 'der Reiz'), (r'auf der Psychologie zu hissen', 'auf der Psychologie zu fussen'),
    (r'\bBekannntschaft\b', 'Bekanntschaft'), (r'An griff spuncte', 'Angriffspuncte'),
    (r'\bErscheinunasverhältnisse\b', 'Erscheinungsverhältnisse'),
    (r'that- sächlichen', 'thatsächlichen'),
    (r'\bZwischen Wirkung\b', 'Zwischenwirkung'),
    # --- ch. XVI: the formulas and their surroundings, restored by hand
    (r'heisse #, der kleine Zuwuchs heisse d®', 'heisse β, der kleine Zuwuchs heisse dβ'),
    (r'dass dß ein kleiner Zuwuchs zu # sei', 'dass dβ ein kleiner Zuwuchs zu β sei'),
    (r'So ist der relative Reizzuwuchs 4$', 'So ist der relative Reizzuwuchs dβ/β.'),
    (r'So ist der relative Reizzuwuchs 4\b', 'So ist der relative Reizzuwuchs dβ/β.'),
    (r'von dem Reize # abhängt, heisse y', 'von dem Reize β abhängt, heisse γ'),
    (r'um dß entsteht, heisse dy', 'um dβ entsteht, heisse dγ'),
    (r'\bdß und dy sind\b', 'dβ und dγ sind'),
    (r'bleibt dy constant, wenn 2 constant bleibt', 'bleibt dγ constant, wenn dβ/β constant bleibt'),
    (r'welche absolute Werthe auch d# und 8 annehmen', 'welche absolute Werthe auch dβ und β annehmen'),
    (r'die Aenderungen dy und dß einander', 'die Aenderungen dγ und dβ einander'),
    (r'durch folgende Gleichung ausdrücken 4=- m wo Keine \(von den für y und # zu wählenden Einheiten abhängige\) Constante ist',
     'durch folgende Gleichung ausdrücken dγ = K (dβ/β)   (1) wo K eine (von den für γ und β zu wählenden Einheiten abhängige) Constante ist'),
    (r'man multiplieire d\? und 8 beide', 'man multiplicire dβ und β beide'),
    (r'auch der Empfindungsunterschied dy constant', 'auch der Empfindungsunterschied dγ constant'),
    (r'den Werth der Aenderung dß allein, ohne den Ausgangswerth 8 zu ändern, so nimmt auch die Aenderung dy',
     'den Werth der Aenderung dβ allein, ohne den Ausgangswerth β zu ändern, so nimmt auch die Aenderung dγ'),
    (r'Die Gleichung dy = I genügt', 'Die Gleichung dγ = K (dβ/β) genügt'),
    (r'\bden Zuwüchsen dy und d# in der Fundamentalformel', 'den Zuwüchsen dγ und dβ in der Fundamentalformel'),
    (r'der Zahl 10 um 4 eine', 'der Zahl 10 um 1 eine'),
    (r'als der Zahl 400 um 40 und', 'als der Zahl 100 um 10 und'),
    (r'dem Werthe 4, sofern der Logarithmus von 1', 'dem Werthe 1, sofern der Logarithmus von 1'),
    (r'die einfachste Beziehung zwischen haklen, die wir aufstellen können, yalgß\. & a',
     'die einfachste Beziehung zwischen beiden, die wir aufstellen können, γ = log β.'),
    (r'\bindireete\b', 'indirecte'),
    (r"W eb er'sche", "Weber'sche"),
    (r'den Ausdruck des ie in dieser Form', "den Ausdruck des Weber'schen Gesetzes in dieser Form"),
    (r'auf seinen Schwellenwerth \(5\)', 'auf seinen Schwellenwerth (b)'),
    (r'dieEmpfindung', 'die Empfindung'),
    (r'sieistproportionaldem', 'sie ist proportional dem'),
    (r'Die Grösse der Empfindung \(y\)', 'Die Grösse der Empfindung (γ)'),
    (r'Grösse des Reizes \(ß\)', 'Grösse des Reizes (β)'),
    (r'Dieser verhältnissmässige Reizwerth £ soll', 'Dieser verhältnissmässige Reizwerth β/b soll'),
    (r'\bänlangt\b', 'anlangt'),
    (r'wenn P=0, sondern wenn f gleich dem endlichen Werthe d ist',
     'wenn β = 0, sondern wenn β gleich dem endlichen Werthe b ist'),
    (r'dass, wenn f£ gleich 5 wird, log £ = log wird, und logi = o ist',
     'dass, wenn β gleich b wird, log β = log b wird, und log 1 = 0 ist'),
    (r'Zuwachs einer grossen Zahl 8 durch', 'Zuwachs einer grossen Zahl durch'),
    (r'einer kleinen Zahl 8 um denselben', 'einer kleinen Zahl um denselben'),
    (r'Wenn die Zahl 40 um 40 wächst, also auf 20 steigt, so wächst der zu”10 gehörige Logarithmus 4 auf 4,3040',
     'Wenn die Zahl 10 um 10 wächst, also auf 20 steigt, so wächst der zu 10 gehörige Logarithmus 1 auf 1,3010'),
    (r'Wenn aber die Zahl 1000 um 40 wächst, so wächst der zu 1000 gehörige Logarithmus 3 nur auf 3,0043',
     'Wenn aber die Zahl 1000 um 10 wächst, so wächst der zu 1000 gehörige Logarithmus 3 nur auf 3,0043'),
    (r'um etwa #, letzterenfalls nur etwa um „4, seiner Grösse vermehrt\. 2',
     'um etwa 3/10, letzterenfalls nur etwa um 1/700 seiner Grösse vermehrt.'),
    (r'dass, wenn ß kleiner als b und mithin log £ kleiner als log wird',
     'dass, wenn β kleiner als b und mithin log β kleiner als log b wird'),
    (r'dass £ zu einem äch- ?ten Bruche wird, wenn # ?<b', 'dass β/b zu einem ächten Bruche wird, wenn β < b'),
    (r'\baffieiren\b', 'afficiren'), (r'\baflieiren\b', 'afficiren'),
    (r'Erfahrung::', 'Erfahrung:'),
    (r'\b4\) In den Gleichheitsfällen', '1) In den Gleichheitsfällen'),
    (r'\bInden Gränzfällen\b', 'In den Gränzfällen'),
    (r'\bInden Gegensatzfällen\b', 'In den Gegensatzfällen'),
    (r'\bHauptuuterlage\b', 'Hauptunterlage'),
    (r'nach einem u a richtigen Gange', 'nach einem richtigen Gange'),
    (r'MitderMassformelhat mannun einallgemeines', 'Mit der Massformel hat man nun ein allgemeines'),
    (r'Empfindunggewonnen', 'Empfindung gewonnen'),
    (r'Wievielmal\.des', 'Wievielmal des'),
    (r'Empfindungen » und deren', 'Empfindungen und deren'),
    (r'Hülfsprin[se]ip', 'Hülfsprincip'), (r"'Zahlenzuwüchse", 'Zahlenzuwüchse'),
    (r'„sagen', 'sagen'), (r'zurück - kommt', 'zurückkommt'),
    (r'‘welcher', 'welcher'), (r'rela- ?tıven', 'relativen'),
    (r'-zugehören', 'zugehören'), (r'als y den Werth Null', 'als γ den Werth Null'),
    (r'im zugehörigen Logarithmus y mit', 'im zugehörigen Logarithmus mit'),
    (r'Diffe- ?renzialzeichen', 'Differenzialzeichen'),
    (r'Logarith- ?mus', 'Logarithmus'), (r'Em- ?pfindungen', 'Empfindungen'),
    (r'Weber’- schen', 'Weber’schen'),
    (r'y\s*=\s*k\s*\(\s*log\s*ß\s*—\s*log\s*b\s*\)\s*\(2\)\.?', 'γ = k (log β − log b)   (2)'),
    (r'y\s*=\s*klog\s*£\s*\(3\)\.?', 'γ = k log (β/b)   (3)'),
    (r'\bReizes 8\b', 'Reizes β'),
    (r'\bEmpfindung y\b', 'Empfindung γ'),
    (r'\bvon y\b', 'von γ'),
    (r'\bEmpfindungsgrösse y\b', 'Empfindungsgrösse γ'),
    (r'\bReizwerthes f\b', 'Reizwerthes β'),
    (r'\bdy und d#\b', 'dγ und dβ'),
]

def emend(paras):
    out = []
    for p in paras:
        for pat, rep in FIXES:
            p = re.sub(pat, rep, p)
        out.append(re.sub(r'\s+', ' ', p).strip())
    return out

vorw = emend(harvest(L1, 104, 389))
begriff = emend(harvest(L1, 828, 1059))
formel = emend(harvest(L2, 938, 1391))

# ch. XVI hand repairs beyond pattern fixes -----------------------------
def find(ps, frag):
    for i, p in enumerate(ps):
        if frag in p: return i
    raise AssertionError('not found: ' + frag)

# the shredded remains of the displayed formula (1) after the summation
# paragraph, and the Vivès-style garbage row after formula (2)
i = find(formel, 'solidarisch zugleich die Richtigkeit der letzten gegeben ist.')
formel[i] = re.sub(r'gegeben ist\..*$', 'gegeben ist.', formel[i])
i = find(formel, 'welche den Namen Massformel führen')
formel[i] = re.sub(r'\s*u a U I un no A 4 une Me a.*$', '', formel[i])
# the small-type remark on k and K is the print's petit text: not carried
formel[i] = re.sub(r'\s*Nach der im folgenden Kapitel gegebenen Ableitungsweise.*$', '', formel[i])
# the derivation of the Unterschiedsformel, shredded around its displays,
# restored by hand after the sense of the passage
i = find(formel, 'deren Unterschied es zu betrachten gilt')
formel[i] = ("Seien zwei Empfindungen, deren Unterschied es zu betrachten gilt, γ und γ′, "
             "und die ihnen zugehörigen Reize β und β′. Dann haben wir nach der Massformel "
             "γ = k (log β − log b) und γ′ = k (log β′ − log b), und mithin für den "
             "Empfindungsunterschied γ − γ′ = k (log β − log β′); oder, da "
             "log β − log β′ = log (β/β′): γ − γ′ = k log (β/β′). Aus dieser Formel folgt, "
             "dass der Empfindungsunterschied γ − γ′ eine Function des Reizverhältnisses "
             "β/β′ ist, und gleich gross bleibt, welche Werthe auch β, β′ annehmen mögen, "
             "wenn nur ihr Verhältniss ungeändert bleibt, was die Aussage des Weber'schen "
             "Gesetzes ist.")
# a page turn splits the Unterschiedsschwelle paragraph
i = find(formel, 'erst bei einem endlichen')
formel[i] = re.sub(r'\s*\|\s*$', ' ', formel[i]).rstrip() + ' ' + formel[i + 1]
del formel[i + 1]
# the table of numbers and logarithms: its header remains, the table not
i = find(formel, 'Zahl. Logarithmus.')
formel[i] = formel[i].replace('Zahl. Logarithmus. ', '')
# the module ends at the emphatic close of the measure claim
i = find(formel, 'womit das Mass der Empfindung gegeben ist')
formel = formel[:i + 1]

if '--dump' in sys.argv:
    for name, ps in (('vorw', vorw), ('begriff', begriff), ('formel', formel)):
        print(f'===== {name} ({len(ps)})')
        for i, p in enumerate(ps):
            print(f'[{i}] {p}')
    sys.exit(0)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fechner_en import EN_VORW, EN_BEGRIFF, EN_FORMEL, NOTES
for name, ps, en in (('vorw', vorw, EN_VORW), ('begriff', begriff, EN_BEGRIFF),
                     ('formel', formel, EN_FORMEL)):
    assert len(ps) == len(en), (name, len(ps), len(en))

k0, sections = 1, []
for sid, titel, ps, en in (
    ('vorw', 'Vorwort (1859) — complete', vorw, EN_VORW),
    ('begriff', 'Vol. I, ch. II — Begriff und Aufgabe der Psychophysik (complete)', begriff, EN_BEGRIFF),
    ('formel', 'Vol. II, from ch. XVI — Fundamentalformel and Massformel', formel, EN_FORMEL)):
    units = []
    for i, (de, e) in enumerate(zip(ps, en)):
        u = {'n': i + 1, 'k': k0 + i, 'txt': e, 'orig': de}
        note = NOTES.get((sid, i))
        if note: u['note'] = note
        units.append(u)
    k0 += len(ps)
    sections.append({'id': sid, 'titel': titel, 'units': units})

out = {
 'id': 'fechner',
 'autor': 'Gustav Theodor Fechner',
 'titel': 'Elemente der Psychophysik (1860) — selections',
 'jahr': 1860,
 'zitierweise': 'EP [k]',
 'quelle': ("Selections from Elemente der Psychophysik (Leipzig: Breitkopf und "
            "Härtel, 1860): the Vorwort and vol. I ch. II complete, and the "
            "Fundamentalformel–Massformel passage of vol. II ch. XVI through "
            "γ = k log (β/b) and its immediate interpretation — the chapter's "
            "further consequences and ch. XVII's mathematical derivation are "
            "named, not carried. Internet Archive scans elementederpsych001fech "
            "and 10255089; the 1860 Antiqua's OCR emended against the sense, "
            "the displayed formulas restored by hand. The English is an "
            "unofficial machine-generated working translation made for this "
            "site directly from the German (CC0) and carries no authority — "
            "cite the German. The translation of 1966 is in copyright and was "
            "not consulted. Paragraph numbering k runs across the module. "
            "Public domain."),
 'hinweis': ("The founding act of the measured mind: psychophysics defined as "
             "an exact doctrine of the functional relations between body and "
             "soul, Weber named its father, and sensation brought under the "
             "logarithmic measure formula — the first claim that inner life "
             "obeys an equation."),
 'sections': sections,
}

path = os.path.join(REPO, 'data', 'fechner.json')
json.dump(out, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(vorw), len(begriff), len(formel)], 'units')
