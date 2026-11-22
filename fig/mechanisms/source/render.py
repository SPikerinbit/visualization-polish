from pathlib import Path
from html import escape
R=Path(__file__).resolve().parent
W,H=1600,470
ink='#253246';edge='#526276'; light='#D6DCE5'; g='#548235'; a='#9B6B16'; b='#2E659A'
green='#E2F0D9'; amber='#FFF2CC'; blue='#DEEBF7'
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="178mm" height="{178*H/W}mm" viewBox="0 0 {W} {H}">', '<title>Cost-guided semantic merge planning and execution</title><defs>']
for key,c in [('gray',edge),('gold',a),('blue',b),('green',g)]:
 s.append(f'<marker id="{key}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="{c}"/></marker>')
s+=['</defs>','<rect width="1600" height="470" fill="white"/>','<g font-family="TeX Gyre Termes,serif">']
def rect(x,y,w,h,f='white',c='none',r=9,sw=2):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f}" stroke="{c}" stroke-width="{sw}"/>')
def path(d,c=edge,sw=2,arr=None,dash=False):s.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#{arr})"' if arr else '')+(' stroke-dasharray="6 5"' if dash else '')+'/>')
def text(x,y,v,sz=21,c=ink,w='normal',align='start',style='normal'):s.append(f'<text x="{x}" y="{y}" fill="{c}" font-size="{sz}" font-style="{style}" font-weight="{w}" text-anchor="{align}">{escape(v)}</text>')
def stage(x,w,num,title,fill,c,bdy):
 rect(x,13,w,440,bdy,r=14);rect(x,13,w,45,fill,r=12)
 rect(x+13,23,25,25,c,r=12.5);text(x+25.5,41,num,17,'white','bold','middle')
 text(x+47,42,title,25,ink,'bold')
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
 rect(x,78,158,63,'white','#C3D2C5',7)
 document(x+9,87,c);text(x+54,115,lab,21,ink,'bold')
path('M112 143 V155 H203 M296 143 V155 H203 V168',g,1.9,'green')
for y,head,sub in [(174,'Run lengths','Items per sorted run'),(232,'Capacity m','Max items per listwise call'),(290,'Requested output','Full Ranking or LIMIT K'),(348,'Token profile','System prompt H + document L')]:
 rect(31,y,345,51,'white','#C4D6C2',7,1.8);text(44,y+22,head,20,ink,'bold');text(44,y+41,sub,17.5,edge)
 if y==174:
  for j in range(3): tokens(304,y+8+j*11,[g,green,green],12,7,3)
 if y==232: tokens(304,y+19,['#A9D18E','#A9D18E',green,green],12,10,3)
 if y==290: rect(322,y+15,37,23,amber,'#C7A149',5);text(340,y+33,'K',17,a,'bold','middle')
 if y==348: tokens(310,y+17,['#A7BACF','#AAC899','#AAC899'],12,14,3)
for y in [198,257,315,373]: path(f'M377 {y} H388',g,1.65)
path('M388 198 V373',g,1.65)
path('M388 257 H437',edge,3,'gray')

# Cost logic stays explicit; pipeline normalizing type and hierarchy.
for x,w,t1 in [(452,175,'Valid plans'),(648,186,'Estimate tokens'),(854,183,'Select minimum')]:
 rect(x,85,w,134,'white','#DFC78E',7,1.8)
 rect(x+1,86,w-2,30,'#FFF3D3',r=6)
 text(x+w/2,108,t1,20,ink,'bold','middle')
path('M630 152 H643',a,2.5,'gold');path('M837 152 H849',a,2.5,'gold')
text(539,143,'SW or LT',19,ink,'bold','middle');text(539,170,'(k, h)',20,a,'bold','middle');text(539,199,'b(k)h ≤ m',20,ink,'normal','middle')
text(741,145,'H × calls',20,ink,'bold','middle');text(741,169,'+',21,a,'bold','middle');text(741,195,'L × item appearances',18.5,ink,'bold','middle')
for j,col in enumerate(['#D8DEE5','#C89533','#AEBCC9']):
 text(871,141+j*17,'ABC'[j],13,a if j==1 else edge,'bold')
 rect(888,132+j*17,[63,49,82][j],8,col,r=2)
text(945,201,'arg min cost',19,ink,'bold','middle')
path('M946 223 V244 H745 V253',a,2.6,'gold')
for x,y,c,role,sub in [(454,269,edge,'A   SW','k=5, h=2'),(657,260,a,'B   LT','k=4, h=2'),(858,269,edge,'C   LT','k=4, h=4')]:
 active=c==a
 rect(x,y,179 if not active else 181,123 if not active else 141,amber if active else 'white',a if active else '#D2D7D9',9,2.8 if active else 1.5)
 text(x+13,y+24,role,20,c,'bold');text(x+13,y+45,sub,18,ink)
 if active:
  rect(x+102,y+9,69,22,'#E6B657',r=7);text(x+136.5,y+25,'EXAMPLE',12.5,ink,'bold','middle')
 mini_tree(x+91,y+62,c,.99 if active else .89,5 if x==454 else 4,4 if x==858 else 2)
text(1038,385,'…',21,edge)
# Route picked config to execution without crossing candidate labels.
path('M1038 152 H1069 V220 H1106',a,2.7,'gold')

# Split outcomes, each with unambiguous flow and encoded group activity.
path('M1110 220 V148 H1128',b,2.8,'blue');path('M1110 220 V326 H1128',b,2.8,'blue')
for y,h,title,sub in [(76,132,'Full Ranking','Materialize layer by layer'),(233,195,'LIMIT K','Pull on demand across layers')]:
 rect(1133,y,436,h,'white','#B9D0E4',8,1.8)
 rect(1134,y+1,434,34,blue,r=7);text(1145,y+25,title,21,ink,'bold');text(1554,y+24,sub,16.8,b,'normal','end');text(1295,y+25,'P(Full)' if y==76 else 'P(K)',16,b,'bold')
def group(x,y,mode,active=True):
 col=blue if mode=='blue'else amber; st=b if mode=='blue'else a
 rect(x,y,57,22,col if active else 'white',st if active else '#CDD8DF',6,1.8 if active else 1.3)
 if active:tokens(x+8,y+7,[st,st,st],8,8,4)
# Transfers occur across one whole-layer barrier, never per group.
rect(1237,118,213,27,'#F1F7FC','#C5D7E9',6,1.4)
for xx in [1244,1315,1386]:group(xx,121,'blue')
text(1150,138,'Layer i',18,edge);text(1150,183,'Layer i+1',18,edge)
path('M1240 150 H1448','#7FA0BB',1.35)
shape='M1334 145 H1351 V151 H1359 L1342.5 163 L1326 151 H1334 Z'
s.append(f'<path d="{shape}" fill="{b}" stroke="white" stroke-width="1.4" stroke-linejoin="round"/>')
text(1456,154,'all groups ready',15.5,b)
for xx in [1244,1315,1386]:group(xx,163,'blue')
path('M1447 174 H1464',b,2,'blue');text(1471,179,'All results',18,b,'bold')
text(1150,297,'Layer i',18,edge);text(1150,353,'Layer i+1',18,edge)
for xx in [1244,1315,1386]:group(xx,280,'gold',xx==1315);group(xx,337,'gold',xx==1315)
path('M1331 304 V334',b,2.3,'blue');path('M1356 334 V304',a,2.3,'gold',True)
text(1325,323,'Push',16,b,'normal','end');text(1363,323,'Pull',16,a)
path('M1343 362 V381 H1461',b,2.1,'blue')
rect(1467,369,85,28,amber,'#D8AD57',5);text(1510,389,'First K',18,a,'bold','middle')
text(1552,416,'Stop at K or EOF',16.5,edge,'normal','end')
s.append('</g></svg>')
(R/'framework-structural-demand.svg').write_text('\n'.join(s))
