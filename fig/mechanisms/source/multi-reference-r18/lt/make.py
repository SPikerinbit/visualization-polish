from lxml import etree as E
from pathlib import Path
import subprocess, os, re
D=Path(__file__).parent
ns="http://www.w3.org/2000/svg"
tree=E.parse(str(D/'r13-source.svg'))
s=tree.getroot()
def q(n):return '{'+ns+'}'+n
def group(id):return tree.xpath(f'//*[@id="{id}"]')[0]
def node(g,n,label=None,**kw):
    a=E.SubElement(g,q(n),{k.replace('_','-'):str(v) for k,v in kw.items()})
    if label is not None:a.text=label
    return a
s.set('height','89.5pt');s.set('viewBox','0 0 240.24655 89.5');s.find(q('rect')).set('height','89.5')
main=s.find(q('g'));main.set('font-family','Liberation Serif, serif')
ink='#292722'; gray='#515750'; muted='#57635C'; pale='#A8ADA5'
sep='#DAD8CB'; warm='#8B4E08'; amber='#FFE3AF'; teal='#285F4D'; sea='#E1EDE5'
shift={ '#252B2E':ink, '#28343C':ink, '#AC6D0B':warm, '#FFE3AE':amber, '#DDEBDD':sea, '#4F6B56':teal,'#425E4D':teal,'#69757C':muted,'#606E74':gray,'#8C989E':'#79837A','#B8C2C5':pale}
for a in s.iter():
    for k in ('fill','stroke'):
        if a.get(k) in shift:a.set(k,shift[a.get(k)])
before=group('read-path');after=group('after')
before.set('transform','translate(0 4)');after.set('transform','translate(0 4)')
for g,h in [(before,'(a) Collect top-down'),(after,'(c) Replay bottom-up')]:
    t=g.find(q('text'));t.set('y','5.0');t.set('font-size','7.2');t.text=h
    for ix,a in enumerate(g):
        if a.tag==q('text') and a.text in {'6','14'}:
            c=g[ix-1]
            if c.tag==q('circle'):
                c.set('fill',amber);c.set('stroke',warm);a.set('fill',warm);a.set('font-weight','bold')
                cx=float(c.get('cx')); cy=float(c.get('cy'))+2.65
                node(g,'path',d=f'M{cx-1.62} {cy} h3.24',stroke=warm,stroke_width='.48')
    for a in g:
        if a.tag==q('text') and a.text in ['R1','R2','R3','R4']:
            a.text='R'+str.translate(a.text[-1],str.maketrans('1234','₁₂₃₄')); a.set('font-size','6.1'); a.set('y','72.05')
def text(g,x,y,t,fs=6.15,c=ink,b=False,anc='middle'):
    return node(g,'text',t,x=x,y=y,fill=c,font_size=fs,text_anchor=anc,font_weight='bold' if b else 'normal')
# One pointer grammar: only downward tree pointers remain. The old teal
# diagonally upward replay arrow becomes a passive branch, and output pairs
# are read by the shared green Output symbol instead of local labels/arrows.
for t in (before,after):
    for a in list(t):
        if a.tag==q('line') and a.get('stroke')==teal:
            if a.get('x1')==a.get('x2') or float(a.get('x1'))==float(a.get('x2')):
                t.remove(a)
            else:
                a.set('stroke',pale)
                a.set('stroke-width','.44')
        elif a.tag==q('polygon') and a.get('fill')==teal:
            t.remove(a)
        elif a.tag==q('text') and a.text in ('(1)','[5, 6]','(2)'):
            t.remove(a)
# Compress each tree around its root, retaining round circles and avoiding
# anisotropically distorted print typography. Shift centers outward slightly
# to leave breathing room between all three phases.
for t,orig,center in [(before,53.,47.5),(after,187.2466,192.7466)]:
    def xx(x):return round(center+(float(x)-orig)*.91,4)
    for a in t:
        for k in ('x','cx','x1','x2'):
            if a.get(k) is not None:a.set(k,str(xx(a.get(k))))
        if a.tag==q('polygon'):
            a.set('points',' '.join(f'{xx(x)},{y}' for x,y in [pt.split(',') for pt in a.get('points').split()]))
        if a.tag==q('path'):
            x,y,dx=re.fullmatch(r'M([-\d.]+) ([-\d.]+) h([-\d.]+)',a.get('d')).groups()
            a.set('d',f'M{xx(x)} {y} h{float(dx)*.91}')
        if a.tag==q('text') and (a.text.isnumeric() or a.text=='∅'):
            a.set('font-size','6.0')
# All surviving arrows point from parent to child and encode the pointer
# stored in the corresponding snapshot. Ordinary branches stay light gray.
for t in (before,after):
    for a in t:
        if a.tag==q('line') and a.get('stroke')!=pale:
            a.set('stroke',ink)
            a.set('stroke-width','.78')
        if a.tag==q('polygon'):
            a.set('fill',ink)
# Main's dashed call-path enclosure, applied to the pre-refresh tree only.
# It encloses the three pair nodes sent to the ranker, not the prior output
# or any part of the sibling subtree. No tree geometry changes.
selection=node(before,'path',
    d='M36.7 33 C36.7 29 39.4 27.1 43 27.1 H52.2 '
      'C55.9 27.1 58.3 29.6 58.3 33.1 C58.3 37.1 55.9 38.9 51.8 39.0 '
      'H45.0 Q42.8 39.0 40.1 40.8 L36.6 43.1 '
      'C38.5 46.3 37.2 49.7 35.6 50.9 Q34.4 52.7 37.0 54.4 '
      'L42.8 56.1 C46.6 57.1 48.3 59.4 48.0 62.3 '
      'C47.9 66.0 45.5 67.6 42.3 67.6 H34.1 C30.3 67.6 28.4 65.5 28.4 62.1 '
      'C28.4 59.7 29.5 58.2 30.7 57.4 L27.3 52.8 H23.4 '
      'C19.4 52.8 16.9 50.5 16.9 46.9 C16.9 43.2 19.8 41.0 23.8 41.0 H30.7 '
      'Q33.2 40.9 35.2 38.9 L37.6 37.1 Q36.7 35.5 36.7 33 Z',
    fill='none',stroke=warm,stroke_width='.68',stroke_dasharray='1.45 1.1',stroke_linecap='round')
before.insert(1,selection)
# Rewrite the center card; inputs are three intact pairs, output is one order.
g=group('one-listwise-call');g.clear();g.set('id','one-listwise-call')
text(g,120.1233,9,'(b) ListwiseRank',7.2,ink,True)
# R15's visible three rank inputs and final order, with Fig. 2/3 tiles.
# Pair panels have mild underlays, not graph edges; no arrows traverse the trees.
neutral='#EDF1ED'; border='#B6BEB8'; shadow='#ECEFEA'
for x,vals,new in [(94.0,(3,4),False),(112.0,(5,7),False),(130.0,(6,14),True)]:
    node(g,'rect',x=x+.55,y=27.55,width=16.25,height=11.7,rx='.75',fill=shadow)
    node(g,'rect',x=x,y=27,width=16.25,height=11.7,rx='.75',fill='#F7F8F7',stroke=border,stroke_width='.42')
    for i,v in enumerate(vals):
        u=x+.83+i*7.7
        node(g,'rect',x=u,y=28.1,width=7.0,height=9.55,fill=amber if new else neutral)
        if new:node(g,'path',d=f'M{u+.4} 37.22 h6.2',stroke=warm,stroke_width='.56')
        text(g,u+3.5,35.02,str(v),6.0,warm if new else ink,new)
# Single transformation glyph, visually distinct from the tree pointer.
node(g,'path',d='M120.1 41.5 V47.5 m-1.45 -1.5 1.45 1.5 1.45 -1.5',stroke=gray,stroke_width='.64',fill='none',stroke_linecap='round',stroke_linejoin='round')
node(g,'rect',x=94.55,y=50.55,width=52.25,height=11.7,rx='.75',fill=shadow)
node(g,'rect',x=94.0,y=50.0,width=52.25,height=11.7,rx='.75',fill='#F7F8F7',stroke=border,stroke_width='.42')
for i,v in enumerate((3,4,5,6,7,14)):
    u=95.15+8.38*i
    new=v in (6,14)
    node(g,'rect',x=u,y=51.1,width=7.75,height=9.55,fill=amber if new else neutral)
    if new:node(g,'path',d=f'M{u+.4} 60.22 h6.95',stroke=warm,stroke_width='.56')
    text(g,u+3.875,58.02,str(v),6.0,warm if new else ink,new)
main.remove(group('bottom-up-order'))
g=group('legend');g.clear();g.set('id','legend')
node(g,'path',d='M1 78.5 H239',stroke=sep,stroke_width='.56')
ly=84.6
for x,c,f,t in [(4,warm,amber,'New from R₂'),(50.2,ink,'white','Stored'),
                (82.6,'#79837A','white','Unread'),(116.8,teal,sea,'Output')]:
    a=node(g,'circle',cx=x,cy=ly,r=2.3,stroke=c,stroke_width='.61',fill=f)
    if t=='Unread':a.set('stroke-dasharray','1.25 .8')
    if x==4:node(g,'path',d='M2.9 85.7 h2.2',stroke=warm,stroke_width='.45')
    text(g,x+4.45,86.9,t,6.15,ink,False,'start')
node(g,'path',d='M149.3 84.6 h5.35',stroke=ink,stroke_width='.78')
node(g,'path',d='M156 84.6 l-2.4 -1.25 v2.5 z',fill=ink)
text(g,158.45,86.9,'Pointer',6.15,ink,False,'start')
node(g,'rect',x=189.2,y=82.25,width=7.1,height=4.7,rx='.85',fill='none',
     stroke=warm,stroke_width='.68',stroke_dasharray='1.45 1.1',stroke_linecap='round')
text(g,198.7,86.9,'Refresh path',6.15,ink,False,'start')
s.find(q('desc')).text='The full tree is shown twice. After prior output [1,2], the pointers reach R2 along the dashed refresh path. One rank call orders [3,4], [5,7], and [6,14]. The lower replay forwards [5,6] and stores [7,14]. The root replay outputs [3,4] and stores [5,6]. Both replays reuse the same rank map. The next pointers go right at the root and left at the lower match; R2 is exhausted.'
tree.write(str(D/'lt.svg'),xml_declaration=True,encoding='utf-8')
subprocess.run(['inkscape',str(D/'lt.svg'),'--export-filename='+str(D/'lt.pdf')],check=True,env=dict(os.environ,XDG_CACHE_HOME=str(D/'cache'),XDG_CONFIG_HOME=str(D/'config')))
