"""Evaluate the preregistered resource rule from completed benchmark timings only."""
from fractions import Fraction as F
import json

from .common import ROOT,HERE,OUT,require,write_once


def main():
    cfg=json.loads((ROOT/HERE/'prereg.json').read_text())
    benchmark=json.loads((ROOT/OUT/'benchmark_summary.json').read_text())
    require(benchmark['status']=='PASS' and benchmark['completed']==4,'four successful benchmark cases required')
    plan=json.loads((ROOT/HERE/'cases.json').read_text())
    pieces={}
    for zone in ('A','AB'):
        keys={a['native_id'] for a in plan['aliases'] if zone in a['zones']}
        times=[F(str(r['cpu_seconds'])) for r in benchmark['results'] if r['native_id'] in keys]
        require(bool(times),'benchmark must cover both zones')
        pieces[zone]=dict(distinct=len(keys),max_measured_bundle_cpu_seconds=float(max(times)),
                          estimated_cpu_seconds=float(F(3,2)*max(times)*len(keys)))
    partA=json.loads((ROOT/OUT/'partA/summary.json').read_text())
    known_cpu=sum(F(str(r.get('cpu_seconds',0))) for r in partA['results'])+F(str(benchmark['cpu_seconds']))
    estimate=known_cpu+sum(F(str(r['estimated_cpu_seconds'])) for r in pieces.values())
    limit=3600*cfg['resource_cap_cpu_hours']
    write_once(ROOT/OUT/'budget.json',dict(responsible='Doan Van Tai',rule='prereg.md ae174d0; resource only',
                 status='AUTHORIZED_BY_PREREG_RULE' if estimate<=limit else 'HOLD_BUDGET',
                 estimated_cpu_hours=float(estimate/3600),cap_cpu_hours=cfg['resource_cap_cpu_hours'],
                 known_completed_cpu_seconds=float(known_cpu),pieces=pieces,
                 interrupted_unfinished_replay_cpu='not finalized; not included in completed-call estimate',
                 no_CF_outcomes=True,limitations='Four measurements are not a population p95; estimate can under/overstate full runtime'))
    print(json.dumps(json.loads((ROOT/OUT/'budget.json').read_text()),indent=2))


if __name__=='__main__':main()
