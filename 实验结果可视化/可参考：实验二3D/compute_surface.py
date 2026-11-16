"""Price the current production MC estimator against the frozen real Full LT grid."""
from pathlib import Path
import csv, json, sys, hashlib, subprocess, time, sqlite3
from concurrent.futures import ProcessPoolExecutor

ROOT=Path(__file__).resolve().parent
DATA=Path('C:/Users/omen/Desktop/项目组/2026-10-23/build/update_v1/data')
REPO=Path('D:/SemaPrototype')
COND='condition_251252d515c1ab241784d189a2ad88e884fe7f19ec199d180cb8245a2f55fee4'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def worker(job):
    slot, rows=job
    sys.path.insert(0,str(REPO))
    from sema_prototype.physical_operator.orderby.merge._shared.plan import estimate_cost, InputTokenProfile
    cache=ROOT/'mc_cache'/str(slot);cache.mkdir(parents=True,exist_ok=True)
    source=Path.home()/'.cache/sema_prototype/orderby_finite/finite_workloads_v2.sqlite3'
    dest=cache/source.name
    if not dest.exists() and source.exists():
        with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as a, sqlite3.connect(dest) as b:a.backup(b)
    output=[]
    for r in rows:
        t=time.perf_counter();k,h=int(r['k']),int(r['h'])
        profile=InputTokenProfile(float(r['H']),float(r['L']),source='frozen_real_experiment')
        est=estimate_cost((20,)*10,'loser_tree',k,h,20,None,profile,mode='full',tail_cache_dir=str(cache))
        point=dict(k=k,h=h,U=float(r['U']),P=est.input_tokens,A_actual=float(r['A_actual']),D_actual=float(r['D_actual']),A_pred=est.total_calls,D_pred=est.total_items,H=profile.H,L=profile.L,observation_id=r['observation_id'],profile_id=r['input_token_profile_id'],condition_id=r['condition_id'],mc=est.expectation)
        (ROOT/'points').mkdir(exist_ok=True)
        (ROOT/'points'/f'k{k}_h{h}.json').write_text(json.dumps(point,indent=2),encoding='utf-8')
        output.append(point)
        print(f'({k},{h}) U={point["U"]:.0f} P={point["P"]:.1f}, {time.perf_counter()-t:.1f}s',flush=True)
    return output

if __name__=='__main__':
    with (DATA/'grid_first.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=[r for r in csv.DictReader(f) if r['condition_id']==COND and r['family']=='loser_tree']
    sys.path.insert(0,str(REPO))
    from sema_prototype.physical_operator.orderby.merge._shared.plan import max_segment,MODEL_VERSION
    legal={(k,h) for k in range(2,11) for h in range(1,max_segment(k,20)+1)}
    assert len(rows)==len(legal)==50 and {(int(r['k']),int(r['h'])) for r in rows}==legal
    assert len({r['condition_id'] for r in rows})==1
    assert len({(r['H'],r['L']) for r in rows})==1
    assert all(r['qualified_complete']=='True' and r['usage_missing_count']=='0' for r in rows)
    with ProcessPoolExecutor(max_workers=4) as pool:
        batches=list(pool.map(worker,[(i,rows[i::4]) for i in range(4)]))
    points=sorted([r for b in batches for r in b],key=lambda r:(r['k'],r['h']))
    best=min(points,key=lambda r:r['U']);chosen=min(points,key=lambda r:r['P'])
    manifest=dict(n=200,m=20,mode='Full',family='LT',query_id='1030303',partition='contiguous',seed=0,model='Qwen3.5-9B',model_version=MODEL_VERSION,mc_samples=16384,mc_seed=2410000,code_commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),files={str(p):sha(p) for p in [DATA/'grid_first.csv',REPO/'sema_prototype/physical_operator/orderby/merge/_shared/plan.py',REPO/'sema_prototype/physical_operator/orderby/merge/_shared/finite.py',REPO/'sema_prototype/physical_operator/orderby/merge/_shared/tail.py']},actual_min=best,model_choice=chosen,selection_regret=chosen['U']/best['U']-1,points=points)
    (ROOT/'surface_data.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    keys=['k','h','U','P','A_actual','D_actual','A_pred','D_pred','H','L','observation_id']
    with (ROOT/'surface_data.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(points)
    print('COMPLETE',json.dumps({k:manifest[k] for k in ['model_version','selection_regret']},ensure_ascii=False),flush=True)
