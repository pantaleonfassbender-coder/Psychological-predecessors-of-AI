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
