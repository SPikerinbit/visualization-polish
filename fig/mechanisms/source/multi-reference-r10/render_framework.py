from pathlib import Path
import os, sys
from html import escape
from subprocess import run
R=Path(sys.argv[1]).resolve()
R.mkdir(parents=True,exist_ok=True)
SHADOW='--shadow' in sys.argv
W,H=1600,470
ink='#253246';edge='#526276'; light='#D6DCE5'; g='#548235'; a='#9B6B16'; b='#2E659A'
green='#E2F0D9'; amber='#FFF2CC'; blue='#DEEBF7'
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="178mm" height="{178*H/W}mm" viewBox="0 0 {W} {H}">', '<title>Cost-guided semantic merge planning and execution</title><defs>']
for key,c in [('gray',edge),('gold',a),('blue',b),('green',g)]:
 s.append(f'<marker id="{key}" viewBox="0 0 10 10" refX="9.4" refY="5" markerWidth="3.8" markerHeight="3.8" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="{c}"/></marker>')
s+=['</defs>','<rect width="1600" height="470" fill="white"/>','<g font-family="TeX Gyre Termes,serif">']
def rect(x,y,w,h,f='white',c='none',r=9,sw=2):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f}" stroke="{c}" stroke-width="{sw}"/>')
def path(d,c=edge,sw=2,arr=None,dash=False):s.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#{arr})"' if arr else '')+(' stroke-dasharray="6 5"' if dash else '')+'/>')
def text(x,y,v,sz=21,c=ink,w='normal',align='start',style='normal'):s.append(f'<text x="{x}" y="{y}" fill="{c}" font-size="{sz}" font-style="{style}" font-weight="{w}" text-anchor="{align}">{escape(v)}</text>')
def stage(x,w,num,title,fill,c,bdy):
 # Typographic stages, defined by shared axes, not card backgrounds.
 path(f'M{x+12} 57 H{x+w-7}', '#D4DBDF',1.35)
 path(f'M{x+12} 57 H{x+51}',c,3.3)
 text(x+17,40,num,18,c,'bold','middle')
 text(x+38,40,title,25,ink,'bold')
def tokens(x,y,colors,sw=13,hh=12,gap=4):
 for i,col in enumerate(colors): rect(x+i*(sw+gap),y,sw,hh,col,'none',2)
def document(x,y,c):
 for dx,dy in [(0,6),(4,2)]:rect(x+dx,y+dy,35,39,'white',c,3,1.65)
 for yy in [12,18,24]:path(f'M{x+11} {y+yy}h19',c,1.4)
def mini_tree(x,y,accent,scale=1,n=3,h=2):
 slots=[(j-(n-1)/2)*17 for j in range(n)]
 for dx in slots:
  path(f'M{x} {y+7} L{x+dx*scale} {y+25*scale}',accent,1.6)
 for dx in slots:
  rect(x+(dx-7)*scale,y+25*scale,14*scale,11*scale,'white',accent,2,1.5)
  for j in range(1,h):
   px=x+(dx-7+j*14/h)*scale
   path(f'M{px} {y+27*scale} v{7*scale}',accent,.82)
 rect(x-7*scale,y,14*scale,10*scale,'white',accent,2,1.5)
stage(10,390,'1','Prepare planning inputs',green,g,'#F6FAF4')
stage(428,637,'2','Choose a cost-effective plan',amber,a,'#FFFBF1')
stage(1091,499,'3','Execute the selected plan',blue,b,'#F5F9FC')

# Inputs, paired extraction and compact profile.
for x,lab,c in [(33,'Documents',g),(217,'NL Query',b)]:
 document(x+9,87,c);text(x+54,115,lab,21,ink,'bold')
path('M112 143 V152 H296 V143 M203 152 V162',g,1.9,'green')
s.append(f'<circle cx="203" cy="152" r="2.35" fill="{g}"/>')
text(203,178,'Initial sorted runs',17.5,g,'bold','middle')
for y,head,sub in [(174,'Run lengths','Items per sorted run'),(232,'Capacity m','Max items per listwise call'),(290,'Requested output','Full Ranking or LIMIT K'),(348,'Token profile','System prompt H + document L')]:
 if y>174: path(f'M43 {y-2} H367','#D6E3D4',1.15)
 text(44,y+22,head,20,ink,'bold');text(44,y+41,sub,17.5,edge)
 if y==174:
  for j in range(3): tokens(304,y+8+j*11,[g,green,green],12,7,3)
 if y==232: tokens(304,y+19,['#A9D18E','#A9D18E',green,green],12,10,3)
 if y==348: tokens(310,y+17,['#A7BACF','#AAC899','#AAC899'],12,14,3)
for y in [198,257,315,373]: path(f'M377 {y} H388',g,1.65)
path('M388 198 V373',g,1.65)
path('M388 257 H407 V170 H444',edge,2.8,'gray')

# Cost logic stays explicit; pipeline normalizing type and hierarchy.
for x,w,t1 in [(452,175,'Valid plans'),(648,186,'Estimate tokens'),(854,183,'Select plan')]:
 path(f'M{x+13} 117 H{x+w-13}','#DFC78E',1.3)
 text(x+w/2,108,t1,20,ink,'bold','middle')
path('M630 152 H643',a,2.5,'gold');path('M837 152 H849',a,2.5,'gold')
text(539,143,'SW or LT',19,ink,'bold','middle');text(539,170,'(k, h)',20,a,'bold','middle');text(539,199,'b(k)h ≤ m',20,ink,'normal','middle')
text(741,145,'H × calls',20,ink,'bold','middle');text(741,169,'+',21,a,'bold','middle');text(741,195,'L × item appearances',18.5,ink,'bold','middle')
if SHADOW:
 # A single small crisp offset: focus only the operation that picks the
 # per-request plan. No samples, leaf nodes, or execution states get shadows.
 rect(872,145,171,55,'#DFE5EA',r=4)
 rect(869,141,171,55,'#F6FAFD','#A3B8C8',r=4,sw=1.55)
text(954.5,166,'Minimum cost',19,ink,'bold','middle')
text(954.5,186,'for this request',17,edge,'normal','middle')
path('M458 264 H1040','#E1E6E9',1.45)
text(458,253,'Candidate examples',18,edge,'bold')
for x,c,role,sub,n,h in [(456,edge,'A  SW','k=5, h=2',5,2),(661,edge,'B  LT','k=4, h=2',4,2),(861,edge,'C  LT','k=4, h=4',4,4)]:
 text(x+5,294,role,20,ink,'bold')
 text(x+5,320,sub,18,edge)
 if role.endswith('SW'):
  # Five runs, two initial entries in the shared listwise window.
  rect(x+57,337,65,22,'#FFF5DF','#AE833E',2,1.4)
  for j in range(n):
   for k in range(3):
    rect(x+61+j*12,341+k*8,10,6,'#E8C884' if k<2 else 'white',edge,1.1,1)
 else:
  mini_tree(x+89,340,c,1.07,n,h)
text(1032,380,'…',21,edge)
# Start at the plan decision, not the example. A junction owns the two
# request modes, avoiding arrowheads pointing to other arrows.
path('M954.5 199 V220 H1111',edge,2.65)
path('M1111 92 V252',b,2.65)
path('M1111 92 H1135',b,2.65,'blue')
path('M1111 252 H1135',b,2.65,'blue')
s.append(f'<circle cx="1111" cy="220" r="3.7" fill="{b}"/>')
path('M1137 225 H1562','#AEC7DB',1.45)
for y,title,plan,xplan,action in [
 (100,'Full Ranking','P(Full)',1304,'Materialize each layer'),
 (260,'LIMIT K','P(K)',1263,'Pull across layers')]:
 text(1144,y,title,25,ink,'bold')
 text(xplan,y,plan,18,b,'bold')
 text(1560,y,action,19,b,'normal','end')
def group(x,y,kind):
 active=kind!='idle'
 st=b if kind=='full' else a
 if active:
  rect(x,y,56,23,blue if kind=='full' else amber,
       '#8AA9C4' if kind=='full' else a,3,1.4 if kind=='full' else 2)
  tokens(x+9,y+7,[st]*3,9,9,6)
 else:
  # Idle peers still have a readable silhouette when printed in grayscale.
  rect(x,y,56,23,'none','#B7C8D4',3,1)
  tokens(x+9,y+7,['#DBE4EA']*3,9,9,6)
xs=[1235,1313,1391]
for xx in xs:
 group(xx,114,'full'); group(xx,176,'full')
 # All three merge groups join one common materialization barrier.
 path(f'M{xx+28} 138 V146',b,1.85)
text(1146,132,'Layer i',20,edge);text(1146,195,'Layer i+1',20,edge)
path('M1263 146 H1419',b,2.65)
# A second rail groups the lower layer. The broad arrow crosses one
# collective barrier; the rail isn't an all-to-all record edge.
path('M1263 175 V170 H1419 V175','#8AA9C4',1.55)
path('M1341 170 V175','#8AA9C4',1.55)
s.append(f'<path d="M1334 146 H1348 V155 H1356 L1341 169 L1326 155 H1334 Z" fill="{b}"/>')
text(1367,163,'layer barrier',17,b,'bold')
for xx in xs: path(f'M{xx+28} 200 V208','#8AA9C4',1.6)
path('M1263 208 H1419',b,1.6)
text(1430,213,'…',15,b)
path('M1449 208 H1467',b,1.85,'blue')
text(1474,215,'All rows',20,b,'bold')
text(1146,305,'Layer i',20,edge);text(1146,379,'Layer i+1',20,edge)
for j,xx in enumerate(xs):
 mode='demand' if j==1 else 'idle';group(xx,287,mode);group(xx,361,mode)
path('M1328 313 V357',b,2.55,'blue')
path('M1355 357 V313',a,2.55,'gold',True)
text(1319,342,'Push',19,b,'bold','end');text(1364,342,'Pull',19,a,'bold')
# Route the prefix beneath the idle peer so that it cannot imply an extra merge.
path('M1341 385 V405 H1467',b,1.9,'blue')
rect(1473,390,80,29,amber,'#C89B46',5,1.45)
text(1513,411,'First K',20,a,'bold','middle')
text(1554,440,'Stop at K or EOF',18,edge,'normal','end')
s.append('</g></svg>')
svg=R/'framework.svg'
svg.write_text('\n'.join(s))
run(['inkscape',str(svg),'--export-type=pdf','--export-filename='+str(R/'framework.pdf')],env={**os.environ,'SOURCE_DATE_EPOCH':'0'},check=True)
run(['pdftocairo','-png','-singlefile','-r','200',str(R/'framework.pdf'),str(R/'framework')],check=True)
