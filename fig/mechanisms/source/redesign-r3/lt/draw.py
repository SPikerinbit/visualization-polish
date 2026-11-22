#!/usr/bin/env python3
from pathlib import Path
from xml.etree import ElementTree as E
import hashlib,json,math
D=Path(__file__).resolve().parent
S=json.loads((D/'states.json').read_text())
assert hashlib.sha256((D/'lt-baseline.pdf').read_bytes()).hexdigest()==S['baseline_sha256']
W,H=240.24655,102.4
N='http://www.w3.org/2000/svg'
E.register_namespace('',N)
C={
  'ink':'#203347','muted':'#526275','panel':'#F1F5F8','rule':'#CBD5E0','far':'#AAB8C6',
  'warm':'#FFF2CC','gold':'#A56909','lightwarm':'#FFFAEB',
  'blue':'#DEEBF7','slate':'#426884','lightblue':'#F0F6FB',
  'green':'#E2F0D9','pine':'#426D37','lightgreen':'#F0F6EC',
  'white':'#FFFFFF','neutral':'#6B7886'
}
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
g=el(root,'g',font_family='TeX Gyre Termes, Liberation Serif, serif',fill=get('ink'))
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
styles={'win':('green','pine'),'stored':('blue','slate'),'new':('warm','gold'),
        'unread':('white','neutral')}
def chip(g,x,y,v,role,r=3.55,show=True,**attrs):
 f,c=styles[role]
 q=el(g,'g',data_value=v,data_role=role,**attrs)
 el(q,'circle',cx=round(x,4),cy=round(y,4),r=r,fill=get(f),stroke=get(c),
   stroke_width=.53 if role in ('win','new') else .43,
   stroke_dasharray='.8 .52' if role=='unread' else None)
 if show:t(q,x,y+1.82,str(v),5.5)
 return q
def chips(g,x,y,values,role,step=7.58,**k):
 for j,v in enumerate(values):
    chip(g,x+(j-(len(values)-1)/2)*step,y,v,role(v) if callable(role) else role,**k)
 if not values:t(g,x,y+1.8,'∅',5.5,'muted')
def tree(x,name,state,before):
    w=70.5; cx=x+w/2
    T=el(g,'g',id=name)
    rect(T,x,1.4,w,10.6,'panel',r=2.0)
    t(T,cx,8.58,'Before refresh' if before else 'After refresh',7.15,bold=True)
    output_name='Just emitted' if before else 'Next winner'
    box_color='lightgreen'
    rect(T,x+5.0,16.05,w-10,12.7,box_color,r=2.4)
    t(T,x+24.5,24.40,output_name,5.95,'pine',bold=True)
    chips(T,x+54.2,22.55,state['emitted' if before else 'next_winner'],'win',
          data_location='root-output')
    pos={'root':(cx,43.8),'left':(x+17.7,61.85),'right':(x+52.8,61.85),
         'R1':(x+8.95,80.3),'R2':(x+26.5,80.3),'R3':(x+43.95,80.3),'R4':(x+61.5,80.3)}
    # The rear neutral edge is drawn from parent to child. Only actual
    # embedded pointer arrows receive a head; the selected old path is bold.
    for start,children in [('root',('left','right')),('left',('R1','R2')),('right',('R3','R4'))]:
       u,v=pos[start]
       for target in children:
          y,z=pos[target];dy=z-v;dx=y-u
          x1,y1=(u+dx*.22,v+dy*.22);x2,y2=(y-dx*.22,z-dy*.22)
          if state['pointers'][start]==target:
             active=before and (start,target) in [('root','left'),('left','R2')]
             arr(T,x1,y1,x2,y2,'gold' if active else 'muted',1.05 if active else .61,
                  3.0 if active else 2.35,data_pointer=f'{start}:{target}')
          else:ln(T,x1,y1,x2,y2,'far',.38)
    # The output arrow is not a child pointer. It points outward.
    arr(T,cx,38.8,cx,29.9,'pine',.65,2.35,data_link='emission')
    for node in ('root','left','right'):
       xx,yy=pos[node]
       chips(T,xx,yy,state[node],'stored',data_location=node)
    for ind,data in enumerate(state['leaves'],1):
       q=f'R{ind}'; xx,yy=pos[q]
       leaf=el(T,'g',data_leaf=q)
       if before and ind==2:rect(leaf,xx-8.2,yy-5.1,16.4,13.9,'lightwarm',r=1.8)
       chips(leaf,xx,yy,data,'unread',data_location=q)
       t(leaf,xx,88.1,q,5.42,'gold' if before and ind==2 else 'muted',bold=True)
    t(T,cx,94.45,'Follow the gold pointers' if before else 'Right subtree unchanged',
      size=5.3,col='gold' if before else 'muted',bold=before)
    return T
tree(1.5,'before',S['before'],True)
tree(168.25,'after',S['after'],False)
M=el(g,'g',id='path-refresh')
cx=120.125
rect(M,75.4,1.4,89.45,10.6,'ink',r=2.0)
t(M,cx,8.58,'Refresh only one path',7.15,'white',bold=True)
rect(M,75.4,14,89.45,23.2,'lightwarm',r=2.4)
t(M,cx,20.15,'1  Gather path segments',6.35,'gold',bold=True)
for x,vals,label,role in zip((90.7,120.125,149.55),S['refresh']['rank_input_groups'],
    ('Root losers','Left losers','New from R2'),('stored','stored','new')):
 t(M,x,26.15,label,5.18,'gold' if role=='new' else 'muted',bold=(role=='new'))
 chips(M,x,31.75,vals,role,data_location='gather')
# DAG flows downward in execution order; arrowheads are kept outside boxes.
arr(M,cx,37.35,cx,40.25,'gold',.55,1.7)
rect(M,75.4,40.5,89.45,18.25,'lightblue',stroke='slate',r=2.4,sw=.5,stroke_dasharray='1.45 .9')
t(M,cx,46.80,'2  One rank call',6.35,'slate',bold=True)
t(M,90.6,54.6,'ρ',6.3,'slate')
rr=S['refresh']['rank_map_order']
chips(M,123.1,52.7,rr,lambda v:'new' if v in (6,14) else 'stored',
      step=8.11,data_location='rank')
arr(M,cx,58.90,cx,61.78,'slate',.55,1.7)
rect(M,75.4,62.1,89.45,29.2,'lightgreen',r=2.4)
t(M,cx,68.35,'3  Replay bottom-up',6.35,'pine',bold=True)
t(M,122.3,74.3,'Forward',5.06,'pine',bold=True)
t(M,148.6,74.3,'Keep losers',5.06,'slate',bold=True)
for y,k,title in ((79.25,'left','Left match'),(87.15,'root','Root match')):
 t(M,79.9,y+1.85,title,5.55,'ink',align='start',bold=(k=='root'))
 for key,x,role in (('winner',122.3,'win'),('retained',148.6,'stored')):
    v=S['refresh'][k][key]
    chips(M,x,y,v,role,step=7.25,r=3.24,data_location=f'{k}-{key}')
# One clean legend at the physical column width.
ln(g,3.2,95.95,W-3.3,95.95,'rule',.32)
L=el(g,'g',id='legend')
for x,role,word in [(5.8,'new','New read'),( 43.4,'stored','Stored'),(77.65,'unread','Unread'),(112.35,'win','Winner')]:
 chip(L,x,98.50,'',role,r=2.2,show=False)
 t(L,x+4.0,100.40,word,5.53,align='start')
for x,c,word in [(148.0,'muted','Pointer'),(191.8,'gold','Refresh path')]:
 arr(L,x,98.55,x+8.0,98.55,c,.67 if c=='muted' else .9,2.4)
 t(L,x+10.15,100.40,word,5.53,align='start')
E.ElementTree(root).write(D/'lt-bold-r3.svg',encoding='utf-8',xml_declaration=True)
