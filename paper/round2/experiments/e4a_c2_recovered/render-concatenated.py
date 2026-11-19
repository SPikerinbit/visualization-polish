"""C2+guides reconstructed from captured source, not rejected hollow/direct-label variants."""
from pathlib import Path
import json,hashlib
import e4a as b
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
O=Path(__file__).resolve().parent;OUT=O/'joined-panels';OUT.mkdir(exist_ok=True);b.configure_matplotlib();b.OFF='#497F96';b.ON='#B98545'
ps=b.synthesize_n100()+b.load_n500();original=json.dumps(ps,sort_keys=True)
for p in ps:b._validate(p)
roles=[('SW','Full'),('SW','LIMIT10'),('LT','Full'),('LT','LIMIT10')];audit=[]
for n in [100,500]:
 vals=[q[k]/1000 for p in ps if p['n']==n for q in p['points'] for k in ['measured_off_U','measured_on_U_minus_Q']];pad=.08*np.ptp(vals);ylim=(min(vals)-pad,max(vals)+pad)
 for row,(family,mode) in enumerate(roles):
  last=row==3;H=60 if last else 40;fig=plt.figure(figsize=(118/72,H/72),facecolor='white');ax=fig.add_axes([19/118,(23 if last else 3)/H,97/118,34/H]);ax.set_xlim(-.45,16.45);ax.set_ylim(ylim);ax.set_yticks([50,75,100] if n==100 else [150,250,350]);ax.set_axisbelow(True);ax.grid(axis='y',color='#DEE4E8',lw=.35)
  ax.axvline(8,color='#C5CBD0',lw=.5,ls=(0,(2,2)),zorder=1)
  xticks=[];labels=[];entry={'n':n,'family':family,'mode':mode,'ylim':list(ylim),'yticks':list(ax.get_yticks()),'segments':[]}
  for dataset,offset in [('DL20',0),('TREC-COVID',9)]:
   p=next(p for p in ps if p['n']==n and p['dataset']==dataset and p['family']==family and p['demand']==mode);labs=[(q['k'],q['h'])for q in p['points']];xs=np.arange(8)+offset;xticks.extend(xs.tolist());labels.extend([f'({k},{h})'for k,h in labs]);seg={'dataset':dataset,'x':xs.tolist(),'labels':labs,'series':{}}
   for state,color,marker,ls,key in [('off',b.OFF,'o','-','measured_off_U'),('on',b.ON,'s','--','measured_on_U_minus_Q')]:
    y=np.array([q[key]for q in p['points']])/1000;ax.plot(xs,y,color=color,marker=marker,ms=2.4,mfc=color if state=='off' else 'white',mew=.55,lw=.95,ls=ls,zorder=3);seg['series'][state]={'y':y.tolist(),'highlights':{}}
    for role in ['measured','predicted']:
     ix=labs.index(tuple(p[f'{state}_{role}_kh']));ax.plot(xs[ix],y[ix],marker='*'if role=='measured'else'D',ls='',ms=4.6 if role=='measured'else 5.2,mfc=color if role=='measured'else'none',mec='#233642'if role=='measured'else color,mew=.35 if role=='measured'else .65,zorder=5 if role=='measured'else 6,clip_on=False);seg['series'][state]['highlights'][role]={'x':int(xs[ix]),'y':float(y[ix]),'kh':labs[ix]}
   entry['segments'].append(seg)
  ax.set_xticks(xticks);ax.set_xticklabels(['']*16);ax.tick_params(labelsize=6.5,length=2,width=.45,pad=1.2)
  if last:
   for x,label in zip(xticks,labels):
    compact=label
    ax.annotate(compact,(x,0),xycoords=ax.get_xaxis_transform(),xytext=(0,-3),textcoords='offset points',fontsize=6.0,rotation=90,ha='center',va='top',annotation_clip=False)
   fig.set_dpi(576);fig.canvas.draw()
   bb=[t.get_window_extent() for t in ax.texts]
   gaps=[(bb[i+1].x0-bb[i].x1)*72/fig.dpi for i in range(len(bb)-1)]
   assert min(gaps)>0, gaps
   entry['tick_texts']=[t.get_text() for t in ax.texts];entry['min_label_gap_bp']=min(gaps)
  fig.text(3.3/118,((23 if last else 3)+17)/H,'Tok. ×10³',rotation=90,fontsize=5.0,ha='center',va='center')
  for sp in ax.spines.values():sp.set_color('#8F9CA6');sp.set_linewidth(.45)
  curves=[l for l in ax.lines if len(l.get_xdata())==8];assert len(curves)==4
  assert all(max(l.get_xdata())<8 or min(l.get_xdata())>8 for l in curves)
  entry['plot_size_bp']=[97,34];entry['separate_curve_count']=4;audit.append(entry)
  for ext in ['pdf','svg']:fig.savefig(OUT/f'n{n}-r{row+1}.{ext}')
  plt.close(fig)
fig=plt.figure(figsize=(240.24655/72,14/72));hs=[Line2D([],[],color=b.OFF,marker='o',ms=2.7,lw=.95,label='Cache Off'),Line2D([],[],color=b.ON,ls='--',marker='s',ms=2.7,mfc='white',lw=.95,label='On-cold'),Line2D([],[],color='black',marker='*',ms=5,lw=0,label='Min.'),Line2D([],[],color='black',marker='D',ms=5,mfc='white',lw=0,label='Model-selected')];fig.legend(handles=hs,loc='center',ncol=4,fontsize=6.3,frameon=False,handlelength=1.1,columnspacing=0.8);fig.savefig(O/'joined-legend.pdf');plt.close(fig)
assert original==json.dumps(ps,sort_keys=True);(O/'joined-audit.json').write_text(json.dumps({'source_hash':hashlib.sha256(original.encode()).hexdigest(),'panels':audit},indent=2,default=float))
