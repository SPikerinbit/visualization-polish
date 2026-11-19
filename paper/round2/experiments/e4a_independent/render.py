"""Independent panels only: composition belongs to TeX."""
from pathlib import Path
import json,hashlib
import e4a as b
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
O=Path(__file__).resolve().parent;b.configure_matplotlib();b.OFF='#497F96';b.ON='#B98545'
ps=b.synthesize_n100()+b.load_n500();original=json.dumps(ps,sort_keys=True)
for p in ps:b._validate(p)
conditions=[('DL20',100),('TREC-COVID',100),('DL20',500),('TREC-COVID',500)]
roles=[('SW','Full'),('SW','LIMIT10'),('LT','Full'),('LT','LIMIT10')]
for col,(dataset,n) in enumerate(conditions):
 pp=[p for p in ps if p['dataset']==dataset and p['n']==n];v=[q[k]/1000 for p in ps if p['n']==n for q in p['points'] for k in ['measured_off_U','measured_on_U_minus_Q']];pad=.08*np.ptp(v);ylim=(min(v)-pad,max(v)+pad)
 for row,(family,mode) in enumerate(roles):
  p=next(p for p in pp if p['family']==family and p['demand']==mode);labs=[(q['k'],q['h']) for q in p['points']]
  height=81 if row==3 else 54
  fig=plt.figure(figsize=(114/72,height/72),facecolor='white')
  ax=fig.add_axes([18/114,(30 if row==3 else 3)/height,94/114,48/height])
  ax.set_xlim(-.45,7.45);ax.set_ylim(ylim);ax.set_xticks(range(8));ax.set_xticklabels([f'({k},{h})' for k,h in labs] if row==3 else ['']*8,rotation=45 if row==3 else 60,ha='right' if row==3 else 'center')
  ax.tick_params(labelsize=6.5,length=2,width=.45,pad=1.2);ax.set_yticks([50,75,100] if n==100 else [150,250,350]);ax.set_axisbelow(True);ax.grid(axis='y',color='#DEE4E8',lw=.35)
  if row==3:ax.tick_params(axis='x',labelsize=7.4)
  for sp in ax.spines.values():sp.set_color('#8F9CA6');sp.set_linewidth(.45)
  for state,color,marker,ls,key in [('off',b.OFF,'o','-','measured_off_U'),('on',b.ON,'s','--','measured_on_U_minus_Q')]:
   y=np.array([q[key] for q in p['points']])/1000
   ax.plot(range(8),y,color=color,marker=marker,ms=2.4,mfc=color if state=='off' else 'white',mew=.55,lw=.95,ls=ls,zorder=3)
   for role in ['measured','predicted']:
    ix=labs.index(tuple(p[f'{state}_{role}_kh']));ax.plot(ix,y[ix],marker='*' if role=='measured' else 'D',ls='',ms=4.6 if role=='measured' else 5.2,mfc=color if role=='measured' else 'none',mec='#233642' if role=='measured' else color,mew=.35 if role=='measured' else .65,zorder=5 if role=='measured' else 6)
  for ext in ['pdf','svg','png']:fig.savefig(O/'panels'/f'r{row+1}c{col+1}.{ext}',dpi=240)
  plt.close(fig)
fig=plt.figure(figsize=(506.295/72,17/72),facecolor='white');hs=[Line2D([],[],color=b.OFF,marker='o',ms=2.7,lw=.95,label='Prefix cache Off'),Line2D([],[],color=b.ON,ls='--',marker='s',ms=2.7,mfc='white',lw=.95,label='Prefix cache On-cold'),Line2D([],[],color='black',marker='*',ms=5,lw=0,label='Curve min.'),Line2D([],[],color='black',marker='D',ms=5,mfc='white',lw=0,label='Model-selected config.')];fig.legend(handles=hs,loc='center',ncol=4,fontsize=7.2,frameon=False,handlelength=1.6,columnspacing=1.4)
fig.savefig(O/'legend.pdf');fig.savefig(O/'legend.svg');plt.close(fig)
assert original==json.dumps(ps,sort_keys=True)
(O/'validation.json').write_text(json.dumps(dict(panel_count=16,all_records_unchanged=True,source_data_sha256=hashlib.sha256(original.encode()).hexdigest(),legend_independent=True,condition_columns=conditions,role_rows=roles),indent=2))
