from pathlib import Path
import json,hashlib,sys
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import e4c
from pdfutil import configure_matplotlib
from style import pt_to_in,COLUMN_PT
R=Path(__file__).parent;e4c.SOURCE=R/'data.json'; configure_matplotlib()
means=e4c.average(e4c.load_points());out=R/'panels';out.mkdir(exist_ok=True)
colors=['#C17422','#5D8F70','#9176AB','#997468','#B27D9C','#548F99','#989849','#7B858A','#B85F60','#4E7D9D']
methods={m['id']:{**m,'color':c} for m,c in zip(e4c.METHODS,colors)}
def mark(m):
 return dict(ls='',marker=m['marker'],ms=4.7 if m['id'] in ['sw','lt'] else (5.5 if m['marker']=='*' else 4.4),mfc=m['color'] if m['id'] in ['sw','lt'] else 'white',mec=m['color'],mew=.85)
xlim=e4c._limits([p['x']/1000 for p in means],.08)
record={'means':means,'fronts':{},'limits':{},'source_sha256':hashlib.sha256(e4c.SOURCE.read_bytes()).hexdigest()}
for metric in ['full','topk']:
 ylim=e4c._limits([p['y'] for p in means if p['metric']==metric])
 for state in ['Off','On-cold']:
  f,ax=plt.subplots(figsize=(pt_to_in(COLUMN_PT*.49),pt_to_in(72 if metric=='full' else 82)))
  f.subplots_adjust(left=.22,right=.98,bottom=.04 if metric=='full' else .16,top=.98)
  ax.set_xlim(*xlim);ax.set_ylim(*ylim)
  ax.set_xticks(e4c._inner_ticks(xlim,10));ax.set_yticks(e4c._inner_ticks(ylim,.1 if ylim[1]-ylim[0]>.2 else .05))
  ax.tick_params(labelbottom=(metric!='full'),labelsize=6.8,length=2,width=.45,pad=1.2,color='#737C82')
  ax.grid(axis='y',color='#E5E8EA',lw=.3);ax.set_axisbelow(True)
  for side in ['top','right']:ax.spines[side].set_visible(False)
  for side in ['bottom','left']:ax.spines[side].set_color('#858D93');ax.spines[side].set_linewidth(.45)
  if state=='Off':ax.set_ylabel('Spearman' if metric=='full' else 'NDCG@10',fontsize=7.4,labelpad=1)
  points=[p for p in means if p['metric']==metric and p['state']==state];front=e4c.nondominated(points)
  if len(front)>1:ax.plot([p['x']/1000 for p in front],[p['y'] for p in front],color='#737B80',lw=.65,ls=(0,(3,2)),zorder=2)
  # Singleton and multivertex frontiers use the same unfilled membership cue.
  for v in front:ax.plot(v['x']/1000,v['y'],marker='o',ms=8.0,ls='',mfc='none',mec='#596168',mew=.5,zorder=2.8)
  for p in points:ax.plot(p['x']/1000,p['y'],**mark(methods[p['method']]),zorder=3)
  stem=f'e4c-{metric}-{state.lower()}';f.savefig(out/f'{stem}.pdf');f.savefig(out/f'{stem}.svg')
  if metric=='full':
   f.set_size_inches(pt_to_in(COLUMN_PT*.49),pt_to_in(82));f.subplots_adjust(bottom=.16);ax.tick_params(labelbottom=True)
   (R/'standalone-raw').mkdir(exist_ok=True);f.savefig(R/'standalone-raw'/f'{stem}.pdf')
  plt.close(f)
  record['fronts'][stem]=front;record['limits'][stem]={'x':xlim,'y':ylim}
f=plt.figure(figsize=(pt_to_in(COLUMN_PT),pt_to_in(25)))
# Fixed two-row table: preserves all ten names without spacing squeezed by longest entry.
order=['pointwise','ext_pointwise','bubble','merge','listk','tournament','lotus','setwise','sw','lt']
from matplotlib.textpath import TextToPath
from matplotlib.font_manager import FontProperties
prop=FontProperties(family='Liberation Serif',size=7.2)
measure=TextToPath()
label_widths=[max(measure.get_text_width_height_descent(methods[order[j]]['legend'],prop,False)[0],measure.get_text_width_height_descent(methods[order[j+5]]['legend'],prop,False)[0]) for j in range(5)]
widths=[5.5+3+w for w in label_widths]
gap=(COLUMN_PT-5-sum(widths))/4
assert gap>=5
xs=[];left=2.5
for width in widths:
 xs.append((left+2.75)/COLUMN_PT);left+=width+gap
for i,mid in enumerate(order):
 m=methods[mid];x=xs[i%5];y=.74 if i<5 else .28
 f.add_artist(Line2D([x],[y],transform=f.transFigure,**mark(m)))
 f.text(x+5.75/COLUMN_PT,y,m['legend'],fontsize=7.2,va='center',ha='left')
f.savefig(R/'e4c-legend.pdf');f.savefig(R/'e4c-legend.svg');plt.close(f)
(R/'records.json').write_text(json.dumps(record,indent=2))
