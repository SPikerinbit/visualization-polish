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
s.set('height','93.5pt');s.set('viewBox','0 0 240.24655 93.5');s.find(q('rect')).set('height','93.5')
main=s.find(q('g'));main.set('font-family','Liberation Serif, serif')
ink='#292722'; gray='#515750'; muted='#57635C'; pale='#A8ADA5'
sep='#DAD8CB'; warm='#8B4E08'; amber='#FFE3AF'; teal='#285F4D'; sea='#E1EDE5'
shift={ '#252B2E':ink, '#28343C':ink, '#AC6D0B':warm, '#FFE3AE':amber, '#DDEBDD':sea, '#4F6B56':teal,'#425E4D':teal,'#69757C':muted,'#606E74':muted,'#8C989E':'#79837A','#B8C2C5':pale}
for a in s.iter():
    for k in ('fill','stroke'):
        if a.get(k) in shift:a.set(k,shift[a.get(k)])
before=group('read-path');after=group('after')
before.set('transform','translate(-3 6)');after.set('transform','translate(3 6)')
for g,h in [(before,'(a) Follow pointers'),(after,'(c) Replay bottom-up')]:
    t=g.find(q('text'));t.set('y','3.0');t.set('font-size','7.2');t.text=h
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
text(before,64,34.95,'Stored',6.0,gray,False,'start')
text(after,198,34.95,'Stored',6.0,gray,False,'start')
# Compact replay labels remain tied to the nodes (not arrow or pointer labels).
for a in list(after):
    if a.tag==q('text') and a.text in ('(1)','(2)'):a.set('font-size','5.9')
# Change the two next-pointer arrows and add a separate key; R3's inherited pointer is muted.
for a in list(after):
    if a.tag in [q('line'),q('polygon')] and a.get('stroke',a.get('fill'))==muted:
        a.set('stroke' if a.tag==q('line') else 'fill',ink)
        if a.tag==q('line'):a.set('stroke-width','.78')
# Rewrite the center card; inputs are three intact pairs, output is one order.
g=group('one-listwise-call');g.clear();g.set('id','one-listwise-call')
text(g,120.1233,9,'(b) Rank six rows',7.2,ink,True)
text(g,120.1233,17.5,'One rank call',6.05,gray)
node(g,'rect',x=94.1,y=22.6,width=52.05,height=30.6,rx=1.4,fill='#FBF9F3',stroke='#C7AE86',stroke_width='.65')
text(g,120.1233,29.95,'Stored on path',6.05,gray)
text(g,120.1233,36.7,'[3, 4] + [5, 7]',6.5,ink,True)
text(g,120.1233,44.7,'New from R₂',6.0,warm)
text(g,120.1233,50.8,'[6, 14]',6.5,warm,True)
node(g,'path',d='M120.123 54.4 V56.75 m-1.2 -1.3 1.2 1.3 1.2 -1.3',stroke=gray,stroke_width='.58',fill='none',stroke_linecap='round')
t=text(g,120.1233,62.3,'3 ≺ 4 ≺ 5 ≺ ',5.85)
a=node(t,'tspan','6',fill=warm,font_weight='bold');a.tail=' ≺ 7 ≺ ';node(t,'tspan','14',fill=warm,font_weight='bold')
main.remove(group('bottom-up-order'))
g=group('legend');g.clear();g.set('id','legend')
node(g,'path',d='M1 82 H239',stroke=sep,stroke_width='.56')
for x,c,f,t in [(4,warm,amber,'New from R₂'),(51,ink,'white','Stored'),(82,'#79837A','white','Unread')]:
    a=node(g,'circle',cx=x,cy=88.1,r=2.3,stroke=c,stroke_width='.61',fill=f)
    if t=='Unread':a.set('stroke-dasharray','1.25 .8')
    if x==4:node(g,'path',d='M2.9 89.2 h2.2',stroke=warm,stroke_width='.45')
    text(g,x+4.45,90.4,t,6.15,ink,False,'start')
for x,c,t in [(114,warm,'Follow pointer'),(161,ink,'Next pointer'),(202,teal,'Replay')]:
    node(g,'path',d=f'M{x} 88.25 h5.5',stroke=c,stroke_width=1 if c==warm else .8)
    node(g,'path',d=f'M{x+6.5} 88.25 l-2.4 -1.25 v2.5 z',fill=c)
    text(g,x+8.28,90.4,t,6.15,ink,False,'start')
s.find(q('desc')).text='The full tree is shown twice. After prior output [1,2], the amber pointers reach R2. One rank call orders [3,4], [5,7], and [6,14]. In replay (1), [5,6] travels up while [7,14] is stored. In (2), [3,4] is next output and [5,6] is stored. The next pointers go right at the root and left at the lower match; R2 is exhausted.'
tree.write(str(D/'lt.svg'),xml_declaration=True,encoding='utf-8')
subprocess.run(['inkscape',str(D/'lt.svg'),'--export-filename='+str(D/'lt.pdf')],check=True,env=dict(os.environ,XDG_CACHE_HOME=str(D/'cache'),XDG_CONFIG_HOME=str(D/'config')))
