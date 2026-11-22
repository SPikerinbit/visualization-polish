from lxml import etree as E
from pathlib import Path
import subprocess, os
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
shift={ '#252B2E':ink, '#28343C':ink, '#AC6D0B':warm, '#FFE3AE':amber, '#DDEBDD':sea, '#4F6B56':teal,'#425E4D':teal,'#69757C':muted,'#606E74':muted,'#8C989E':'#79837A','#B8C2C5':pale}
for a in s.iter():
    for k in ('fill','stroke'):
        if a.get(k) in shift:a.set(k,shift[a.get(k)])
before=group('read-path');after=group('after')
before.set('transform','translate(0 4)');after.set('transform','translate(0 4)')
for g,h in [(before,'(a) Follow pointers'),(after,'(c) Replay bottom-up')]:
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
            a.text='R'+str.translate(a.text[-1],str.maketrans('1234','₁₂₃₄')); a.set('font-size','6.1')
def text(g,x,y,t,fs=6.15,c=ink,b=False,anc='middle'):
    return node(g,'text',t,x=x,y=y,fill=c,font_size=fs,text_anchor=anc,font_weight='bold' if b else 'normal')
text(before,62.8,19.1,'Prior output',6.05,teal,True,'start')
text(after,198,19.1,'Next output',6.2,teal,True,'start')
# The 1,2 have already gone out. Do not draw an arrow from the still-stored 3,4.
for a in list(before):
    if (a.tag==q('line') and a.get('x1')=='53') or (a.tag==q('polygon') and a.get('points','').startswith('53.0000')):
        before.remove(a)
# Compact replay labels remain tied to the nodes (not arrow or pointer labels).
for a in list(after):
    if a.tag==q('text') and a.text in ('(1)','(2)'):a.set('font-size','5.9'); a.set('x',str(float(a.get('x'))+1.15))
# Change the two next-pointer arrows and add a separate key; R3's inherited pointer is muted.
for a in list(after):
    if a.tag in [q('line'),q('polygon')] and a.get('stroke',a.get('fill'))==muted:
        a.set('stroke' if a.tag==q('line') else 'fill',ink)
        if a.tag==q('line'):a.set('stroke-width','.78')
# Rewrite the center card; inputs are three intact pairs, output is one order.
g=group('one-listwise-call');g.clear();g.set('id','one-listwise-call')
text(g,120.1233,9,'(b) Rank once',7.2,ink,True)
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
# Single transformation glyph, visually distinct from either pointer family.
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
for x,c,f,t in [(4,warm,amber,'New from R₂'),(51,ink,'white','Stored'),(82,'#79837A','white','Unread')]:
    a=node(g,'circle',cx=x,cy=84.6,r=2.3,stroke=c,stroke_width='.61',fill=f)
    if t=='Unread':a.set('stroke-dasharray','1.25 .8')
    if x==4:node(g,'path',d='M2.9 85.7 h2.2',stroke=warm,stroke_width='.45')
    text(g,x+4.45,86.9,t,6.15,ink,False,'start')
for x,c,t in [(114,warm,'Follow pointer'),(161,ink,'Next pointer'),(202,teal,'Replay')]:
    node(g,'path',d=f'M{x} 84.75 h5.5',stroke=c,stroke_width=1 if c==warm else .8)
    node(g,'path',d=f'M{x+6.5} 84.75 l-2.4 -1.25 v2.5 z',fill=c)
    text(g,x+8.28,86.9,t,6.15,ink,False,'start')
s.find(q('desc')).text='The full tree is shown twice. After prior output [1,2], the amber pointers reach R2. One rank call orders [3,4], [5,7], and [6,14]. In replay (1), [5,6] travels up while [7,14] is stored. In (2), [3,4] is next output and [5,6] is stored. The next pointers go right at the root and left at the lower match; R2 is exhausted.'
tree.write(str(D/'lt.svg'),xml_declaration=True,encoding='utf-8')
subprocess.run(['inkscape',str(D/'lt.svg'),'--export-filename='+str(D/'lt.pdf')],check=True,env=dict(os.environ,XDG_CACHE_HOME=str(D/'cache'),XDG_CONFIG_HOME=str(D/'config')))
