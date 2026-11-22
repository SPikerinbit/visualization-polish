from pathlib import Path
import json,html,subprocess
P=Path(__file__).resolve().parent
W=240.24655
RUNS=[[3,7,12,16],[1,5,6,14],[2,8,11,15],[4,9,10,13]]
run={n:i for i,r in enumerate(RUNS) for n in r}
def rounds():
 unread=[r[:] for r in RUNS]; kept=[]; trace=[]
 for _ in range(3):
  additions=[[] for r in RUNS]
  held=[[n for n in kept if run[n]==i] for i in range(4)]
  for i in range(4):
   while len(held[i])+len(additions[i])<2 and unread[i]:
    additions[i].append(unread[i].pop(0))
  supplied=[h+n for h,n in zip(held,additions)]
  rank=sorted(sum(supplied,[]))
  stop=len(rank); trigger=None
  remaining=list(map(len,supplied))
  for k,v in enumerate(rank):
   i=run[v];remaining[i]-=1
   if remaining[i]==0 and unread[i]:
    stop,trigger=k+1,i+1;break
  trace.append(dict(round=len(trace)+1,retain_before=held,new=additions,call=supplied,unread=[r[:] for r in unread],
                    ranked=rank,emitted=rank[:stop],retained=rank[stop:],trigger=trigger))
  kept=rank[stop:]
 return trace
T=rounds()
assert [r['ranked'] for r in T]==[[1,2,3,4,5,7,8,9],[6,7,8,9,10,11,12,14],[11,12,13,14,15,16]]
assert [r['trigger'] for r in T]==[2,4,None]
assert sum((r['emitted'] for r in T),[])==list(range(1,17))
assert [r['call'] for r in T]==[[[3,7],[1,5],[2,8],[4,9]],[[7,12],[6,14],[8,11],[9,10]],[[12,16],[14],[11,15],[13]]]
assert [r['unread'] for r in T]==[[[12,16],[6,14],[11,15],[10,13]],[[16],[],[15],[13]],[[],[],[],[]]]
INK='#252B2E'; MUTE='#626A70'; GRAY='#A8AFB4'; LINE='#CED4D7'; WARM='#AC6D0B'; CREAM='#FFE3AE'; WASH='#FFF4DC'
LEAF='#DDEBDD'; FOREST='#4F6B56'; GHOST='#747D81'
STYLE={'new':(CREAM,WARM,''),'held':('white','#4A535A',''),'emit':(LEAF,FOREST,''),'unread':('white',GHOST,'1.17 .88')}
def f(x):return f'{x:.4f}'
class Art:
 def __init__(self,H,title):
  self.H=H;self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><title>{title}</title><desc>m=8, h=2. Exact SW example. Run grouping depicts membership, not a re-sort of retained rows. R2 and R4 trigger rounds 1 and 2; all rows emit in the final round.</desc><defs><marker id="arrow" viewBox="0 0 6 6" refX="5.6" refY="3" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#747D81"/></marker></defs><rect width="{W}" height="{H}" fill="white"/><g font-family="TeX Gyre Termes, Liberation Serif, serif" fill="{INK}">']
 def txt(self,x,y,t,size=5.7,anchor='middle',weight='normal',c=INK):self.s.append(f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{c}">{html.escape(str(t))}</text>')
 def rect(self,x,y,w,h,c='none',st='none',lw=0,rx=0,d=''):self.s.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{c}" stroke="{st}" stroke-width="{lw}"'+(f' stroke-dasharray="{d}"' if d else '')+'/>')
 def path(self,s,stroke=GRAY,lw=.45,arrow=False):self.s.append(f'<path d="{s}" fill="none" stroke="{stroke}" stroke-width="{lw}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def circle(self,x,y,status,n='',r=3.62):
  fill,b,d=STYLE[status]
  self.s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{fill}" stroke="{b}" stroke-width=".48"'+(f' stroke-dasharray="{d}"' if d else '')+'/>')
  if n!='':self.txt(x,y+1.86,n,5.5)
 def export(self,name):
  path=P/f'{name}.svg';path.write_text('\n'.join(self.s+['</g></svg>']))
  subprocess.run(['inkscape',str(path),'--export-filename='+str(P/f'{name}.pdf')],check=True,capture_output=True)
  subprocess.run(['pdftoppm','-r','300','-png','-singlefile',str(P/f'{name}.pdf'),str(P/name)],check=True,capture_output=True)
def legend(a,y,pre=None):
 for x,status,word in [(7,'new','New'),(53,'held','Retained'),(110,'unread','Unread'),(168,'emit','Emitted')]:
  a.circle(x,y,status,r=2.35);a.txt(x+4.5,y+1.95,word,5.9,'start')
 if pre: a.txt(237,y+1.7,pre,5.65,'end',c=MUTE)
def pair(a,x,y,t,new,mode,large=False):
 if not t: a.txt(x,y+1.2,'–',5.5,c=GRAY)
 for off,v in zip((0,) if len(t)==1 else(-4.325,4.325) if large else (-4.03,4.03),t):
  a.circle(x+off,y,'new' if mode=='call' and v in new else 'held' if mode=='call' else 'unread',v,r=3.96 if large else 3.62)
def rank(a,x,y,r,strong=True,large=False):
 ctr=[x+5.35+i*8.65 for i in range(8)]
 xs=ctr[:len(r['ranked'])]
 if len(xs)==6:xs=[q+8.65 for q in xs]
 t=len(r['emitted'])
 cut=(xs[t-1]+xs[t])/2 if t<len(xs) else None
 for i,(p,n) in enumerate(zip(xs,r['ranked'])):a.circle(p,y,'emit' if i<t else 'held',n,r=3.96 if large else 3.62)
 if cut:
  if large:
   a.path(f'M{f(cut-1.75)} {y-6.0} l1.75 1.35 1.75 -1.35',WARM,.67)
   a.path(f'M{f(cut)} {y+4.8} v2.05',WARM,.71)
  else:
   a.path(f'M{f(cut)} {y-5.7} v11.4',WARM,.82)
   a.path(f'M{f(cut-1.52)} {y-5.3} l1.52 1.52 1.52 -1.52',WARM,.55)
 return cut,xs
def snapshots(large=False):
 a=Art(83.4,'Sliding-window merge: window, rank, emit and retain')
 for j,r in enumerate(T):
  x=2+j*80.1
  a.txt(x+37.1,7.6,f'Round {j+1}',7.05,weight='bold')
  a.path(f'M{x+1:.3f} 10.2 h73.4',LINE,.48)
  group=[x+9.8+i*18.45 for i in range(4)]
  for i,g in enumerate(group):
   target=r['trigger']==i+1
   incoming=large and j>0 and T[j-1]['trigger']==i+1
   if target:a.rect(g-7.25,11.7,14.5,8.2,WASH,rx=2)
   if incoming: a.rect(g-7.25,11.7,14.5,8.2,'white',WARM,.57,2)
   a.txt(g,17.75,'R'+str(i+1),5.8,weight='bold' if target or incoming else 'normal',c=WARM if target or incoming else MUTE)
   pair(a,g,27,r['unread'][i],[],'unread',large)
   pair(a,g,40,r['call'][i],r['new'][i],'call',large)
   if incoming:
    # Same badge as prior cut, with the new refill items safely inside the call.
    a.path(f'M{g-6.2:.3f} 45.8 h12.4',WARM,.65)
  a.rect(x+.8,34.9,73.4,10.2,'none','#BD8A45',.52,2,'1.6 1.15')
  a.path(f'M{x+37.2:.3f} 45.1 v6.2',GHOST,.48,True)
  cut,xs=rank(a,x,59.0,r,large=large)
  note=f"Emit {r['emitted'][0]}–{r['emitted'][-1]}" if j!=2 else 'Emit all six'
  a.txt(x+3,71.55,note,5.85,'start','bold',FOREST)
  if j<2:
   a.txt(x+73.5,71.55,(f"Refill R{r['trigger']}" if large else f"R{r['trigger']} sets cut"),5.85,'end','bold',WARM)
 for j in (0,1):
  x=79.3+j*80.1
  a.path(f'M{x-1:.3f} 6.3 h4.4',GHOST,.51,True)
 if large:
  for x,status,word in [(6,'new','New'),(45,'held','Retained'),(101,'unread','Unread'),(153,'emit','Emitted')]:
   a.circle(x,79.55,status,r=2.35);a.txt(x+4.45,81.50,word,5.9,'start')
  a.rect(210,77.2,7.1,4.6,'none','#BD8A45',.52,1.3,'1.6 1.15')
  a.txt(220.6,81.50,'Call',5.9,'start')
 else: legend(a,79.55,'Dashed frame: call')
 return a
def rails():
 a=Art(91.3,'Sliding-window merge: ranked cut and run-aligned state rails')
 for j,r in enumerate(T):
  x=2+j*80.1
  a.txt(x+37.1,7.6,f'Round {j+1}',7.05,weight='bold')
  a.path(f'M{x+1:.3f} 10.3 h73.4',LINE,.48)
  rank(a,x,18.6,r)
  a.txt(x+3,29.15,f'Emit {r["emitted"][0]}–{r["emitted"][-1]}',5.8,'start','bold',FOREST)
  if r['trigger']:a.txt(x+73.5,29.15,f'R{r["trigger"]} sets cut',5.8,'end','bold',WARM)
  else:a.txt(x+73.5,29.15,'No unread rows',5.8,'end',c=MUTE)
  a.txt(x+27.1,38.05,'Call window',5.65,c=MUTE)
  a.txt(x+56.1,38.05,'Unread',5.65,c=MUTE)
  a.path(f'M{x+6:.3f} 40.55 h65',LINE,.45)
  a.path(f'M{x+42:.3f} 43.0 v39.4',LINE,.48)
  for i in range(4):
   y=47.1+i*10.4
   target=r['trigger']==i+1
   if target:a.rect(x+2,y-4.4,71.2,8.8,WASH,rx=2)
   a.txt(x+4.1,y+1.86,'R'+str(i+1),5.8,'start','bold' if target else 'normal',WARM if target else MUTE)
   pair(a,x+27.1,y,r['call'][i],r['new'][i],'call')
   pair(a,x+56.1,y,r['unread'][i],[],'unread')
   if target:a.path(f'M{x+67:.3f} {y:.2f} h3.7',WARM,.55)
   if i<3:a.path(f'M{x+4:.3f} {y+5.2:.2f} h68',LINE,.34)
 legend(a,86.7)
 return a
for label,fig in [('A-window-to-rank',snapshots()),('B-run-rails',rails()),('A2-window-large',snapshots(large=True))]:fig.export(label)
(P/'states.json').write_text(json.dumps({'runs':RUNS,'m':8,'h':2,'trace':T},indent=2)+'\n')
