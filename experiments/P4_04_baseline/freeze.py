"""Create a write-once prereg from the author-approved spec before plant calls."""
from fractions import Fraction as F

from .common import ROOT,HERE,OUT,LEVELS,RHOS,INVENTORY,SEALED,load,plan,sha,require,write_once,guard_case


def main():
    require(not (ROOT/OUT/'native').exists() and not (ROOT/OUT/'controls').exists(), 'plant output already exists')
    require(load(HERE/'author_choices.json')['status']=='ADOPTED_BY_AUTHOR_CHOICE','author choice missing')
    cases=plan()['cases']
    require(len(cases)==90,'scope changed')
    for case in cases:guard_case(case)
    benchmark=[]
    for region,count in [('MV+A',18),('SH+A',72)]:
        group=[c for c in cases if region in c['regions']]
        require(len(group)==count,'region count changed')
        benchmark += [group[0]['id'],group[-1]['id']]
    parameters=['7','6','1/10','0','8','0']
    from .common import canonical
    control=dict(id='P44_CONTROL_U0',parameters=parameters,key=list(canonical(parameters)),
                 aliases=[],regions=[],purpose='exact zero-action plant sanity; not discovery or CF')
    guard_case(control,control=True)
    from experiments.P4_03_map_audit.common import verify_prereg as verify_frozen
    verify_frozen()
    paths=[p for p in (ROOT/HERE).glob('*') if p.is_file() and p.name!='prereg.json']
    paths += list((ROOT/'tests').glob('test_p4_04*.py'))
    paths += [ROOT/INVENTORY,ROOT/SEALED,ROOT/'notes/phases/PHASE_4_entry_decision.md',
              ROOT/'notes/phases/PHASE_3R_hypothesis_cards_v2.md',
              ROOT/OUT/'input_manifest.json',*list((ROOT/OUT/'inputs').glob('*.md'))]
    cfg=dict(responsible='Doan Van Tai',status='FROZEN_BEFORE_PLANT_BASELINE',
             author_choice=str(HERE/'author_choices.json'),spec=str(HERE/'spec.md'),
             rho=list(RHOS),levels=[list(v) for v in LEVELS],benchmark_ids=benchmark,control=control,
             workers=2,case_cpu_seconds=1800,case_wall_seconds=2400,cpu_cap_hours=8,
             CF_computed=False,card_v2_verdict_unchanged=True,
             source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)})
    write_once(ROOT/HERE/'prereg.json',cfg)
    print('Frozen before plant:90 discovery cases,1 zero-action control, benchmark',benchmark,flush=True)


if __name__=='__main__':main()
