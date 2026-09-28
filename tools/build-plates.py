# -*- coding: utf-8 -*-
# Build assets/plates/ and data/plates.json — one public-domain plate per
# shipped module: title pages, the first page of a journal article, and a
# figure, from the same digitisations the editions cite, fetched page by
# page over IIIF (no full scans are downloaded or carried). Faithful
# reproduction of a public-domain two-dimensional work adds nothing
# licensable; every plate names its source, digitisation and leaf below.
# Plates are added as modules ship.
# Usage: python tools/build-plates.py          (needs the network)
import io, json, os, urllib.request
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'assets', 'plates')
os.makedirs(OUT, exist_ok=True)

def ia(item, leaf, w=1400):
    return f"https://iiif.archive.org/iiif/{item}${leaf}/full/{w},/0/default.jpg"

PLATES = [
 { 'id': 'overview',
   # the site's visual anchor, shown on the overview page — the Google scan
   # of the first edition omits the plate pages, so this one leaf comes from
   # the Wellcome Collection copy of the same 1883 printing
   'url': ia('b21914631', 8),
   'caption': "Specimens of Composite Portraiture — the frontispiece of "
              "Galton's Inquiries (1883): faces averaged into statistical "
              "portraits. The corpus's thesis in one plate, and the very "
              "plate the Galton module's composite chapter describes, "
              "panel by panel.",
   'credit': "Galton, Inquiries into Human Faculty and its Development "
             "(London: Macmillan, 1883), frontispiece. Internet Archive "
             "b21914631 (Wellcome Collection copy), leaf 8. Public "
             "domain." },
 { 'id': 'fechner',
   'url': ia('elementederpsych001fech', 9),
   'caption': "Title page of the first edition: Elemente der Psychophysik, "
              "Leipzig 1860 — the measured mind's founding book.",
   'credit': "Elemente der Psychophysik, vol. I (Leipzig: Breitkopf und "
             "Härtel, 1860). Internet Archive elementederpsych001fech, "
             "leaf 9. Public domain." },
 { 'id': 'ebbinghaus',
   'url': ia('memorycontributi00ebbiuoft', 7),
   'caption': "Title page of the translation this edition carries: Memory, "
              "New York 1913.",
   'credit': "Ebbinghaus, Memory: A Contribution to Experimental "
             "Psychology, trans. Ruger & Bussenius (New York: Teachers "
             "College, 1913). Internet Archive memorycontributi00ebbiuoft, "
             "leaf 7. Public domain." },
 { 'id': 'huxley',
   'url': ia('methodandresult01huxlgoog', 6),
   'caption': "Title page of Collected Essays, vol. I: Method and Results — "
              "the volume that carries the automaton address.",
   'credit': "T. H. Huxley, Method and Results: Essays (New York: D. "
             "Appleton and Company, 1894). Internet Archive "
             "methodandresult01huxlgoog, leaf 6. Public domain." },
 { 'id': 'spearman',
   'url': ia('jstor-1412107', 1),
   'caption': "The first page of the paper as printed: American Journal of "
              "Psychology 15 (1904), p. 201 — general intelligence, "
              "objectively determined and measured.",
   'credit': "Spearman, “General Intelligence,” AJP 15 (1904). "
             "Internet Archive jstor-1412107 (JSTOR Early Journal "
             "Content), leaf 1. Public domain." },
 { 'id': 'galton',
   # this Google-digitised item times out above ~800px wide
   'url': ia('inquiriesintohu00galtgoog', 8, w=800),
   'caption': "Title page of the first edition: Inquiries into Human "
              "Faculty and its Development, London 1883 — the book that "
              "coins the word 'eugenics'.",
   'credit': "Galton, Inquiries into Human Faculty and its Development "
             "(London: Macmillan, 1883). Internet Archive "
             "inquiriesintohu00galtgoog, leaf 8. Public domain." },
 { 'id': 'binet',
   # this digitisation too times out above ~800px wide
   'url': ia('developmentofint00binerich', 9, w=800),
   'caption': "Title page of the Vineland translation: The Development of "
              "Intelligence in Children (The Binet-Simon Scale), 1916 — "
              "the edition that carried the scale into English.",
   'credit': "Binet & Simon, The Development of Intelligence in Children, "
             "trans. Elizabeth S. Kite (Vineland, N.J.: The Training "
             "School, 1916). Internet Archive developmentofint00binerich, "
             "leaf 9. Public domain." },
 { 'id': 'morgan',
   # the cited Google scan's front matter is unusable, so this one leaf
   # comes from the Toronto copy of the same first printing
   'url': ia('introductiontoco00morg', 7, w=800),
   'caption': "Title page of the first edition: An Introduction to "
              "Comparative Psychology, London 1894 — the book of the "
              "canon.",
   'credit': "C. Lloyd Morgan, An Introduction to Comparative Psychology "
             "(London: Walter Scott, 1894). Internet Archive "
             "introductiontoco00morg (University of Toronto copy), "
             "leaf 7. Public domain." },
 { 'id': 'loeb',
   'url': ia('comparativephysi00loeb', 11, w=600),
   'caption': "Title page of the 1900 printing: Comparative Physiology of "
              "the Brain and Comparative Psychology — the tropism-machine's "
              "book, dedicated to Ernst Mach.",
   'credit': "Jacques Loeb, Comparative Physiology of the Brain and "
             "Comparative Psychology (New York: G. P. Putnam's Sons, "
             "1900). Internet Archive comparativephysi00loeb, leaf 11. "
             "Public domain." },
 { 'id': 'watson',
   # microfilm scan: film borders trimmed by IIIF region; times out above ~600px
   'url': ('https://iiif.archive.org/iiif/sim_psychological-review_1913-03_20_2'
           '$69/pct:10,6,82,88/600,/0/default.jpg'),
   'caption': "The manifesto's first page as printed: Psychological "
              "Review 20 (1913), p. 158 — 'a purely objective "
              "experimental branch of natural science.'",
   'credit': "Watson, “Psychology as the Behaviorist Views It,” "
             "Psychological Review 20 (1913). Internet Archive "
             "sim_psychological-review_1913-03_20_2, leaf 69 (film "
             "borders trimmed). Public domain." },
 { 'id': 'pavlov',
   # margins trimmed by IIIF region; this item times out above ~800px
   'url': ('https://iiif.archive.org/iiif/conditionedrefle0000ippa'
           '$52/pct:11,2,81,88/700,/0/default.jpg'),
   'caption': "The double chamber, as the 1927 plates show it: the dog "
              "on its stand in the animal's section (Fig. 4), the "
              "experimenter at his registering apparatus beyond the "
              "sound-proof partition (Fig. 5) — the separation Lecture II "
              "describes.",
   'credit': "Pavlov, Conditioned Reflexes, trans. G. V. Anrep (London: "
             "Oxford University Press, 1927), Figs. 4–5. Internet Archive "
             "conditionedrefle0000ippa, leaf 52 (margins trimmed). Public "
             "domain in the United States." },
 { 'id': 'mcdougall',
   'url': ia('cu31924029080880', 6, w=800),
   'caption': "Title page of Body and Mind: A History and a Defense of "
              "Animism, in the Methuen printing of 1918 — the soul's last "
              "full-dress defence before the machines arrived.",
   'credit': "William McDougall, Body and Mind (London: Methuen, 1918; "
             "first published 1911). Internet Archive cu31924029080880 "
             "(Cornell copy), leaf 6. Public domain." },
 { 'id': 'hull_machines',
   'url': ('https://archive.org/download/sim_psychological-review_1930-11_37_6/'
           'page/n58_w1100.jpg'),
   'crop': (0.14, 0.12, 0.80, 0.84),
   'caption': "Psychological Review, November 1930, p. 513: Hull's diagrams of "
              "'The World' and 'The Organism' — the world sequence stamping a "
              "parallel sequence of reactions upon the organism, which then runs "
              "on by itself (Figs. 3–5).",
   'credit': "Clark L. Hull, 'Knowledge and Purpose as Habit Mechanisms', "
             "Psychological Review 37 (1930), p. 513. Internet Archive "
             "sim_psychological-review_1930-11_37_6, page n58, film borders "
             "trimmed. Public domain in the United States since 1 January 2026." },
 { 'id': 'hull_aptitude',
   'url': 'https://archive.org/download/aptitudetesting00hull/page/n507_w1000.jpg',
   'crop': (0.08, 0.08, 0.95, 0.87),
   'caption': "Fig. 60: the perforated paper tape on which a subject's test scores "
              "are punched for the aptitude-prediction machine — 9, 24, 365, and so "
              "on — the edge holes to feed it through.",
   'credit': "Clark L. Hull, Aptitude Testing (Yonkers-on-Hudson: World Book "
             "Company, 1928), p. 488, Fig. 60. Internet Archive "
             "aptitudetesting00hull, page n507, cropped. Public domain in the "
             "United States." },
 { 'id': 'hartley',
   # microfilm frame of an ECCO copy; page image cropped to the title leaf
   'url': ('https://archive.org/download/bim_eighteenth-century_observations-'
           'on-man-his_hartley-david_1749_1/page/n2_w1000.jpg'),
   'crop': (0.10, 0.02, 0.93, 0.95),
   'caption': "Title page of the first edition, London 1749 — 'Printed by "
              "S. Richardson', the printer-novelist of Pamela and Clarissa: "
              "the book in which association became a mechanism of mind.",
   'credit': "David Hartley, Observations on Man, his Frame, his Duty, and "
             "his Expectations (London: S. Richardson for James Leake and "
             "Wm. Frederick, 1749), vol. I, title page. Internet Archive "
             "bim_eighteenth-century_observations-on-man-his_hartley-"
             "david_1749_1 (Eighteenth Century Collections Online "
             "microfilm), page n2, cropped. Public domain." },
 { 'id': 'koehler',
   # the DLI scan the edition cites carries no plates, and this copy's IIIF
   # endpoint times out: the page image, cropped to photograph and legend
   'url': 'https://archive.org/download/mentalityofapes0000kohl_p5t8/page/n144_w800.jpg',
   'crop': (0.07, 0.15, 0.94, 0.73),
   'caption': "Plate III: Sultan making a double-stick — a still from a "
              "film taken a month after the first joining, which the "
              "chapter on chance calls the accident that 'led at once to "
              "insight'.",
   'credit': "Wolfgang Köhler, The Mentality of Apes, trans. Ella Winter "
             "(London: Kegan Paul, 1927), Plate III, facing p. 128. "
             "Internet Archive "
             "mentalityofapes0000kohl_p5t8 (a later Routledge reprint of "
             "the 1927 setting), page n144, margins trimmed. Public domain "
             "in the United States." },
 { 'id': 'bain',
   'url': ia('sensesintellectb00bain', 7, w=800),
   'caption': "Title page of The Senses and the Intellect, London 1855 — "
              "the first edition, in which random spontaneity, the "
              "volitional spur of feeling and the Law of Contiguity are "
              "set down as the ground plan of learning.",
   'credit': "Alexander Bain, The Senses and the Intellect (London: John "
             "W. Parker and Son, 1855). Internet Archive "
             "sensesintellectb00bain (Library of Congress copy), leaf 7. "
             "Public domain." },
 { 'id': 'james',
   # journal scan: film margins trimmed by IIIF region, capped near 600px
   'url': ('https://iiif.archive.org/iiif/sim_mind_1879-01_4_13'
           '$0/pct:8,4,84,90/600,/0/default.jpg'),
   'caption': "Mind, January 1879: the journal's masthead and the first "
              "page of 'Are We Automata?' — whose opening sentence names "
              "Huxley's Belfast address.",
   'credit': "William James, “Are We Automata?”, Mind IV, no. 13 "
             "(January 1879), p. 1 (University of Minnesota library "
             "copy). Internet Archive sim_mind_1879-01_4_13, leaf 0, "
             "margins trimmed. Public domain." },
 { 'id': 'thorndike',
   # the IIIF endpoint refuses this Google-digitised item above ~600px wide
   'url': ia('animalintellige00thorgoog', 43, w=600),
   'caption': "The puzzle box as the print shows it — Fig. 1 on p. 30, the "
              "drawing the module's apparatus description refers to.",
   'credit': "Thorndike, Animal Intelligence (New York: Macmillan, 1911). "
             "Internet Archive animalintellige00thorgoog, leaf 43. Public "
             "domain." },
]

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':
        'psychpred-plates (psychological-predecessors-of-ai.netlify.app)'})
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=90).read()
        except Exception as e:
            err = e
    raise err

import sys
force = '--force' in sys.argv
reg = {}
for p in PLATES:
    dest = os.path.join(OUT, p['id'] + '.jpg')
    if force or not os.path.exists(dest):
        im = Image.open(io.BytesIO(fetch(p['url']))).convert('RGB')
        if p.get('crop'):   # for page images served without IIIF regions
            l, t, r, b = p['crop']
            im = im.crop((round(l * im.width), round(t * im.height),
                          round(r * im.width), round(b * im.height)))
        if im.width > 1400:
            im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(dest, quality=82, optimize=True)
        th = im.copy(); th.thumbnail((300, 480), Image.LANCZOS)
        th.save(os.path.join(OUT, p['id'] + '_t.jpg'), quality=80, optimize=True)
        print('plate', p['id'], im.size)
    else:
        print('plate', p['id'], 'kept')
    reg[p['id']] = {'caption': p['caption'], 'credit': p['credit']}

path = os.path.join(REPO, 'data', 'plates.json')
json.dump(reg, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', path, '-', len(reg), 'plates')
