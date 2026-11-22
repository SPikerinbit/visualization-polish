"""Verify each printed numeric row in R14 against corresponding R13 positions."""
from pathlib import Path
from lxml import etree as E
from collections import Counter
from json import dumps
O=Path(__file__).resolve().parent
R13=O.parents[1]/'multi-reference-r13/sw/sw.svg'
cfg={R13:((0,80.1,160.2,240.3),(3,21.025,39.475,57.925),[28.86,41.86,60.86]),O/'sw.svg':((27,99,171,240.3),(27,44,61,78),[26.9,39.83,61.0])}
def assign(n,starts):
 return sum(n>=v for v in starts)-1
def parse(path):
 (axes,grid,yco)=cfg[path]
 root=E.parse(str(path))
 rows=[[[] for _ in range(3)] for _ in range(3)]
 for n in root.xpath('//*[local-name()="text"]'):
  if not (n.text or '').isdigit():continue
  x,y=map(float,(n.get('x'),n.get('y')))
  rd=assign(x,axes)
  layer=min(range(3),key=lambda i:abs(y-yco[i]))
  assert abs(y-yco[layer])<.1,(x,y,yco)
  g=None if layer==2 else assign(x-(axes[rd]-axes[0]),grid)
  rows[rd][layer].append((x,int(n.text),g))
 return [[[z[1:] for z in sorted(layer)] for layer in rd] for rd in rows]
b,a=parse(R13),parse(O/'sw.svg')
assert a==b
counter=Counter()
for rd,(unread,buf,ranks) in enumerate(a,1):
 buffered={v:g for v,g in buf}
 assert set(buffered)=={v for v,g in ranks}
 assert sorted(buffered)==[v for v,g in ranks]
 unread_g={g for v,g in unread}
 nt=Counter(buffered.values())
 def emitted_rows():
  for v,_ in ranks:
   g=buffered[v]
   yield v
   nt[g]-=1
   if nt[g]==0 and g in unread_g:return
 emit=list(emitted_rows())
 assert emit==[list(range(1,6)),list(range(6,11)),list(range(11,17))][rd-1]
 print(f'Round {rd}: unread, window, and ranked order identical; emits {emit}')
 counter.update((len(unread),len(buf),len(ranks)))
assert sum(k*v for k,v in counter.items())==55
