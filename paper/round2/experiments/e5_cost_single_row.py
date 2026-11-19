"""Cost-only 2x2 panels at true single-column scale. Data unchanged; all K labels."""
from pathlib import Path
import json,hashlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import e5
O=Path(__file__).parent/'figures/e5-cost-row';O.mkdir(exist_ok=True)
e5._font_setup();rows,meta=e5.load();audit=[]
for ds,state,tag in [('DL20','Off','dl20-off'),('DL20','On-cold','dl20-on'),('COVID','Off','covid-off'),('COVID','On-cold','covid-on')]:
 W=120.12328;H=79;fig=plt.figure(figsize=(W/72,H/72))
 a=fig.add_axes([21/W,15/H,82.4/W,62/H]);f=fig.add_axes([109.4/W,15/H,9/W,62/H]);ylim=meta['y_limits_1e3'][state]
 for ax in [a,f]:
  ax.set_ylim(ylim);ax.tick_params(width=.4,length=1.2,pad=.7,labelsize=6.1)
  for sp in ax.spines.values():sp.set_linewidth(.4);sp.set_color('#737373')
 a.set_xlim(-.45,8.45);a.set_xticks(range(9));a.set_xticklabels([str(k) for k in e5.LIMIT_N],rotation=90,fontsize=6.1)
 a.set_yticks(e5._yticks(ylim));a.grid(axis='y',color='#DADADA',lw=.3);a.set_axisbelow(True);a.spines['right'].set_visible(False);a.spines['top'].set_visible(False)
 f.set_xlim(-.7,.7);f.set_yticks([]);f.set_xticks([0]);f.set_xticklabels(['Full'],rotation=90,fontsize=6.1);f.set_facecolor('#F5F5F5');f.spines['left'].set_visible(False);f.spines['top'].set_visible(False)
 for y in [15,77]:fig.add_artist(Line2D([104.4/W,107.4/W],[(y-.7)/H,(y+.7)/H],transform=fig.transFigure,color='#333333',lw=.5))
 fig.text(3.7/W,46/H,'Tokens (×10³)',ha='center',va='center',rotation=90,fontsize=6.1)
 vals={};key='cost_input_equiv_1e3'
 series={family:[float(q[key]) for q in e5._series(rows,state,ds,family,'limit')] for family in ('SW','LT')}
 ties=[i for i,(sw,lt) in enumerate(zip(series['SW'],series['LT'])) if sw==lt]
 distinct=[i for i in range(9) if i not in ties]
 for family,color,marker,dodge in [('SW',e5.SW_RGB,'o',-.24),('LT',e5.LT_RGB,'^',.24)]:
  v=series[family];full=float(e5._series(rows,state,ds,family,'full')[0][key]);vals[family]={'limit':v,'full':full}
  a.plot(range(9),v,color=color,marker=marker,markevery=distinct,ms=e5.MARKER_PT,lw=e5.LINE_PT,mfc=color if family=='SW' else 'white',mec=color,mew=e5.EDGE_PT,zorder=3)
  f.plot([dodge],[full],ls='none',color=color,marker=marker,ms=e5.MARKER_PT,mfc=color if family=='SW' else 'white',mec=color,mew=e5.EDGE_PT,zorder=3)
 if ties:
  ty=[series['SW'][i] for i in ties]
  a.scatter(ties,ty,marker='^',s=5.4**2,facecolors='white',edgecolors=e5.LT_RGB,linewidths=.65,zorder=4)
  a.scatter(ties,ty,marker='o',s=1.65**2,facecolors=e5.SW_RGB,edgecolors=e5.SW_RGB,linewidths=.25,zorder=5)
 fig.canvas.draw();texts=[t for ax in [a,f]for t in ax.get_xticklabels()+ax.get_yticklabels() if t.get_text()]+fig.texts;bb=[t.get_window_extent(fig.canvas.get_renderer())for t in texts]
 assert all(b.x0 >= 0 and b.y0 >= 0 and b.x1 <= fig.bbox.width and b.y1 <= fig.bbox.height for b in bb), 'tick clipped'
 for i,x in enumerate(bb):
  for y in bb[i+1:]:assert not x.overlaps(y),'tick overlap'
 for ext in ['pdf','svg']:fig.savefig(O/f'e5-cost-{tag}.{ext}')
 audit.append({'dataset':ds,'state':state,'values':vals,'all_K':list(e5.LIMIT_N),'labeled_K':list(e5.LIMIT_N),'tie_K':[e5.LIMIT_N[i] for i in ties],'width_bp':W,'height_bp':H});plt.close(fig)
fig=plt.figure(figsize=(240.24656/72,14/72));fig.legend(**e5.legend_keys(),loc='center',ncol=3,frameon=False,fontsize=6.3,handlelength=2.2)
for ext in ['pdf','svg']:fig.savefig(O/f'e5-cost-legend.{ext}')
(O/'validation.json').write_text(json.dumps({'synthetic':True,'data_sha256':hashlib.sha256(e5.DATA.read_bytes()).hexdigest(),'panels':audit},indent=2))
