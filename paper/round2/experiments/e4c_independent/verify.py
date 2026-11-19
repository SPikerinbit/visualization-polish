"""Validate local fixture/means/fronts and actual independent vector assets.
This checks internal consistency, not scientific validity or measurements.
"""
from pathlib import Path
import json,hashlib
import fitz
import e4c
R=Path(__file__).resolve().parent
e4c.SOURCE=R/'data.json'
a=e4c.average(e4c.load_points());b=json.loads((R/'records.json').read_text())
assert len(a)==40 and a==b['means']
assert hashlib.sha256(e4c.SOURCE.read_bytes()).hexdigest()==b['source_sha256']
for metric in ['full','topk']:
 for state in ['Off','On-cold']:
  key=f'e4c-{metric}-{state.lower()}'
  assert e4c.nondominated([p for p in a if p['metric']==metric and p['state']==state])==b['fronts'][key]
 limits=[b['limits'][f'e4c-{metric}-{s}'] for s in ['off','on-cold']]
 assert limits[0]==limits[1]
paths=[*sorted((R/'panels').glob('*.pdf')),R/'e4c-legend.pdf'];assert len(paths)==5
for path in paths:
 page=fitz.open(path)[0]
 for w in page.get_text('words'):assert page.rect.contains(fitz.Rect(w[:4])),(path.name,w)
print('PASS: 40 equal-weight means, 4 exact fronts, shared per-metric axes, 4 independent panel PDFs + legend; no text outside canvas. Synthetic only.')
