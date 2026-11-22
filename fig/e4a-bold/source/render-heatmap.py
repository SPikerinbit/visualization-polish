from pathlib import Path
from collections import defaultdict
from itertools import product
import os, csv, html, subprocess, math, json, hashlib

P=Path(__file__).resolve().parent
source=P/'legal-targets.csv'
groups=defaultdict(set)
for r in csv.DictReader(source.open()):
    assert (r['n'],r['m'])==('500','20')
    groups[tuple(r[x] for x in ('algorithm','demand','dataset','cache_state'))].add((int(r['k']),int(r['h'])))
assert len(groups)==16
FAMILIES=['sliding_window','loser_tree']; MODES=['Full','LIMIT10']
ALL_MASKS={(f,d):set.intersection(*(g for (a,b,*_),g in groups.items() if (a,b)==(f,d))) for f,d in product(FAMILIES,MODES)}
W=240.24655
STYLE=os.environ.get('HEATMAP_STYLE','prism')
ANCHORS={
  'prism':['#233C73','#557EB5','#ACC7DD','#F7F7F4','#F2C4AA','#D5785F','#8F302B'],
  'oxide':['#863B33','#CC7867','#F1C8B4','#F7F7F4','#A8C8B7','#4C846A','#225B49'],
}[STYLE]
def rgb(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
def color(v):
    x=max(0,min(5.9999,(v+30)/10));i=int(x);t=x-i
    return '#'+''.join(f'{round(a+(b-a)*t):02x}' for a,b in zip(rgb(ANCHORS[i]),rgb(ANCHORS[i+1])))
def dummy(k,h,a,d):
    # Identical for any shared key across variants. No input files beyond legal domain.
    t=(k-2)/8;r=h-1
    return 14*math.sin(4.2*t+.85*r+.85*a+.45*d)+8*math.cos(5.6*t-1.25*r+1.3*d)+(-4+8*a-5*d)+4*r
def render(nh,nk):
    parts=[]
    def tag(t,props,s=None):
        attrs=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in props.items())
        parts.append(f'<{t} {attrs}/>' if s is None else f'<{t} {attrs}>{html.escape(s)}</{t}>')
    def rect(x,y,w,h,fill,stroke='none',sw=0):tag('rect',dict(x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=sw))
    def txt(x,y,s,size=8,w='normal',a='start',color='#24292f',style='normal'):
        tag('text',dict(x=x,y=y,font_size=size,font_weight=w,text_anchor=a,fill=color,font_style=style),s)
    def ln(x,y,X,Y,c='#b3bbc4',w=.45):tag('line',dict(x1=x,y1=y,x2=X,y2=Y,stroke=c,stroke_width=w))
    K=range(2,nk+2);H=range(1,nh+1); keys=set(product(K,H)); masks={x:m&keys for x,m in ALL_MASKS.items()}
    cw=98/nk;ch=7.4; grid_h=nh*ch; rowH=grid_h+18.9; last=11+2*rowH; height=last+4
    rect(0,0,W,height,'white')
    parts.append('<defs><pattern id="invalid" width="3.3" height="3.3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3.3" height="3.3" fill="#F0F2F4"/><path d="M0 0V3.3" stroke="#C7CED6" stroke-width=".48"/></pattern></defs>')
    records=[]
    for d,name in enumerate(['Full','LIMIT 10']):
        y=11+d*rowH
        txt(0,y+4.5,name,7.7,'bold',color='#233044')
        for a,lab in enumerate(['SW','LT']):
            x=13+a*103.0; y0=y+8.65
            txt(x+49,y+4.5,lab,7.25,'bold','middle','#28384c')
            for i,h in enumerate(reversed(H)):
                if a==0:txt(x-2.8,y0+ch*(i+.76),str(h),6.05,'normal','end')
                for j,k in enumerate(K):
                    feasible=(k,h) in masks[FAMILIES[a],MODES[d]]
                    v=dummy(k,h,a,d) if feasible else None
                    fill=color(v) if feasible else 'url(#invalid)'
                    rect(round(x+j*cw,4),round(y0+i*ch,4),cw-.34,ch-.34,fill)
                    records.append([FAMILIES[a],MODES[d],k,h,feasible,v,fill])
            rect(x-.22,y0-.22,98.12,grid_h+.12,'none','#777f89',.45)
            for j,k in enumerate(K):
                t=x+(j+.5)*cw
                txt(t,y0+grid_h+7.15,str(k),6.05,'normal','middle')
                ln(t,y0+grid_h,t,y0+grid_h+1.5,'#616976',.48)
            if a==0:txt(x-5.6,y0+grid_h+7.15,'k',6.55,style='italic')
            if a==0:txt(2.8,y0+4.1,'h',6.55,style='italic')
    bar_h=72; top=31.5
    tag('text',dict(x=0,y=0,transform=f'translate(238.5 {top+bar_h/2}) rotate(-90)',text_anchor='middle',font_size=6.05,font_weight='bold',fill='#24292f'),'Savings (%)')
    stops=''.join(f'<stop offset="{i/6}" stop-color="{c}"/>' for i,c in enumerate(reversed(ANCHORS)))
    parts.append('<defs><linearGradient id="scale" x1="0%" y1="0%" x2="0%" y2="100%">'+stops+'</linearGradient></defs>')
    rect(218.3,top,5.25,bar_h,'url(#scale)');rect(218.3,top,5.25,bar_h,'none','#717988',.45)
    for frac,s in [(0,'≥+30'),(.25,'+15'),(.5,'0'),(.75,'−15'),(1,'≤−30')]:
        y=top+bar_h*frac
        ln(223.55,y,224.15,y,'#515861',.48);txt(224.65,y+1.8,s,5.35,color='#2D3741')
    rect(218.3,113,5.25,5.25,'url(#invalid)','#838f9d',.45)
    txt(218.3,124.1,'Infeasible',5.45,color='#3b4652')
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{height-8.3}pt" viewBox="0 8.3 {W} {height-8.3}"><g font-family="TeX Gyre Termes,Liberation Serif,serif">'+''.join(parts)+'</g></svg>'
    stem=P/'E4a-key-beside'
    stem.with_suffix('.svg').write_text(s)
    for ext in ('pdf','png'):
        cmd=['inkscape',str(stem.with_suffix('.svg')),'--export-filename='+str(stem.with_suffix('.'+ext))]
        if ext=='png':cmd+=['--export-width=1200']
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    # Independent vector crop assets, placed at exact native sizes by TeX.
    tiles=P/'fig/e4a-key-beside'/f'{nh}x{nk}'
    tiles.mkdir(parents=True,exist_ok=True)
    rowcut=11+rowH-1.35
    cps={
        'full-sw':(0,8.3,113,rowcut-8.3), 'full-lt':(113,8.3,103,rowcut-8.3),
        'limit-sw':(0,rowcut,113,height-rowcut), 'limit-lt':(113,rowcut,103,height-rowcut),
        'key':(216,8.3,W-216,height-8.3),
    }
    body=s[s.index('><g')+1:]
    for name,(x,y,ww,hh) in cps.items():
        c=f'<svg xmlns="http://www.w3.org/2000/svg" width="{ww}pt" height="{hh}pt" viewBox="{x} {y} {ww} {hh}">'+body
        asset=tiles/name
        asset.with_suffix('.svg').write_text(c)
        subprocess.run(['inkscape',str(asset.with_suffix('.svg')),'--export-filename='+str(asset.with_suffix('.pdf'))],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    glue=P/f'combine-{nh}x{nk}.tex'
    texpath=f'fig/e4a-key-beside/{nh}x{nk}'
    def include(n):
        return r'\includegraphics{'+texpath+'/'+n+'.pdf}'
    glue.write_text(r'% Exact native placement of four vector panels, a shared color and feasibility key.'+'\n'
                    +r'\leavevmode\vbox{\offinterlineskip'+'\n'
                    +r'\hbox{\vbox{\offinterlineskip'+'\n'
                    +r'\hbox{'+include('full-sw')+include('full-lt')+'}\n'
                    +r'\hbox{'+include('limit-sw')+include('limit-lt')+'}\n'
                    +'}'+include('key')+'}}\n')
    return {'tiles':cps,'name':f'{nh}x{nk}' ,'w_bp':W,'h_bp':height-8.3,'k':list(K),'h':list(H),'cells':records,'counts':{f'{f}|{d}':len(m) for (f,d),m in masks.items()}}
variants=[render(6,10)]
overlap={}
for var in variants:
    for row in var['cells']:
        key=tuple(row[:4]);val=row[4:]
        if key in overlap:assert overlap[key]==val
        overlap[key]=val
(P/'audit.json').write_text(json.dumps({'status':'all values simulated; no measurements shown','range_pct':[-30,30], 'legal_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'same_synthetic_function_on_overlaps':True,'variants':variants},indent=2)+'\n')
for v in variants: print(v['name'],v['w_bp'],v['h_bp'],v['counts'])
