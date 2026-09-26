# -*- coding: utf-8 -*-
# Corpus checker: registry <-> data files, unit numbering, cite fields.
# Exit 1 on errors. Usage: python tools/check-corpus.py
import glob, io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
errors, warns = [], []

works = json.load(io.open('data/works.json', encoding='utf-8'))
LINES = {'messen', 'lernen', 'automat', 'labor'}
texts = {}
for w in works:
    for f in ('id', 'linie', 'status', 'autor', 'leben', 'kurz', 'titel', 'sprachen', 'claim'):
        if not w.get(f):
            errors.append(f"{w.get('id')}: registry field {f} empty")
    if w['linie'] not in LINES:
        errors.append(f"{w['id']}: unknown line {w['linie']}")
    if w['status'] == 'shipped':
        p = os.path.join('data', w.get('datei', '') + '.json')
        if not w.get('datei') or not os.path.exists(p):
            errors.append(f"{w['id']}: shipped but data file missing"); continue
        texts[w['id']] = json.load(io.open(p, encoding='utf-8'))
    elif not w.get('geplant'):
        errors.append(f"{w['id']}: planned but no source plan")

registered = {w.get('datei') for w in works if w.get('datei')}
for p in glob.glob('data/*.json'):
    b = os.path.basename(p)[:-5]
    if b not in registered and b not in ('works', 'network', 'plates'):
        warns.append(f'unregistered data file: {b}')

total = 0
for wid, t in texts.items():
    for f in ('id', 'autor', 'titel', 'jahr', 'zitierweise', 'quelle', 'sections'):
        if not t.get(f):
            errors.append(f'{wid}: text field {f} empty')
    if t.get('id') != wid:
        errors.append(f'{wid}: text id mismatch ({t.get("id")})')
    for s in t.get('sections', []):
        us = s.get('units', [])
        if not us:
            errors.append(f'{wid}/{s.get("id")}: no units'); continue
        total += len(us)
        for i, u in enumerate(us):
            if u.get('n') != i + 1:
                errors.append(f'{wid}/{s["id"]}: unit n broken at index {i}'); break
            if not u.get('txt') or len(u['txt']) < 25:
                errors.append(f'{wid}/{s["id"]} [{u.get("n")}]: suspiciously short unit')
            if re.search(r'�|\btJi|AUTOMATISM|A\w*T[0O][MK]AT[I1]SM', u.get('txt', '')):
                errors.append(f'{wid}/{s["id"]} [{u["n"]}]: OCR damage marker in text')

shipped = [w for w in works if w['status'] == 'shipped']
print(f'registry: {len(works)} works, {len(shipped)} shipped')
print(f'units across shipped corpus: {total}')
for e in errors: print('ERROR:', e)
for w in warns: print('  ?', w)
print(f'\nERRORS: {len(errors)}\nWARNINGS: {len(warns)}')
sys.exit(1 if errors else 0)
