"""Doan Van Tai — candidate cells, factorized D/support certificates and budgets; no J."""
from experiments.lessons.v1_1_a_common import *
import numpy as np
from smr.stationary import r2_keep
from smr.dominance import can_idle_within,empty_after_every_slot


def cells(redesign=False):
    result=[]
    center=F(36,5) if redesign else F(15,2)
    levels=(F(7),F(36,5),F(81,10)) if redesign else (F(13,2),F(15,2),F(17,2))
    def make(id,role,lam=None,k=F(1),eta=F(1,2),a=F(9,10),b=F(1,2),rh=F(1),**overrides):
        if lam is None:lam=center
        if 'ratesA' in overrides:lam=sum(overrides['ratesA'])/2
        if 'yA' in overrides:yA=overrides['yA']
        else:
            unit,A=law_for(lam,2*eta,k,1);yA=A.quantile(a)*unit
        ub,B=law_for(F(8),F(0),k,1)
        yB=overrides.get('yB',B.quantile(b)*ub)
        h=overrides.get('h',rh*yB/(2-2*eta) if eta<1 else yB/2)
        H=math.ceil(h*120)
        result.append(dict(id=id,role=role,lambdaA=lam,kappa=k,eta=eta,u=2*eta,
            ratesA=overrides.get('ratesA',(lam-6,lam+6)),ratesB=(F(2),F(14)),
            alphaA=a,alphaB=b,yA=yA,yB=yB,r_h=rh,target_h=h,H_coarse=H,h=F(H,120),
            rounding_error=F(H,120)-h,zA=yA/(10-lam-2*eta),zB=yB/2,
            drain_B_post=None if eta>=1 else yB/(2-2*eta),age=F(1)))
    for lam,k,ab in __import__('itertools').product(levels,(F(3,10),F(1),F(3)),(F(1,2),F(9,10))):
        make(f'M{len(result)+1:02}','main',lam,k,b=ab)
    make('M19','main',a=F(1,2));make('M20','main',rh=F(1,2));make('M21','main',rh=F(3));make('M22','main',eta=F(9,10))
    make('N01','negative',lam=F(15,2),yA=F(0),ratesA=(F(4),F(4)),h=F(1,4))
    make('N02','negative',lam=F(15,2),yA=F(0),yB=F(100),h=F(1,4))
    make('N03','negative',lam=F(15,2),yA=F(100),yB=F(100),h=F(1,4))
    make('N04','negative',lam=F(15,2),yA=F(200),yB=F(200),h=F(1,2))
    make('W01','wd_probe',lam=F(15,2),yA=F(100),yB=F(0),h=F(1,4))
    make('S01','stress',lam=F(13,2),eta=F(3,2))
    for lam,k in __import__('itertools').product((F(7),F(8)),(F(3,5),F(2),F(4))):
        make(f'R{len(result)-27:02}','reserve_extrapolation' if k==4 else 'reserve',lam,k,b=F(3,4))
    return result


def queue_D(cell,which,ref):
    rates=tuple(cell['rates'+which]);u=cell['u'] if which=='A' else F(0);dt=F(1,120*ref)
    unit,inc=lattice(rates,u,dt);index=cell['y'+which]/unit
    if index.denominator!=1:raise ValueError('observation outside stationary sublattice')
    index=int(index);tau=120*ref;s,e=r2_keep(dt,cell['kappa'])
    if max(inc)<=0:
        if index!=0:raise ValueError('impossible stationary observation for draining deterministic queue')
        prior,bound=.5,0.
    else:
        _,law=law_for(sum(rates)/2,u,cell['kappa'],ref);prior,bound=law.posterior(index)
    size=index+tau*max(0,*inc)+1
    mass=np.zeros((size,2),dtype=np.longdouble);support=np.zeros((size,2),dtype=bool)
    mass[index]=1-np.longdouble(prior),np.longdouble(prior);support[index]=True
    p=np.longdouble(str(s.numerator))/np.longdouble(str(s.denominator))
    for _ in range(tau):
        after=np.zeros_like(mass);active=np.zeros_like(support)
        for m,a in enumerate(inc):
            if a<0:
                after[0]+=mass[:min(-a+1,size),m].sum(dtype=np.longdouble)*np.array([p if m==0 else 1-p,p if m==1 else 1-p])
                active[0]|=np.any(support[:min(-a+1,size),m])
                source=mass[-a+1:,m];reach=support[-a+1:,m];dest=slice(1,size+a)
            elif a>0:
                source=mass[:-a,m];reach=support[:-a,m];dest=slice(a,None)
                assert not np.any(support[-a:,m])
            else:source=mass[:,m];reach=support[:,m];dest=slice(None)
            for mode in (0,1):
                after[dest,mode]+=source*(p if m==mode else 1-p);active[dest,mode]|=reach
        mass,support=after,active
    assert not np.any(support & (mass==0)),'positive support underflow'
    total=mass.sum(dtype=np.longdouble);assert abs(total-1)<1e-12
    error=bound+float((tau*(8+2*max(map(abs,inc)))+4*size)*np.finfo(np.longdouble).eps)
    return unit,mass,support,error


def flags(cell,which,ref,unit,support):
    dt=F(1,120*ref);rates={m:cell['rates'+which][m]*dt for m in (0,1)};u=cell['u']*dt;H=cell['H_coarse']*ref
    q,m=np.nonzero(support);none_idle=[];empty=[]
    for i,j in zip(q,m):
        none_idle.append(not can_idle_within(int(i)*unit,int(j),rates,F(0),10*dt,H))
        empty.append(empty_after_every_slot(int(i)*unit,int(j),rates,u,10*dt,H))
    return bool(all(none_idle)),bool(all(empty))


def common_unit(cell,which,ref):
    dt=F(1,120*ref);rates=cell['rates'+which]
    vals=[(r+u-10)*dt for r in rates for u in (F(0),cell['u'])]
    vals.append(cell['y'+which]);den=math.lcm(*(v.denominator for v in vals))
    return F(math.gcd(*(int(v*den) for v in vals)),den)


def run(redesign=False):
    out=ROOT/('results/lessons/v1_1_a2_redesign' if redesign else 'results/lessons/v1_1_a2');out.mkdir(parents=True,exist_ok=True)
    if (out/'labels.csv').exists():raise SystemExit('preserve A2 evidence')
    proposed=cells(redesign);labels=[];budgets=[];metadata=[]
    write(out/'config.json',dict(author='Doan Van Tai',A01_updates_limit=2e11,RAM_limit=4*1024**3,no_J=True,cells=proposed))
    for c in proposed:
        for ref in (1,2):
            f=[]
            for which in ('A','B'):
                unit,mass,support,error=queue_D(c,which,ref);f.append(flags(c,which,ref,unit,support))
                np.savez_compressed(out/f'{c["id"]}_{ref}_{which}.npz',mass=mass,support=support)
                metadata.append(dict(cell=c['id'],refinement=ref,queue=which,unit=unit,TV_error=error,
                                     support_states=int(support.sum()),max_index=len(mass)-1,total_mass=str(mass.sum())))
            sd=f[0][1] or f[1][0];wd=f[0][0] or f[1][1]
            label='conservation-cell' if f[0][0] and f[1][0] else 'SD-cell' if sd else 'WD-cell' if wd else 'candidate'
            labels.append(dict(cell=c['id'],refinement=ref,role=c['role'],label=label,all_SD=sd,all_WD=wd))
        for ref in (1,2,4,8,16):
            updates=0;peak=0
            for which in ('A','B'):
                unit=common_unit(c,which,ref);dt=F(1,120*ref);H=c['H_coarse']*ref
                growth=max(F(0),*( (r+c['u']-10)*dt for r in c['rates'+which]))
                upper=c['y'+which]+120*ref*growth+H*growth
                drain=max(0,*(int((10-r)*dt/unit) for r in c['rates'+which]))
                N=max(math.ceil(upper/unit)+1,H*drain+1);updates+=4*N*H;peak=max(peak,N*2*8*8)
            budgets.append(dict(cell=c['id'],refinement=ref,H=c['H_coarse']*ref,scalar_updates=updates,peak_bytes=peak,
                                within_A01_budget=updates<=2e11 and peak<=4*1024**3))
        print('B2',c['id'],labels[-1]['label'],flush=True)
    write(out/'supports.json',metadata);csvwrite(out/'labels.csv',labels);csvwrite(out/'budget.csv',budgets)
    write(ROOT/('notes/design/grid_v1_1_redesign_candidate.json' if redesign else 'notes/design/grid_v1_1_candidate.json'),dict(author='Doan Van Tai',status='CANDIDATE_BEFORE_SCREEN',cells=proposed,
          outcomes_computed=False,labels=labels,budget_path=str(out.relative_to(ROOT)/'budget.csv')))
    (ROOT/('notes/design/grid_v1_1_redesign_candidate.md' if redesign else 'notes/design/grid_v1_1_candidate.md')).write_text('# Lưới ứng viên v1.1\n\nDoan Van Tai,23/10/2026. 28 ô +6 reserve, giữ observation/horizon vật lý giữa hai mức. D tách theo queue, không tích Descartes. Chưa tính J/gap/p_switch. Cấu hình đầy đủ trong JSON, support và ĐK1/budget trong results/lessons/v1_1_a2/.\n')
    manifest(out)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--redesign',action='store_true');run(p.parse_args().redesign)
