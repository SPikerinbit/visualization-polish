from pathlib import Path
from html import escape
D=Path(__file__).resolve().parents[1];a=[]
W,H=1600,474
ink='#262626';gray='#666666';gold='#E07B00';pale='#FFE5A3';sage='#DDEBDD';green='#52775C';blue='#E5EDF3';steel='#647E91'
a.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="178mm" height="{178*H/W}mm" viewBox="0 0 {W} {H}"><title>Cost-guided semantic merge execution</title><desc>Abstract sorted runs inform a cost model. Feasible merge structures are evaluated for the requested mode, and the selected parameters configure either full materialization or demand-driven LIMIT execution. Solid arrows carry results downstream. Dashed reverse arrows request data upstream; no further requests after K outputs.</desc><defs>')
for name,c in [('steel',steel),('gray',gray),('pull',gold),('green',green)]:a.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="{c}"/></marker>')
a.append('</defs><rect width="1600" height="474" fill="white"/><g font-family="Liberation Serif,Times New Roman,serif" fill="#262626">')
def text(x,y,s,size=24,anchor='middle',weight='normal',color=ink):a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>')
def rect(x,y,w,h,fill='white',stroke='#BBBBBB',rx=5,sw=1.6):a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def path(d,color=gray,dash=False,arrow=True,sw=1.8):a.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'+(' stroke-dasharray="5 4"' if dash else '')+(f' marker-end="url(#{"pull" if color==gold else "green" if color==green else "steel" if color==steel else "gray"})"' if arrow else '')+'/>')
def run(x,y,w=69,filled=True,color=sage):
 rect(x,y,w,16,color if filled else 'white','#A8B5AA',3)
 for i in range(1,5):path(f'M{x+i*w/5} {y+2} V{y+14}',color='#A8B5AA',arrow=False,sw=1)
def merge(x,y,active=True):rect(x-14,y-12,28,24,pale if active else 'white',gold if active else '#BBBBBB',4)
# Four stages use the same element palette; requests/configuration are not document-derived.
for x,s,end,c in [(12,'Inputs for planning',420,green),(470,'Cost-effective plan',1135,steel),(1175,'Execute the selected plan',1590,gold)]:
 text(x,28,s,27,'start','bold');path(f'M{x} 40 H{end}',color=c,arrow=False,sw=3)
for x in [447,1145]:path(f'M{x} 50 V{H-40}',color='#DDDDDD',arrow=False,sw=1)
# Document and request sources are distinct from derived sizes and configuration.
for x,y in [(18,99),(24,93),(30,87)]:rect(x,y,54,64,'white',green,3)
for y in [102,116,130]:path(f'M38 {y} H74',color=green,arrow=False)
text(57,180,'Documents',23)
# Natural-language query is an entity, distinct from runtime configuration.
a.append('<g transform="translate(0,60)">')
for xx,yy in [(19,226),(25,220),(31,214)]:rect(xx,yy,54,61,'white',gold,3)
rect(31,214,54,14,pale,gold,3,1)
for yy,ww in [(237,35),(248,28),(259,33)]:path(f'M39 {yy} H{39+ww}',gold,arrow=False)
text(62,313,'NL Query',23)
a.append('</g>')
# m and requested output are given inputs: no arrow falsely derives them from query.
path('M84 121 H120',arrow=False);path('M120 95 V352',arrow=False)
path('M85 317 H120',arrow=False)
for yy in [95,352]:path(f'M120 {yy} H154')
rect(154,63,263,65,'white','#BBCBBB',5)
text(285,86,'Items per sorted run',24)
for yy,ww in [(95,100),(107,64),(119,84)]:
 rect(175,yy,ww,5,sage,green,1,1)
path('M286 95 H391',arrow=False,sw=1)
path('M286 107 H353',arrow=False,sw=1)
path('M286 119 H373',arrow=False,sw=1)
rect(154,143,263,65,'white','#BBCBBB',5)
text(285,167,'m: max items per call',24)
for q in range(7):rect(178+q*29,180,20,16,'white',steel,2,1)
path('M173 177 V201 H404 V177',color=steel,arrow=False)
rect(154,223,263,65,'white','#BBCBBB',5)
text(285,246,'Requested output',24)
# Full grid and shorter prefix are mode identities, not observed counts.
rect(167,253,36,25,'white',green,2,1)
for yy in [258,266]:
 for q in range(5):rect(171+q*5.5,yy,4,5,sage,green,0,0.6)
text(235,273,'Full /',23)
rect(276,255,35,22,'white',gold,2,1)
for q in range(3):rect(280+q*9,259,6,13,pale,gold,1,.7)
text(364,273,'LIMIT K',23)
rect(154,303,263,98,'white','#BBCBBB',5)
rect(166,315,239,33,'#DDD2E7','#82718E',3,1)
text(285,337,'System prompt',24)
text(182,378,'+',25)
for xx,hh in [(205,32),(232,26),(259,36)]:
 rect(xx,353,21,hh,sage,green,2,1)
 for dy in [8,16]:path(f'M{xx+4} {353+dy} H{xx+17}',color=green,arrow=False,sw=1)
text(346,378,'Documents',23)
# Output of feature/configuration preparation enters the cost model.
for yy in [95,175,255,352]:path(f'M417 {yy} H430',arrow=False)
path('M430 95 V352',arrow=False)
path('M430 123 H475')
# Expanded, visually separated valid-family objects and per-candidate input estimate.
text(800,65,'Merge-input cost model',25,weight='bold')
rect(475,79,650,213,'white',steel,6)
for xx in [725,976]:path(f'M{xx} 88 V252',color='#D4DEE4',arrow=False,sw=1)
text(600,104,'Valid plans',24)
text(600,131,'b(k) h ≤ m',23,color=steel)
text(540,153,'SW',23)
text(665,153,'LT',23)
# SW: k separate run windows, each with h slots. Neither k nor h is a depth.
for xx in [504,529,554]:
 rect(xx,163,19,32,'white',gold,2,1)
 rect(xx+2,166,15,11,pale,gold,1,1)
 rect(xx+2,181,15,11,pale,gold,1,1)
path('M504 202 V207 H573 V202',gold,arrow=False,sw=1)
text(539,230,'k',23)
path('M578 163 H583 V195 H578',color=steel,arrow=False,sw=1)
text(596,187,'h',23,color=steel)
# LT: binary internal organization, segment capacity carried by slots.
for xx,yy in [(665,171),(638,210),(692,210)]:
 rect(xx-13,yy-8,26,16,'white',steel,1,1)
 path(f'M{xx} {yy-8} V{yy+8}',color=steel,arrow=False,sw=1)
path('M638 202 L665 179');path('M692 202 L665 179')
text(697,178,'h',23,color=steel)
path('M625 225 V230 H705 V225',color=steel,arrow=False,sw=1)
text(665,253,'k',23)

text(850,104,'Input tokens',24)
rect(739,115,223,81,'white',steel,3,1)
rect(744,121,213,28,'#DDD2E7','#82718E',2,1)
text(850,143,'H: call overhead',23)
for xx,hh in [(752,28),(801,23),(850,33),(899,25)]:
 rect(xx,156,29,hh,sage,green,2,1)
 for dy in [8,16]:path(f'M{xx+5} {156+dy} H{xx+24}',color=green,arrow=False,sw=1)
text(850,220,'L: avg item tokens',23)
text(1051,104,'Select min',24)
# Persistent A/B/C badges connect example plan objects and their estimated costs.
for j,(yy,ww,hh,chosen) in enumerate([(122,72,22,False),(162,35,14,True),(202,55,19,False)]):
 rect(987,yy-5,29,29,pale if chosen else 'white',gold if chosen else steel,5,1.3)
 text(1001.5,yy+16,'ABC'[j],23,color='#8F4C00' if chosen else steel)
 rect(1022,yy,ww,16,'white',gold if chosen else steel,2,2 if chosen else 1)
 rect(1024,yy+2,hh-2,12,'#DDD2E7','none',0,0)
 rect(1022+hh,yy+2,ww-hh-2,12,sage,'none',0,0)
 if chosen:
  path(f'M{1022+ww} {yy+8} H1103 V292',gold,arrow=False,sw=2)
  text(1103,158,'✓',23,color=green)
text(1051,250,'…',23,color=steel)
path('M714 112 H736',sw=1.5);path('M963 112 H987',sw=1.5)
# Color identities persist from input profile into the actual estimate.
a.append('<text x="800" y="280" font-size="23" font-weight="bold" text-anchor="middle" xml:space="preserve"><tspan fill="#756080">H × calls</tspan><tspan fill="#262626"> + </tspan><tspan fill="#52775C">L × item appearances</tspan></text>')
# Candidate cards are unchanged semantically from v9.
a.append('<g transform="translate(220,150)">')
for j,x in enumerate([250,490,730]):
 chosen=j==1
 if chosen:rect(x,158,169,139,'#FFF8E7',gold,6,3.2)
 else:path(f'M{x+10} 191 H{x+159}',color='#B5B5B5',arrow=False,sw=1.2)
 rect(x+4,159,29,29,pale if chosen else 'white',gold if chosen else steel,5,1.3)
 text(x+18.5,180,'ABC'[j],23,color='#8F4C00' if chosen else steel)
 text(x+99,183,['vary k','Selected','vary h'][j],24,weight='bold' if chosen else 'normal')
 root=(x+84,207)
 def payload(xx,yy,width=28):
  # Empty cells encode capacity only, never occupancy or emitted values.
  n=4 if j==2 else 2
  cell=8; total=n*cell
  rect(xx-total/2,yy-8,total,16,'white',steel,1,1.8)
  for q in range(1,n):path(f'M{xx-total/2+q*cell} {yy-8} V{yy+8}',color=steel,arrow=False,sw=1.2)
 if j==0:
  for xx in [x+20,x+62,x+106,x+148]:
   payload(xx,279,27);path(f'M{xx} 271 L{root[0]} 215')
 else:
  for idx,xx in enumerate([x+20,x+62,x+106,x+148]):
   payload(xx,279,27);midx=x+42 if idx<2 else x+127
   path(f'M{xx} 271 L{midx} 249')
  for xx in [x+42,x+127]:payload(xx,241,32);path(f'M{xx} 233 L{root[0]} 215')
 payload(*root,width=38)
 # Root annotation repeats the parameter, while empty slots show capacity.
 text(root[0]+(32 if j==2 else 23),root[1]+7,'h',24,color=steel)

a.append('</g>')
text(1128,390,'…',23,color=steel)
path('M1103 292 V300 H794 V308',gold,sw=2)
path('M794 447 V459 H1158 V89 H1236 V120 H1250',color=steel)
text(1175,252,'or',23,'start',color=steel)
path('M1158 459 V288 H1236 V318 H1250',color=steel)
# Compact execution lanes free width for the candidate-plan visual comparison.
text(1175,76,'Full Ranking',25,'start','bold',green)
text(1201,134,'layer i',23);text(1201,215,'i+1',23)
rect(1250,96,238,77,'#EFF5EE',green,5,1.8)
rect(1250,189,238,40,'white','#C6CBC8',5,1)
for xx in [1288,1369,1450]:
 rect(xx-24,106,48,28,sage,green,14,1.5)
 for q in range(3):rect(xx-15+q*10,115,7,10,pale,gold,1,1)
 path(f'M{xx} 134 V146',color=green)
 rect(xx-28,146,56,18,'white',green,2,1.5)
 for q in range(4):
  rect(xx-23+q*12,150,9,10,sage,green,1,1)
  path(f'M{xx-21+q*12} 154 H{xx-16+q*12}',color=green,arrow=False,sw=.7)
 rect(xx-24,196,48,26,'white','#C6CBC8',13,1)
 path(f'M{xx} 164 V189',color=green)
# Short barrier ends inside the stage width; completion mark does not extend it.
path('M1258 181 H1480',color=green,arrow=False,sw=3)
text(1500,183,'✓',24,color=green)
path('M1488 209 H1510')
rect(1510,191,76,40,sage,green,4,1.6)
for yy in [198,208,218]:
 for q in range(5):rect(1518+q*12,yy,9,5,'white',green,1,1)
text(1548,253,'all results',23)
text(1175,274,'LIMIT K',25,'start','bold','#8F4C00')
text(1201,327,'layer i',23);text(1201,395,'i+1',23)
for yy in [297,365]:
 rect(1250,yy,238,43,'white','#D4D7D5',5,1)
 for xx in [1288,1369,1450]:
  active=xx==1369
  rect(xx-24,yy+8,48,27,pale if active else 'white',gold if active else '#CCD0CD',14,1.6 if active else 1)
  if active:
   for q in range(3):
    rect(xx-15+q*11,yy+16,8,10,pale if q==0 else 'white',gold,1,1)
    if q==0:path(f'M{xx-13+q*11} {yy+20} H{xx-9+q*11}',color=gold,arrow=False,sw=.7)
path('M1358 332 V373');path('M1380 373 V332',gold,True)
path('M1393 386 H1410 V426 H1498 V388 H1510')
rect(1510,368,76,40,pale,gold,5);text(1548,397,'K',24)
path('M1548 408 V437 H1369 V400',gold,True)
path('M1455 433 V444',gold,False,False,3)
text(1180,466,'results',23,'start');path('M1254 458 H1288')
path('M1357 458 H1323',gold,True);text(1365,466,'pull',23,'start',color='#8F4C00')
text(1497,466,'stop: K or EOF',23,color='#8F4C00')
a.append('</g></svg>');(D/'framework.svg').write_text('\n'.join(a))
