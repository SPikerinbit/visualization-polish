from pathlib import Path
from html import escape
D=Path(__file__).resolve().parents[1];a=[]
W,H=1600,474
ink='#262626';gray='#666666';gold='#E07B00';pale='#FFE5A3';sage='#DDEBDD';green='#52775C';blue='#E5EDF3';steel='#647E91'
a.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="178mm" height="{178*H/W}mm" viewBox="0 0 {W} {H}"><title>Cost-guided semantic merge execution</title><desc>Abstract sorted runs inform a cost model. Feasible merge structures are evaluated for the requested mode, and the selected parameters configure either full materialization or demand-driven LIMIT execution. Solid push arrows return requested results downstream. Dashed pull arrows request data upstream; requests stop at K outputs or end of input.</desc><defs>')
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
for x,s,end,c in [(12,'Planning inputs',414,green),(465,'Cost-effective plan',1134,steel),(1175,'Execute the selected plan',1590,gold)]:
 text(x,28,s,27,'start','bold');path(f'M{x} 40 H{end}',color=c,arrow=False,sw=3)
for x in [447,1145]:path(f'M{x} 50 V{H-40}',color='#DDDDDD',arrow=False,sw=1)
# Document and request sources are distinct from derived sizes and configuration.
for x,y in [(18,99),(24,93),(30,87)]:rect(x,y,54,64,'white',green,3)
# Front document: folded corner, hierarchy and ragged text, not a generic rectangle.
path('M72 87 V99 H84',color=green,arrow=False,sw=1.2)
rect(38,100,20,4,sage,'none',1,0)
for yy,ww in [(113,36),(123,30),(133,35),(142,22)]:
 path(f'M38 {yy} H{38+ww}',color=green,arrow=False,sw=1.3)
text(57,180,'Documents',23)
# Natural-language query is an entity, distinct from runtime configuration.
a.append('<g transform="translate(0,60)">')
for xx,yy in [(19,226),(25,220),(31,214)]:rect(xx,yy,54,61,'white',gold,3)
rect(31,214,54,14,pale,gold,3,1)
# Query keeps the document-stack family but uses quotation marks and phrase rhythm.
path('M40 235 h-3 v5 h4 M47 235 h-3 v5 h4',gold,arrow=False,sw=1.4)
for yy,xx,ww in [(238,53,22),(249,39,34),(259,39,27)]:
 path(f'M{xx} {yy} H{xx+ww}',gold,arrow=False,sw=1.3)
text(62,313,'NL Query',23)
a.append('</g>')
# m and requested output are given inputs: no arrow falsely derives them from query.
# Two independent source inlets join one four-card input bundle.
# Neutral, undirected port branches denote grouping, NOT derivation of m/options.
a.append('<g id="planning-input-bundle"><desc>Documents and NL Query enter a shared planning-input bundle. Four hollow ports associate all four cards with this bundle; undirected branches do not imply that capacity or requested mode are computed from document text.</desc>')
path('M124 95 V352',color='#9BA6AB',arrow=False,sw=1.4)
for yy in [95,175,255,352]:
 path(f'M124 {yy} H147',color='#9BA6AB',arrow=False,sw=1.4)
 a.append(f'<circle cx="150" cy="{yy}" r="3" fill="white" stroke="#9BA6AB" stroke-width="1.4"/>')
path('M84 121 H124',color=green)
path('M85 317 H124',color=gold)
a.append('</g>')
# Four input cards keep the same connection ports. Icon rows explain rather than decorate.
def card(x,y,w,h,title):
 rect(x,y,w,h,'white','#AFBFB5',6,1.55)
 rect(x+1,y+1,w-2,29,'#F0F5F1','none',5,0)
 text(x+w/2,y+22,title,23)
card(154,63,263,65,'Items per sorted run')
# Bound each strip as a run; segment count varies with run length.
for yy,n in [(97,8),(107,5),(117,7)]:
 width=n*26-3
 rect(182,yy-2,width+10,9,'#F5F8F5','#A4B9AA',3,.85)
 for i in range(n):
  rect(187+i*26,yy,23,5,sage if i%2==0 else '#EFF5EE',green,1,.8)

card(154,143,263,65,'Max items per listwise call')
rect(162,174,86,28,'#F3F6F9','#C3CED6',4,1.1)
# Compact vector brain: circuit hemisphere + organic hemisphere, inspired by supplied reference.
a.append('<g id="llm-brain" transform="translate(169,175) scale(.35)" stroke-linecap="round" stroke-linejoin="round">')
path('M36 6 C24 -2 9 3 9 15 C-1 18 -1 29 5 33 C-3 40 0 51 7 54 C1 65 13 77 25 72 C30 76 35 73 36 69 Z',color=steel,arrow=False,sw=3.4)
path('M44 6 C55 -2 70 3 70 15 C81 18 81 29 75 33 C83 40 80 51 73 54 C79 65 67 77 55 72 C50 76 45 73 44 69 Z',color=steel,arrow=False,sw=3.4)
path('M40 7 V70',color=steel,dash=True,arrow=False,sw=2.4)
path('M22 16 V36 H12 M22 36 V51 H31 V64 H20 M6 58 H17 V48 H9',color=steel,arrow=False,sw=3.4)
for xx,yy in [(22,16),(12,36),(20,64),(9,48)]:
 a.append(f'<circle cx="{xx}" cy="{yy}" r="3.6" fill="{blue}" stroke="{steel}" stroke-width="2.6"/>')
path('M56 10 C65 19 47 20 50 29 C53 36 65 29 67 38 C69 46 56 44 56 53 C53 61 63 64 60 70 M73 26 C63 20 58 30 60 34 M72 53 C65 47 65 60 70 62',color=gold,arrow=False,sw=3.4)
a.append('</g>')
text(222,194,'LLM',20,color=steel)
# Slot rack and a bounded maximum; the empty slots show capacity, not occupancy.
for q in range(6):
 rect(266+q*18,180,15,14,'#F5F8FB',steel,2,1)
path('M260 177 v22 h116 v-22',steel,arrow=False,sw=1.4)
text(393,194,'m',22,weight='bold',color=steel)

card(154,223,263,65,'Requested output')
rect(164,254,116,27,'#EFF5EE','#BBCDBD',4,1.1)
rect(290,254,117,27,'#FFFAED','#E6C78B',4,1.1)
for yy in [260,268]:
 for q in range(5):rect(172+q*5.5,yy,4,5,sage,green,.6,.6)
text(237,274,'Full',22,color=green)
path('M296 259 h-2 v16 h2 M320 259 h2 v16 h-2',gold,arrow=False,sw=1)
for q in range(3):rect(298+q*7,261,6,12,pale,gold,1,.7)
text(367,274,'LIMIT K',21,color='#8F4C00')

card(154,303,263,98,'Input token profile')
# Separate overhead and per-item cues with identical module geometry.
rect(163,338,119,53,'#F6F0F8','#C9B8D1',4,1.1)
rect(289,338,119,53,'#F1F6F0','#B7CBB9',4,1.1)
text(178,360,'H',22,weight='bold',color='#756080')
text(302,360,'L',22,weight='bold',color=green)
rect(209,343,31,19,'white','#82718E',3,1.2)
path('M217 350 l-3 3 3 3 M232 350 l3 3 -3 3 M226 348 l-3 10',color='#82718E',arrow=False,sw=1)
for xx,dy in [(330,2),(344,0),(358,3)]:
 rect(xx,343+dy,12,17,sage,green,1,1)
 path(f'M{xx+3} {348+dy} h6 M{xx+3} {352+dy} h5',green,arrow=False,sw=.9)
text(222.5,383,'System prompt',18.5,color='#684F73')
text(348.5,383,'Documents',20,color=green)

# Output of feature/configuration preparation enters the cost model.
for yy in [95,175,255,352]:path(f'M417 {yy} H430',arrow=False)
path('M430 95 V352',arrow=False)
path('M430 123 H475')
# The planner's three operations read as check capacity → estimate tokens → choose.
violet='#7E608F'
purple='#E9DAF0'
darkamber='#8F4C00'
text(800,65,'Merge-input cost model',25,weight='bold')
rect(475,78,650,213,'white',steel,8,1.8)
for x,w,caption,fill in [(482,218,'Valid plans','#EAF0F6'),(720,221,'Estimate tokens','#F3EEF6'),(961,145,'Select min','#FBF2E1')]:
 rect(x,86,w,30,fill,'none',4,0)
 text(x+w/2,108,caption,24,weight='bold')
for xx in [711,951]:path(f'M{xx} 123 V247',color='#D4DEE4',arrow=False,sw=1.15)
for xx in [703,943]:path(f'M{xx} 102 h14',steel,sw=1.5)

# Two distinct live-buffer structures; diagrams represent slots, not observed items.
text(539,140,'SW',23,color=darkamber)
text(647,140,'LT',23,color=steel)
for xx in [505,531,557]:
 rect(xx,150,18,42,'#FFF8E7',gold,2,1.3)
 for yy in [154,166,178]:rect(xx+3,yy,12,9,pale,gold,1,.65)
path('M505 198 v4 h70 v-4',gold,arrow=False,sw=1)
text(540,225,'k',22,color=darkamber)
path('M501 151 h-4 v41 h4',gold,arrow=False,sw=1)
text(490,178,'h',20,color=darkamber)
# A binary bracket feeds a highlighted path; ghost bins are not charged as live slots.
path('M620 191 L635 171 L652 153 M649 191 L635 171 M681 188 L669 171 L652 153',steel,arrow=False,sw=1.25)
for xx,yy,active in [(652,153,True),(635,171,True),(669,171,False),(620,191,True),(649,191,False),(681,191,False)]:
 rect(xx-10,yy-5,20,10,blue if active else 'white',steel if active else '#C0CAD1',2,1)
 for dx in [-3,3]:path(f'M{xx+dx} {yy-4} v8',steel if active else '#C0CAD1',arrow=False,sw=.7)
path('M608 198 v4 h85 v-4',steel,arrow=False,sw=1)
text(650,225,'k',22,color=steel)
text(678,158,'h',20,color=steel)
text(591,248,'b(k) h ≤ m',23,color=steel)

# One schematic sequence, not a second rendering of the pricing equation.
# Violet caps denote estimated call boundaries. Dark green repeats are the
# same item across successive example calls, not cached tokens or measured counts.
text(830,140,'Expected merge work',23,color=steel)
for x,n,highlight in [(738,3,1),(806,2,0),(874,3,0)]:
 rect(x,156,50,45,'white',violet,3,1.25)
 rect(x+1,157,48,10,purple,'none',2,0)
 path(f'M{x+7} 162 h13',violet,arrow=False,sw=1.15)
 for c in range(n):
  xx=x+6+c*13
  active=c==highlight
  rect(xx,175,11,17,green if active else sage,green,1,1)
  path(f'M{xx+3} 181 h5 M{xx+3} 185 h4',
       'white' if active else green,arrow=False,sw=.9)
 if x<874:
  path(f'M{x+52} 178 h13',steel,sw=1.3)
# Dotted identity guide connects the repeated item across calls, not execution edges.
xs=[762.5,817.5,885.5]
path(f'M{xs[0]} 194 v23 H{xs[-1]} v-23 M{xs[1]} 194 v23',
     green,True,False,1.1)
text(830,243,'Same item can reappear',21,color=green)

# Split cost bars carry the two equation colors; A/B/C denote schematic candidates.
for j,(yy,w,overhead,selected) in enumerate([(135,83,27,False),(173,49,19,True),(211,68,23,False)]):
 if selected:rect(961,yy-16,145,32,'#FFF8E7',gold,4,1.2)
 rect(969,yy-11,23,22,pale if selected else 'white',gold if selected else steel,4,1)
 text(980.5,yy+7,'ABC'[j],20,color=darkamber if selected else steel)
 rect(1000,yy-8,w,16,'white',gold if selected else steel,2,1.25)
 rect(1001,yy-7,overhead,14,purple,'none',1,0)
 rect(1001+overhead,yy-7,w-overhead-2,14,sage,'none',1,0)
 if selected:
  a.append(f'<circle cx="1066" cy="{yy}" r="9" fill="{sage}" stroke="{green}" stroke-width="1.1"/>')
  path(f'M1062 {yy} l3 3 5 -6',green,arrow=False,sw=1.7)
text(1034,248,'…',23,color=steel)
rect(500,259,600,25,'#F8FAFB','none',5,0)
a.append('<text x="800" y="279" font-size="23" font-weight="bold" text-anchor="middle" xml:space="preserve"><tspan fill="#756080">H × calls</tspan><tspan fill="#262626"> + </tspan><tspan fill="#52775C">L × item appearances</tspan></text>')
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
  for xx in [x+12,x+48,x+84,x+120,x+156]:
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
path('M1082 173 H1120 V299 H794 V308',gold,sw=2)
path('M794 447 V459 H1158 V89 H1236 V120 H1250',color=steel)
path('M1158 459 V288 H1236 V318 H1250',color=steel)
# R6 execution-zone fragment. Uses the parent generator's a/text/rect/path and palette.
# Selected-plan inputs retain x1250,y120 (Full) and x1250,y318 (LIMIT).
text(1382.5,76,'Full Ranking',25,'middle','bold',green)
text(1201,134,'layer i',23)
text(1201,219,'i+1',23)
# The three producers materialize into a continuous, visibly complete layer buffer.
rect(1250,96,238,77,'#EFF5EE',green,5,1.8)
for xx in [1288,1369,1450]:
 rect(xx-24,106,48,28,sage,green,14,1.5)
 for q in range(3):rect(xx-15+q*10,115,7,10,pale,gold,1,1)
 path(f'M{xx} 134 V146',color=green)
 rect(xx-28,146,56,18,'white',green,2,1.5)
 for q in range(4):
  rect(xx-23+q*12,150,9,10,sage,green,1,1)
  path(f'M{xx-21+q*12} 154 H{xx-16+q*12}',color=green,arrow=False,sw=.7)
# One completed layer is the transfer unit; no implied group-to-group edge.
rect(1258,165,222,8,sage,green,2,1.2)
a.append('<path id="materialized-layer-transfer" d="M1355 173 H1383 V183 H1399 L1369 196 L1339 183 H1355 Z" fill="#63846A" stroke="#52775C" stroke-width="1.15" stroke-linejoin="round"/>')
text(1540,161,'all groups',22,color=green)
text(1540,187,'ready',22,color=green)
rect(1250,197,238,40,'white','#C6CBC8',5,1)
for xx in [1288,1369,1450]:
 rect(xx-24,204,48,26,'white',green,13,1.2)
path('M1488 217 H1510',color=green)
rect(1510,199,76,40,sage,green,4,1.6)
for yy in [206,216,226]:
 for q in range(5):rect(1518+q*12,yy,9,5,'white',green,1,1)
text(1548,260,'all results',23)
text(1382.5,285,'LIMIT K',25,'middle','bold','#8F4C00')
text(1201,327,'layer i',23)
text(1201,411,'i+1',23)
# The unbroken pale corridor is restricted to the active path, not a layer barrier.
rect(1339,319,60,88,'#FFF8E7','none',12,0)
for yy in [297,381]:
 rect(1250,yy,238,43,'white','#D4D7D5',5,1)
 for xx in [1288,1369,1450]:
  active=xx==1369
  rect(xx-24,yy+8,48,27,pale if active else 'white',gold if active else '#CCD0CD',14,1.6 if active else 1)
  if active:
   for q in range(3):
    rect(xx-15+q*11,yy+16,8,10,pale if q==0 else 'white',gold,1,1)
    if q==0:path(f'M{xx-13+q*11} {yy+20} H{xx-9+q*11}',color=gold,arrow=False,sw=.7)
# Actual transfer arrows: push down / demand pull up. Labels sit on opposite sides.
path('M1358 332 V389',color=gray,sw=2)
path('M1380 389 V332',gold,True,sw=2)
text(1318,369,'push',23,color=gray)
text(1424,369,'pull',23,color='#8F4C00')
# A direct emitted prefix sits below the active producer: no loop around inactive nodes.
path('M1369 416 V434',color=gray,sw=2)
rect(1331,434,76,30,pale,gold,5)
path('M1338 440 H1343 M1338 440 V458 H1343 M1400 440 H1395 M1400 440 V458 H1395',color=gold,arrow=False,sw=1.2)
text(1369,457,'K',24)
text(1498,455,'stop: K or EOF',22,color='#8F4C00')

a.append('</g></svg>');(D/'framework.svg').write_text('\n'.join(a))
