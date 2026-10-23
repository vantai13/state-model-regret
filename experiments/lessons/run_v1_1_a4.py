"""Doan Van Tai — 22 main cells at two levels, persist only sign probabilities."""
from experiments.lessons.v1_1_a_common import *
from experiments.lessons.run_v1_1_a2 import common_unit
from smr.gap_screen import backward,probability_interval
from smr.stationary import r2_keep
import numpy as np,time,resource,subprocess


def load_cells():
    rows=json.loads((ROOT/'notes/design/grid_v1_1_candidate.json').read_text())['cells']
    for c in rows:
        for k in ('lambdaA','kappa','eta','u','yA','yB','h','age'):c[k]=F(c[k])
        for k in ('ratesA','ratesB'):c[k]=tuple(map(F,c[k]))
    return rows


def component(c,which,ref,extended,metadata):
    path=ROOT/f'results/lessons/v1_1_a2/{c["id"]}_{ref}_{which}.npz'
    with np.load(path) as f:mass=f['mass'];support=f['support']
    entry=next(m for m in metadata if m['cell']==c['id'] and m['refinement']==ref and m['queue']==which)
    native=F(entry['unit']);unit=common_unit(c,which,ref);factor=native/unit;assert factor.denominator==1
    indices=np.arange(len(mass),dtype=np.int64)*int(factor);H=c['H_coarse']*ref;dt=F(1,120*ref)
    keep,ke=r2_keep(dt,c['kappa'])
    rates=c['rates'+which]
    stay=tuple(int((r+(c['u'] if which=='A' else 0)-10)*dt/unit) for r in rates)
    switch=tuple(int((r+(c['u'] if which=='B' else 0)-10)*dt/unit) for r in rates)
    minimal=switch if which=='A' else stay
    zero=np.column_stack([(indices+a>=0)&(indices+a+(H-1)*min(0,*minimal)>=0) for a in minimal])
    if np.all(zero[support]):
        return np.zeros(mass.shape,dtype=np.longdouble),mass,0.,float(entry['TV_error']),zero.ravel()
    a,ea,_=backward(indices,stay,H,keep,ke,extended)
    b,eb,_=backward(indices,switch,H,keep,ke,extended)
    scale=np.longdouble(str((unit*dt).numerator))/np.longdouble(str((unit*dt).denominator))
    value=(b.astype(np.longdouble)-a.astype(np.longdouble))*scale
    error=(ea+eb)*float(scale)+float(16*np.finfo(np.longdouble).eps*scale*(np.max(a)+np.max(b)))
    assert np.all(value[zero]==0),'nonidle certificate violated'
    if which=='A':assert np.min(value)>=-error
    else:assert np.max(value)<=error
    return value,mass,error,float(entry['TV_error']),zero.ravel()


def screen(c,ref,extended,metadata):
    A,pa,ea,da,za=component(c,'A',ref,extended,metadata)
    B,pb,eb,db,zb=component(c,'B',ref,extended,metadata)
    result=probability_interval(A,B,pa,pb,ea,eb,da+db,za,zb)
    # No per-state fields leave this function or get serialized.
    return result


def run():
    out=ROOT/'results/lessons/v1_1_a4';out.mkdir(parents=True,exist_ok=True)
    metadata=json.loads((ROOT/'results/lessons/v1_1_a2/supports.json').read_text())
    cells=[c for c in load_cells() if c['role']=='main'];assert len(cells)==22
    write(out/'config.json',dict(author='Doan Van Tai',candidate_commit='571d4cf',screen_parent=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        acceptance=[.1,.9],required_in=15,levels=[1,2],no_margin_output=True,no_Lstar=True,reserve_screened=False,seed=None))
    rows=[]
    for c in cells:
        for ref in (1,2):
            target=out/f'{c["id"]}_{ref}.json'
            if target.exists():
                row=json.loads(target.read_text());rows.append(row);continue
            start=time.monotonic();r=screen(c,ref,False,metadata);initial=r.copy();extended=r['unresolved_mass']>.01
            if extended:r=screen(c,ref,True,metadata)
            if r['unresolved_mass']>.01:label='HOLD_PRECISION'
            elif r['p_low']>=.1 and r['p_high']<=.9:label='in'
            elif r['p_high']<.1 or r['p_low']>.9:label='out'
            else:label='unstable'
            row=dict(cell=c['id'],refinement=ref,dt=str(F(1,120*ref)),**r,classification=label,
                extended=extended,initial_unresolved_mass=initial['unresolved_mass'],wall_s=time.monotonic()-start,
                peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
            assert row['peak_rss_bytes']<=4*1024**3
            write(target,row);rows.append(row)
            print(f"B3 {c['id']} /{ref}: [{r['p_low']:.9f},{r['p_high']:.9f}] {label} unresolved={r['unresolved_mass']:.3g} {row['wall_s']:.2f}s",flush=True)
    csvwrite(out/'screen.csv',rows);manifest(out)
if __name__=='__main__':run()
