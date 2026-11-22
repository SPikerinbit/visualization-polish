#!/usr/bin/env python3
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib,json,math
D=Path(__file__).resolve().parent
S=json.loads((D/'states.json').read_text())
assert hashlib.sha256((D/'baseline.pdf').read_bytes()).hexdigest()==S['baseline_sha256']
W,H=240.24655,79.5
N='http://www.w3.org/2000/svg'
E.register_namespace('',N)
C={'ink':'#252B2E','muted':'#69757C','structure':'#B8C2C5','quiet':'#8C989E','rule':'#C9D0D2','gold':'#AC6D0B','goldfill':'#FFE3AE','win':'#4F6B56','winfill':'#DDEBDD','white':'#FFFFFF'}
def el(p,tag,**attrs):
 return E.SubElement(p,'{'+N+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items() if v is not None})
root=E.Element('{'+N+'}svg',{'width':f'{W}pt','height':f'{H}pt','viewBox':f'0 0 {W} {H}'})
el(root,'title').text='Segmented loser tree: refresh one path'
el(root,'desc').text='The pre-refresh tree points from the root to its left child and then to R2. One call ranks the two stored path segments and the new segment. Replay first the lower match, then the root. The other subtree is unchanged.'
def get(x):return C.get(x,x)
def rect(g,x,y,w,h,f,stroke=None,r=0,sw=.4,**k):
 return el(g,'rect',x=x,y=y,width=w,height=h,rx=r,fill=get(f),
      stroke=get(stroke),stroke_width=sw if stroke else None,**k)
rect(root,0,0,W,H,'white')
g=el(root,'g',font_family='Nimbus Roman, Liberation Serif, serif',fill=get('ink'))
def t(g,x,y,word,size=5.55,col='ink',align='middle',bold=False):
    q=el(g,'text',x=round(x,4),y=round(y,4),font_size=size,text_anchor=align,
       fill=get(col),font_weight='bold' if bold else None)
    q.text=word
    return q
def ln(g,x,y,u,v,c,sw=.4,**k):
 return el(g,'line',x1=round(x,4),y1=round(y,4),x2=round(u,4),y2=round(v,4),
          stroke=get(c),stroke_width=sw,stroke_linecap='round',**k)
def poly(g,points,c):
 return el(g,'polygon',points=' '.join(f'{x:.4f},{y:.4f}' for x,y in points),fill=get(c))
def arr(g,x,y,u,v,c,sw=.7,head=2.65,**k):
 dx,dy=u-x,v-y;nn=math.hypot(dx,dy);dx/=nn;dy/=nn
 ln(g,x,y,u-.82*head*dx,v-.82*head*dy,c,sw,**k)
 ex,ey=u-head*dx,v-head*dy
 poly(g,[(u,v),(ex-head*.44*dy,ey+head*.44*dx),
                (ex+head*.44*dy,ey-head*.44*dx)],c)
STYLE={'stored':('white','ink'),'new':('goldfill','gold'),'unread':('white','quiet'),
       'winner':('winfill','win'),'active':('white','gold'),'quiet':('white','quiet')}
def coin(g,x,y,num,role,r=3.70):
 fill,ink=STYLE[role]
 el(g,'circle',cx=x,cy=y,r=r,fill=get(fill),stroke=get(ink),
    stroke_width=.52,stroke_dasharray='1.15 .8' if role=='unread' else None)
 if num is not None: t(g,x,y+1.77,str(num),5.5,
                         'quiet' if role=='quiet' else 'ink')
def pair(g,x,y,vals,role):
 for i,num in enumerate(vals):coin(g,x+(i-.5)*8.5,y,num,role)
 if not vals:t(g,x,y+1.65,'∅',6.0,'muted')
def tree(cx,before):
 state=S['before' if before else 'after']
 T=el(g,'g',id='read-path' if before else 'after')
 t(T,cx,7.2,'(a) Before replay' if before else '(b) After replay',7.05,bold=True)
 pos={'root':(cx,33),'left':(cx-22.5,46.9),'right':(cx+22.5,46.9),
      'R1':(cx-35,62.2),'R2':(cx-10,62.2),'R3':(cx+10,62.2),'R4':(cx+35,62.2)}
 for parent,dests in [('root',('left','right')),('left',('R1','R2')),('right',('R3','R4'))]:
  for dest in dests:
   x,y=pos[parent];X,Y=pos[dest]
   xp=x+(X-x)*.28;yp=y+4.0
   xq=X-(X-x)*.29;yq=Y-4.15
   selected=(state['pointers'][parent]==dest)
   active=before and selected and parent in ('root','left')
   color='gold' if active else ('quiet' if parent=='right' else 'muted')
   if selected: arr(T,xp,yp,xq,yq,color,1.2 if active else .64,2.9 if active else 2.3)
   else: ln(T,xp,yp,xq,yq,'structure',.44)
 pair(T,cx,17.1,state['emitted' if before else 'next_winner'],'winner')
 arr(T,cx,28.7,cx,21.85,'win',.6,2.35)
 for node in ['root','left','right']:
  x,y=pos[node]
  pair(T,x,y,state[node],('quiet' if node=='right' else ('active' if before else 'stored')))
 for k,nums in enumerate(state['leaves'],1):
  x,y=pos[f'R{k}']
  hot=before and k==2
  pair(T,x,y,nums,'new' if hot else 'unread')
  t(T,x,70.55,'R'+str(k),5.6,'gold' if hot else 'muted',bold=hot)
tree(53,True)
tree(W-53,False)
cx=W/2
t(g,cx,34.4,'Rank once',6.7,bold=True)
arr(g,cx-14.7,39.7,cx+14.7,39.7,'ink',.85,3.0)
t(g,cx,47.6,'Replay bottom-up',5.45,'muted')
L=el(g,'g',id='legend')
for x,key,name in [(9,'new','New read'),(56,'stored','Stored'),(98,'unread','Unread'),(139,'winner','Output')]:
 coin(L,x,76.6,None,key,r=2.1)
 t(L,x+3.9,78.4,name,5.45,align='start')
arr(L,180,76.6,189,76.6,'gold',1.03,2.75)
t(L,192,78.4,'Refresh path',5.45,align='start')
E.ElementTree(root).write(D/'lt-path.svg',encoding='utf-8',xml_declaration=True)
