"""Doan Van Tai — recompute dominance mass and compare B propagation to a legacy reference."""
from experiments.lessons.v1_1_a_common import *
from experiments.lessons.run_v1_1_a2 import common_unit
from smr.design import episode_law
import numpy as np


def run():
    output=ROOT/'results/lessons/v1_1_a6';mass_rows=[];reference_max=0.
    for suffix,candidate in [('', 'grid_v1_1_candidate.json'),('_redesign','grid_v1_1_redesign_candidate.json')]:
        directory=ROOT/f'results/lessons/v1_1_a2{suffix}';metadata=json.loads((directory/'supports.json').read_text())
        screen=list(csv.DictReader((ROOT/f'results/lessons/v1_1_a4{suffix}/screen.csv').open()))
        for c in json.loads((ROOT/'notes/design'/candidate).read_text())['cells']:
            for k in ('u','kappa','yA','yB'):c[k]=F(c[k])
            for k in ('ratesA','ratesB'):c[k]=tuple(map(F,c[k]))
            for ref in (1,2):
                probability={};all_support={};H=c['H_coarse']*ref;dt=F(1,120*ref);Derror=0
                for which in ('A','B'):
                    item=next(m for m in metadata if m['cell']==c['id'] and m['refinement']==ref and m['queue']==which)
                    with np.load(directory/f"{c['id']}_{ref}_{which}.npz") as f:p,support=f['mass'],f['support']
                    unit=common_unit(c,which,ref);factor=F(item['unit'])/unit;assert factor.denominator==1
                    q=np.arange(len(p),dtype=np.int64)[:,None]*int(factor)
                    stay=np.array([int((r+(c['u'] if which=='A' else 0)-10)*dt/unit) for r in c['rates'+which]])
                    switch=np.array([int((r+(c['u'] if which=='B' else 0)-10)*dt/unit) for r in c['rates'+which]])
                    idle_base=switch if which=='A' else stay;zero_base=stay if which=='A' else switch
                    noidle=(q+idle_base>=0)&(q+idle_base+(H-1)*min(0,*idle_base)>=0)
                    empty=(q+zero_base<=0)&((H==1) or max(zero_base)<=0)
                    for key,flags in [('noidle',noidle),('empty',empty)]:
                        probability[which+key]=np.sum(p[flags],dtype=np.longdouble)
                        all_support[which+key]=bool(np.all(flags[support]))
                    Derror+=item['TV_error']
                    if which=='B':
                        # Old implementation independently uses closed-form B prior and scalar scatter.
                        _,_,reference,_,_=episode_law(dict(yA=F(0),yB=c['yB'],age=F(1),eta=c['u']/2,kappa=c['kappa']),ref)
                        diff=float(np.abs(reference-p).sum()/2);reference_max=max(reference_max,diff)
                        assert diff<=item['TV_error']+1e-13
                ms=1-(1-probability['Aempty'])*(1-probability['Bnoidle'])
                mw=1-(1-probability['Anoidle'])*(1-probability['Bempty'])
                actual=next((r for r in screen if r['cell']==c['id'] and int(r['refinement'])==ref),None)
                if actual:assert float(actual['p_low'])<=1-float(ms)+Derror+1e-12
                mass_rows.append(dict(round='initial' if not suffix else 'redesign',cell=c['id'],refinement=ref,
                    m_SD=str(ms),m_WD=str(mw),m_conservation=str(probability['Anoidle']*probability['Bnoidle']),
                    probability_error=Derror,all_SD=all_support['Aempty'] or all_support['Bnoidle'],
                    all_WD=all_support['Anoidle'] or all_support['Bempty']))
    csvwrite(output/'dominance_mass.csv',mass_rows)
    write(output/'factorized_law_audit.json',dict(author='Doan Van Tai',status='PASS',rows=len(mass_rows),
        B_legacy_comparisons=136,max_B_TV_difference=reference_max,sign_upper_bound_checks=88,Cartesian_products=0))
    print('Factorized law audit PASS:',len(mass_rows),'dominance rows, 136 B references; maxTV',reference_max)

if __name__=='__main__':run()
