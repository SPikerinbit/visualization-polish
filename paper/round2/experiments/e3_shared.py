"""Grouped E3 variant only. Standalone e3.py output retains every axis label."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import e3

def build(out):
 e3.configure_matplotlib();payload=e3.load();ylim=e3._ylim(payload);by={(p['family'],p['mode']):p for p in payload['panels']};checks=[]
 for kind in ['predicted','measured']:
  for col,(family,mode) in enumerate([('SW','Full'),('SW','LIMIT10'),('LT','Full'),('LT','LIMIT10')]):
   fig=e3.draw_panel(by[family,mode],kind,ylim,0 if family=='SW' else 5);ax=fig.axes[0]
   before=[l.get_xydata().copy() for l in ax.lines];xr=ax.get_xlim();yr=ax.get_ylim()
   ax.tick_params(labelsize=7.0,labelleft=col==0,labelbottom=kind=='measured')
   if kind=='predicted':
    ax.set_xlabel('')
    fig.set_size_inches(e3.pt_to_in(e3.PANEL_PT),e3.pt_to_in(52))
    ax.set_position([0.205,(0.235*62-10)/52,0.755,0.725*62/52])
   else:ax.xaxis.label.set_fontsize(6.2)
   # Rebalance 1.5bp of the existing left margin to the right; retain true centered ticks.
   box=ax.get_position();ax.set_position([box.x0-1.5/e3.PANEL_PT,box.y0,box.width,box.height])
   for a,b in zip(before,ax.lines):np.testing.assert_array_equal(a,b.get_xydata())
   assert xr==ax.get_xlim() and yr==ax.get_ylim()
   problems=e3.overflow_labels(fig)+e3.overlapping_tick_labels(fig)
   if problems:raise RuntimeError(problems)
   stem=f'e3-{family.lower()}-{mode.lower()}-{kind}-shared'
   for ext in ['pdf','svg','png']:fig.savefig(out/(stem+'.'+ext),dpi=300)
   checks.append(dict(panel=stem,y_values=sum(len(l.get_ydata()) for l in ax.lines),tick_font=7.0,show_y=col==0,show_x=kind=='measured',data_exact=True,xlim=xr,ylim=yr))
   plt.close(fig)
 (out/'e3-shared-verification.json').write_text(json.dumps(checks,indent=2))
if __name__=='__main__':build(Path(__file__).parent/'figures/e3')
