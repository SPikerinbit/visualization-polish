from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import e4b,e4c
from pdfutil import configure_matplotlib
from style import pt_to_in,COLUMN_PT
configure_matplotlib();out=Path(__file__).parent/'figures'
# E4c uses its independently reviewed generator; keep E4b unchanged below.
import subprocess, sys, shutil
src=Path(__file__).parent/'e4c_independent'
subprocess.run([sys.executable,str(src/'render.py')],check=True)
shutil.copytree(src/'panels',out/'e4c/panels',dirs_exist_ok=True)
for ext in ['pdf','svg']:shutil.copy2(src/('e4c-legend.'+ext),out/'e4c'/('e4c-legend.'+ext))
# E4b directly generated independent plot and legend; no PDF crop.
f=e4b.draw(e4b.load(),e4b.costs(e4b.load()))
for legend in list(f.legends):legend.remove()
f.set_size_inches(pt_to_in(COLUMN_PT),pt_to_in(133))
f.axes[0].set_position([.155,.24,.815,.71])
f.savefig(out/'e4b/e4b-panel.pdf');plt.close(f)
f=plt.figure(figsize=(pt_to_in(COLUMN_PT),pt_to_in(33)))
colors=['#648D9B','#507F90','#3E7185','#2D6077','#204D65'];marks=['o','s','^','v','+']
handles=[Line2D([],[],color=c,ls=ls,lw=.9,marker=m,ms=3,mfc='white',label=rf'$\beta={beta:g}$')for beta,c,ls,m in zip(e4b.BETAS,colors,e4b.LINESTYLES,marks)]
f.legend(handles=handles,loc='upper center',bbox_to_anchor=(.55,1),ncol=5,fontsize=7.2,frameon=False,handlelength=1.45,columnspacing=.9,handletextpad=.4)
roles=[Line2D([],[],color='#24495D',marker='D',ms=5.2,mfc='white',lw=0,label='Predicted config. (placeholder)'),Line2D([],[],color='#24495D',marker='*',ms=6,lw=0,label='Curve minimum')]
f.legend(handles=roles,loc='lower center',bbox_to_anchor=(.55,0),ncol=2,fontsize=7.2,frameon=False,columnspacing=1.2,handletextpad=.4)
f.savefig(out/'e4b/e4b-legend.pdf');plt.close(f)
