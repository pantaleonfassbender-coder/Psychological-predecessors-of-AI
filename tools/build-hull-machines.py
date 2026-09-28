# -*- coding: utf-8 -*-
# Build data/hull_machines.json — the conditioning machines, the corpus's
# last station. Two papers, both complete:
#   science — Clark L. Hull and H. D. Baernstein, "A Mechanical Parallel to
#             the Conditioned Reflex", Science 70, no. 1801 (5 July 1929),
#             pp. 14-15 (Discussion). Internet Archive
#             sim_science_1929-07-05_70_1801.
#   wissen  — Clark L. Hull, "Knowledge and Purpose as Habit Mechanisms",
#             Psychological Review 37, no. 6 (November 1930), pp. 511-525.
#             Internet Archive sim_psychological-review_1930-11_37_6
#             (leaf = page - 455).
# Both in the United States public domain (1929 and 1930 publications).
# The 1930 paper's nine diagrams are not reproduced; each place is marked.
# Its subscripts (S1, R5, s4, Sp …), which the OCR does not survive, and
# its footnotes were read from the page images and are set by hand.
# Usage: python tools/build-hull-machines.py [--dump]
import io, json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '.cache')
os.makedirs(CACHE, exist_ok=True)
def src(item):
    p = os.path.join(CACHE, item + '.txt')
    if not os.path.exists(p):
        urllib.request.urlretrieve(f'https://archive.org/download/{item}/{item}_djvu.txt', p)
    return io.open(p, encoding='utf-8', errors='replace').read().splitlines()
SCI = src('sim_science_1929-07-05_70_1801')
PR = src('sim_psychological-review_1930-11_37_6')

def rng(lines, a, b, skip):
    assert all(0 < x <= len(lines) for x in (a, b))
    out = []
    for ln in range(a, b + 1):
        if any(x <= ln <= y for x, y in skip):
            continue
        out.append(lines[ln - 1])
    return out

def is_head(s):
    letters = re.sub(r'[^A-Za-z]', '', s)
    return len(letters) >= 5 and len(s) < 60 and sum(c.isupper() for c in letters) / len(letters) > .8

def is_noise(s):
    return not re.search(r'[a-z]{4}', s) and 'Fig.' not in s

def harvest(ls):
    paras, buf = [], []
    for s in (x.strip() for x in ls):
        if not s:
            if buf: paras.append(' '.join(buf)); buf = []
            continue
        if is_head(s) or is_noise(s):
            continue
        buf.append(s)
    if buf: paras.append(' '.join(buf))
    paras = [re.sub(r'\s+', ' ', re.sub(r'(\w)- (?=[a-z])', r'\1', p)).strip() for p in paras]
    merged = []
    for p in paras:
        if merged and (re.match(r'^[a-z\)\],;:]', p) or re.search(r'[a-z,;—-]$', merged[-1])):
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged

COMMON = [
 (r'[“”]', '"'), (r'[‘’]', "'"), (r"''", '"'),
 (r'\s+([;:,!?]|\.(?!\d))', r'\1'),
]
def emend(t, fixes):
    for a, b in COMMON + fixes:
        t = t.replace(a[1:], b) if a.startswith('=') else re.sub(a, b, t)
    return re.sub(r'\s+', ' ', t).strip()

# ------------------------------------------------------------ Science 1929
assert 'A MECHANICAL PARALLEL TO THE CON-' in SCI[2303 - 1]
assert 'UNIVERSITY OF WISCONSIN' in SCI[2513 - 1]
assert 'germinal idea' in SCI[2507 - 1]
sci_lines = rng(SCI, 2306, 2510, [(2354, 2414)])
SFIX = [
 (r'trial-anderror', 'trial-and-error'), (r'mercurytoluene', 'mercury-toluene'),
 (r'^iis "mouth waters', 'his "mouth waters'), (r'\biis "mouth', 'his "mouth'),
 (r'\brefiex\b', 'reflex'), (r'birth; -in the second', 'birth; in the second'),
 (r'the contact of the food Nevertheless, in both cases substantially the same reaction follows\. with the mouth\.',
  'the contact of the food with the mouth. Nevertheless, in both cases substantially the same reaction follows.'),
 (r'\bbehavioristie\b', 'behavioristic'), (r'\bbasie\b', 'basic'), (r'support this view\.1 As', 'support this view. As'),
 (r'\bextine- tion\b|\bextinetion\b', 'extinction'),
]
sci = [{'txt': emend(p, SFIX)} for p in harvest(sci_lines)]
# the twelve duplicated phenomena stand as one list
i = next(n for n, u in enumerate(sci) if u['txt'].startswith('(1)'))
j = next(n for n, u in enumerate(sci) if u['txt'].startswith('(12)'))
sci[i:j + 1] = [{'txt': ' '.join(u['txt'] for u in sci[i:j + 1])}]
sig = [u for u in sci if 'HULL' in u['txt'].upper() and 'WISCONSIN' in u['txt'].upper()]
for u in sig: sci.remove(u)
sci.append({'txt': 'Clark L. Hull · H. D. Baernstein · University of Wisconsin'})

# ------------------------------------------------------------ Psych. Rev. 1930
assert 'It is only with the greatest difficulty' in PR[3710 - 1]
end = next(n for n in range(4700, 4760) if 'may be realized' in PR[n - 1])
FIG = [(3747, 3750), (3755, 3755), (3792, 3800), (3858, 3870), (3887, 3893), (3905, 3922),
       (4410, 4422), (4432, 4436), (4474, 4474), (4520, 4523), (4534, 4540)]
FOOT = [(3815, 3821), (3997, 3999), (4059, 4065), (4213, 4221), (4302, 4311),
        (4377, 4387), (4499, 4508), (4635, 4635)]
pr_lines = rng(PR, 3710, end, FIG + FOOT)
S = lambda d: ''.join('₀₁₂₃₄₅₆₇₈₉'[int(c)] for c in d)
PFIX = [
 (r'Here Sj, Sz, etc\.,', 'Here S₁, S₂, etc.,'),
 (r'themselves\.! R, in itself has no power of causing \(evoking\) R,\.', 'themselves. R₁ in itself has no power of causing (evoking) R₂.'),
 (r'placing of R, after R; is', 'placing of R₂ after R₁ is'),
 (r'R» follows R; because S; follows S;\.', 'R₂ follows R₁ because S₂ follows S₁.'),
 (r'by the S > R ~5 sequences', 'by the S → R → s sequences'),
 (r'Fig\. 3, S, coinciding in time with s,, S; with s2', 'Fig. 3, S₂ coinciding in time with s₁, S₃ with s₂'),
 (r'how can Rs, which is a reaction to the stimulating event S;, take place before S; itself',
  'how can R₅, which is a reaction to the stimulating event S₅, take place before S₅ itself'),
 (r'not yet 11 existence', 'not yet in existence'), (r'existenc« cannot', 'existence cannot'),
 (r'which it parallels\.\?, Thus', 'which it parallels. Thus'), (r'<A great deal', 'A great deal'),
 (r'above, S; is a seriously nocuous stimulus and R; is', 'above, S₅ is a seriously nocuous stimulus and R₅ is'),
 (r'so that 54 will evoke R; before S; has occurred\. In this event Ss,', 'so that s₄ will evoke R₅ before S₅ has occurred. In this event S₅,'),
 (r'result of the act Rs\. In case R; is', 'result of the act R₅. In case R₅ is'),
 (r'latter before S; is reached', 'latter before S₅ is reached'),
 (r"^'whose sole function|'whose sole function", 'whose sole function'),
 (r'R;, the actual defense reaction', 'R₅, the actual defense reaction'),
 (r'high degree\. 4, on the other hand', 'high degree. R₄, on the other hand'),
 (r'Without R, there would be no s4, and without s4 there would be no R; 1\.e\. no defense\. In short, R, is',
  'Without R₄ there would be no s₄, and without s₄ there would be no R₅ i.e. no defense. In short, R₄ is'),
 (r'In the same way R; and R;, serve', 'In the same way R₃ and R₂ serve'),
 (r'\bealarged\b', 'enlarged'), (r'\bfreeand\b', 'free and'), (r'\bindispensible\b', 'indispensible'),
 (r'symbolism\.\*', 'symbolism.'), (r'goal act\.‘|goal act\.\'', 'goal act.'),
 (r'\baninstrumental\b', 'an instrumental'), (r'an instant\." 5', 'an instant."'),
 (r'this persisting stimulus by S,\.', 'this persisting stimulus by Sₚ.'),
 (r'shows that S, has a unique advantage', 'shows that Sₚ has a unique advantage'),
 (r'Thus, S;, So, etc\. and 51, 52, etc\.', 'Thus, S₁, S₂, etc. and s₁, s₂, etc.'),
 (r"associative tendencies,' only", 'associative tendencies, only'),
 (r'associative tendencies,\'', 'associative tendencies,'), (r'\bhumber\b', 'number'),
 (r'1\.¢\. to but', 'i.e. to but'), (r'But S,, since', 'But Sₚ, since'),
 (r'in\. Fig\. 7\.', 'in Fig. 7.'), (r'radiating from S, will', 'radiating from Sₚ will'),
 (r'first phase, S}\.', 'first phase, S₁.'),
 (r'assume that s, has an excitatory tendency toward R, of 2 units, that S, also has an excitatory tendency toward R, of 2 units, toward R; of 3 units, towards R, of 4 units and towards R; of 5 units',
  'assume that s₁ has an excitatory tendency toward R₂ of 2 units, that Sₚ also has an excitatory tendency toward R₂ of 2 units, toward R₃ of 3 units, towards R₄ of 4 units and towards R₅ of 5 units'),
 (r'reaction \(R,\) in the original', 'reaction (R₂) in the original'),
 (r'reactions such as R3, Ry, and Rs,', 'reactions such as R₃, R₄, and R₅,'),
 (r'that arising only from S,\.', 'that arising only from Sₚ.'), (r'single \(S,\) excitatory', 'single (Sₚ) excitatory'),
 (r'case that S, gets conditioned', 'case that Sₚ gets conditioned'), (r"is approached\.'", 'is approached.'),
 (r'from the second stimulus complex as follows:$', 'from the second stimulus complex as follows: R₂ = 4, R₃ = 3, R₄ = 4, R₅ = 5.'),
 (r'not R» as in the original act sequence, but R;\. But if R; follows immediately after R:,',
  'not R₂ as in the original act sequence, but R₅. But if R₅ follows immediately after R₁,'),
 (r'\bthanever\b', 'than ever'), (r'bec»me', 'become'), (r"chaining tendency\.'", 'chaining tendency.'),
 (r'\bparailel\b', 'parallel'), (r'(\w)- (?=[a-z])', r'\1'), (r'\bstimulusresponse\b', 'stimulus-response'),
 (r'49 X 67', '49 × 67'), (r"called 'short-circuiting\.\"", "called 'short-circuiting.'"), (r'in\. Fig\. 7\.', 'in Fig. 7.'), (r'faster rat»,', 'faster rate,'),
]
wissen = [{'txt': emend(p, PFIX)} for p in harvest(pr_lines)]

def U(us, frag):
    hit = [u for u in us if frag in u['txt']]
    assert len(hit) == 1, f'unit not found or ambiguous: {frag!r}'
    return hit[0]

def add(u, note):
    u['note'] = (u['note'] + ' — ' + note) if u.get('note') else note

FN = lambda t: 'Footnote: "' + t + '"'
# Science: the one footnote, and the diagram-free original
add(U(sci, 'to support this view.'), FN('The most significant summary of the Russian experimental '
    'results now available to English readers is the recent translation of I. P. Pavlov\'s great '
    'work, "Conditioned Reflexes." Oxford University Press, 1927.'))
# 1930: footnotes, read from the page images
add(U(wissen, 'direct causal relationship among themselves'), FN('This neglects the original dynamic '
    'influence of the ever-present internal component of the organismic stimulus complex into which '
    'each phase of the world sequence enters to evoke the corresponding organismic reaction. The '
    'excitatory potency of this internal component is here supposed to be minimal. Its influence is '
    'neglected in the interest of simplicity of exposition. Its undeniable presence clearly introduces '
    'an element of subjectivity into reactions which appear superficially to be evoked purely by the '
    'external world.'))
add(U(wissen, 'master world sequence which it parallels'), FN('C. L. Hull, A functional interpretation '
    'of the conditioned reflex, Psychol. Rev., 1929, 36, p. 507 ff. A quite distinct mechanism serving '
    'much the same function as that here emphasized has its basis in the peculiar advantage afforded by '
    'distance receptors. The stimulus of a distant object through a distance receptor is often '
    'sufficiently like that when the object is near and nocuous to evoke a successful defense reaction '
    'before the source of danger can get near enough to produce injury. This has been discussed in '
    'detail by Howard C. Warren, J. Phil., Psychol. & Scient. Meth., 1916, 13, p. 35 ff.'))
add(U(wissen, 'individual—symbolism'), FN('This peculiarly individual form of symbolism is not to be '
    'confused with the purely stimulus acts of social communication. Neither is it to be confused with '
    'what appears to be a derivative of the latter by a reduction process, the subvocal speech '
    'emphasized by Watson. The special stimulus-response mechanisms by which the evolution of these '
    'latter forms of symbolism take place, together with their peculiar potentialities for mediating '
    'biological adjustment and survival, are so complex as to preclude consideration here.'))
add(U(wissen, 'the final instrumental or goal act.'), FN('Movements greatly reduced in magnitude tend to '
    'become vestigial. This suggests a possible explanation of the extreme subjectivity of imagery. '
    'Just how far the weakening of pure stimulus acts may go and still serve their stimulus function is '
    'a question which may yield to experimental approach. That they should diminish to an actual zero, '
    'with nothing but a neural vestige remaining to perform the stimulus function, is conceivable '
    'though hardly probable. It is believed that the present hypothesis is general enough to fit '
    'either alternative.'))
add(U(wissen, 'There is in all these cases a noticeable tendency'), FN('E. L. Thorndike, Animal '
    'intelligence, MacMillan, 1911, p. 48.'))
add(U(wissen, 'except for remote associative tendencies'), FN('These are here neglected in order to '
    'simplify the exposition. Ultimately they must, of course, be taken fully into account.'))
add(U(wissen, 'is approached. Accordingly'), FN('It would not appear to be an over difficult task to '
    'test this hypothesis experimentally. If it should prove true it would have extensive theoretical '
    'implications and would clear up a number of questions in the theory of learning. However, almost '
    'any other hypothesis which provides considerable variation in the strength of the excitatory '
    'tendencies radiating from Sₚ will produce substantially similar results. It may be added that an '
    'irregular distribution of intensities of excitatory tendencies from Sₚ offers special '
    'opportunities for backward serial segment elimination as contrasted with the more usual forward '
    'variety here emphasized.'))
add(U(wissen, 'transcending the chaining tendency'), FN('See E. L. Thorndike, The original nature of '
    'man, New York, 1913, 186-187.'))
FIGN = {
 'shown in Fig. 1': 'Fig. 1 (p. 511): the world sequence S₁ → S₂ → S₃ → S₄ → S₅.',
 'diagrammatically in Fig. 2': 'Fig. 2 (p. 512): each Sₙ of the world sequence evokes a reaction Rₙ in the organism.',
 'as shown in Fig. 3': 'Fig. 3 (p. 513): each Rₙ now also produces an internal stimulus sₙ.',
 'as shown in Fig. 4': 'Fig. 4 (p. 513): dotted rectangles enclose each redintegrative stimulus complex (Sₙ₊₁ with sₙ); dotted arrows mark the newly acquired excitatory tendencies from sₙ to Rₙ₊₁.',
 'shown diagrammatically in Fig. 5': 'Fig. 5 (p. 513): the world sequence interrupted after S₁; the organism runs on R₁ → s₁ → R₂ → s₂ → … by itself.',
 'represented in Fig. 6': 'Fig. 6 (p. 520): the persisting stimulus Sₚ present in every stimulus complex of the series.',
 'diagrammatically in Fig. 7': 'Fig. 7 (p. 520): Sₚ with excitatory tendencies to R₁, R₂, R₃, R₄, R₅.',
 'shown in Fig. 8': 'Fig. 8 (p. 521): from the second stimulus complex, s₁ → R₂ with 2 units; Sₚ → R₂, R₃, R₄, R₅ with 2, 3, 4, 5 units.',
 'shown in Fig. 9 drops': 'Fig. 9 (p. 522): the segment R₂ → s₂ → R₃ → s₃ → R₄ → s₄ that drops out.',
}
for frag, desc in FIGN.items():
    add(U(wissen, frag), 'Diagram not reproduced — ' + desc)
add(U(wissen, 'R₂ = 4, R₃ = 3'), 'The four values are set as a column at the head of p. 522.')

LAB = [
 (sci, 'It is common knowledge', 'The mouth that waters'),
 (sci, 'offers a challenge to the attempt at a synthetic verification', 'Synthetic verification'),
 (sci, 'polarizable cells and mercury', 'The machine'),
 (sci, '(1) The simple substitution', 'Twelve phenomena duplicated'),
 (wissen, 'It is only with the greatest difficulty', 'A naturalistic attitude'),
 (wissen, 'One of the oldest problems', 'I. How can one physical object know another?'),
 (wissen, 'the organism may be said to know the world', 'The world stamped upon the organism'),
 (wissen, 'Once the organism has acquired', 'II. Foresight'),
 (wissen, 'A reflective consideration of the habit mechanisms', 'III. Pure stimulus acts'),
 (wissen, 'buttons his coat with one hand', 'The buttoning experiment'),
 (wissen, "'psychic' machine", "A 'psychic' machine"),
 (wissen, 'Pure stimulus-act sequences present certain unique', 'IV. Economy of energy and time'),
 (wissen, 'There is in all these cases a noticeable tendency', "Thorndike's cats, again"),
 (wissen, 'The importance of the serial-segment elimination', 'V. Purpose as a persisting stimulus'),
 (wissen, 'It is evident that in a situation such as is presented', 'VI. Intraserial competition'),
 (wissen, 'the product of 49', '49 × 67'),
 (wissen, 'The results of the present inquiry', 'VII. Summary'),
]
for us, frag, lab in LAB:
    U(us, frag)['label'] = lab

if '--dump' in sys.argv:
    for name, us in (('science', sci), ('wissen', wissen)):
        print('=====', name)
        for i, u in enumerate(us):
            print(i + 1, '|', u.get('label', ''), '|', u['txt'])
            if u.get('note'): print('   NOTE:', u['note'][:160])
    raise SystemExit

s1 = [dict({'n': i + 1, 'k': i + 1}, **u) for i, u in enumerate(sci)]
s2 = [dict({'n': i + 1, 'k': len(s1) + i + 1}, **u) for i, u in enumerate(wissen)]
out = {
 'id': 'hull_machines',
 'autor': 'Clark L. Hull · H. D. Baernstein',
 'titel': 'A Mechanical Parallel to the Conditioned Reflex (1929) · Knowledge and Purpose as Habit Mechanisms (1930) — complete',
 'jahr': 1929,
 'zitierweise': 'MPC [k] · KP [k]',
 'quelle': ("Both papers complete, from the journals' printings: Hull and Baernstein, 'A "
            "Mechanical Parallel to the Conditioned Reflex', Science 70, no. 1801 (5 July 1929), "
            "pp. 14–15, Internet Archive sim_science_1929-07-05_70_1801; Hull, 'Knowledge and "
            "Purpose as Habit Mechanisms', Psychological Review 37, no. 6 (November 1930), "
            "pp. 511–525, Internet Archive sim_psychological-review_1930-11_37_6. Both are in "
            "the United States public domain (the 1930 paper since 1 January 2026). OCR emended "
            "against the sense; the 1930 paper's subscripts and footnotes were read from the "
            "page images and are set by hand, and its nine diagrams, not reproduced, are "
            "described where they stand. Cited as 'MPC [k]' (Science) and 'KP [k]' (Psychological "
            "Review), k unique across the module. The 1931 sequel, Baernstein and Hull's 'A "
            "Mechanical Model of the Conditioned Reflex' (Journal of General Psychology), joins "
            "on 1 January 2027."),
 'hinweis': ("The corpus ends where the machines begin to learn. In 1929 Hull and Baernstein "
             "report a device of polarizable cells and mercury-toluene regulators, switches for "
             "receptors and a flashlight bulb for a salivary gland, that duplicates twelve "
             "phenomena of Pavlov's conditioned reflex — and draw the conclusion outright: "
             "'Learning and thought are here conceived as by no means necessarily a function of "
             "living protoplasm any more than is aerial locomotion.' A year later Hull derives "
             "knowledge, foresight, symbolic thought and purpose from habit alone, and predicts "
             "that 'a \"psychic\" machine' could attain 'a degree of freedom, spontaneity, and "
             "power to dominate its environment' inconceivable to the designers of rigid "
             "machines. From here the line runs, beyond the threshold of this collection, to "
             "Hull's Principles of Behavior (1943) and the learning machines that followed."),
 'sections': [
   {'id': 'science', 'titel': 'Hull & Baernstein, A Mechanical Parallel to the Conditioned Reflex — Science, 5 July 1929 (complete)', 'units': s1},
   {'id': 'wissen', 'titel': 'Hull, Knowledge and Purpose as Habit Mechanisms — Psychological Review, November 1930 (complete)', 'units': s2},
 ],
}
path = os.path.join(REPO, 'data', 'hull_machines.json')
json.dump(out, io.open(path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('wrote', path, '-', [len(s1), len(s2)], 'units')
