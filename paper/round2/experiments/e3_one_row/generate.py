from pathlib import Path
import sys,json,hashlib
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import e3
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
out=Path(__file__).resolve().parents[1]/'figures/e3-one-row';out.mkdir(parents=True,exist_ok=True);e3.configure_matplotlib();payload=e3.load();ylim=e3._ylim(payload);before=hashlib.sha256(e3.SOURCE.read_bytes()).hexdigest();checks=[]
e3.TABLEAU=("#0072B2","#D55E00","#009E73","#CC79A7","#8A6500","#3C58A6","#C34D28","#007F69","#A74C96","#7B7200")
for panel in payload['panels']:
 fam,mode=panel['family'],panel['mode'];offset=0 if fam=='SW' else 5
 first=fam=='SW' and mode=='Full'
 width=66.0 if first else (e3.PANEL_PT*4-66.0)/3
 left=13.5 if first else 4.0
 fig=plt.figure(figsize=(e3.pt_to_in(width),e3.pt_to_in(72)))
 ax=fig.add_axes([left/width,.215,49.0/width,.745]);e3._style_ax(ax,ylim)
 ax.tick_params(labelsize=5.5,pad=.5);ax.set_xlabel('$n$',fontsize=5.5,labelpad=.5)
 if fam=='SW' and mode=='Full':
  ax.set_ylabel('Layout units',fontsize=4.6,labelpad=.4)
 else: ax.tick_params(labelleft=False)
 for kind in ['measured','predicted']:
  for i,s in enumerate(panel['series']):
   c=e3.TABLEAU[offset+i]
   line,=ax.plot(e3.X,s[kind],color=c,marker=e3.MARKERS[i],markersize=2.4,markerfacecolor='white' if kind=='predicted' else c,markeredgecolor=c,markeredgewidth=e3.EDGE_PT,linewidth=e3.LINE_PT,linestyle=(0,(2.5,1.6)) if kind=='predicted' else '-',solid_capstyle='round',zorder=3 if kind=='predicted' else 2)
   np.testing.assert_array_equal(line.get_xdata(),e3.X);np.testing.assert_array_equal(line.get_ydata(),s[kind])
 stem=f'overlay-{fam.lower()}-{mode.lower()}'
 for ext in ['pdf','svg','png']:fig.savefig(out/(stem+'.'+ext),dpi=300)
 checks.append({'panel':stem,'xlim':ax.get_xlim(),'ylim':ax.get_ylim(),'points':sum(len(x.get_ydata())for x in ax.lines),'data_exact':True})
 plt.close(fig)
legend=e3.draw_legend(payload);legend.savefig(out/'config-legend.pdf');plt.close(legend)
fig=plt.figure(figsize=(e3.pt_to_in(e3.PANEL_PT*4),e3.pt_to_in(11)))
fig.legend(handles=[Line2D([0],[0],color='#444444',linewidth=e3.LINE_PT,linestyle=(0,(2.5,1.6)),marker='o',markerfacecolor='white',markersize=3,label='Predicted'),Line2D([0],[0],color='#444444',linewidth=e3.LINE_PT,marker='o',markersize=3,label='Reference')],loc='center',ncol=2,fontsize=6.3,frameon=False)
fig.savefig(out/'kind-legend.pdf');plt.close(fig)
assert before==hashlib.sha256(e3.SOURCE.read_bytes()).hexdigest()
(out/'data-audit.json').write_text(json.dumps({'source_sha256':before,'kind':payload['kind'],'panels':checks,'data_points':120,'limits_shared_and_unchanged':True},indent=2))
