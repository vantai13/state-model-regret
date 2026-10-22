"""Doan Van Tai — verify saved L1.8A CSV using independent scalar formulas.

No production module imports, RNG or new episodes. Decimal exp checks R2;
positive-part antiderivative checks fluid areas. This is technical verification,
not an independent scientific review or Phase3/PartB convergence experiment.
"""
import argparse
import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/l1_8_a')
    out=parser.parse_args().output_dir.resolve()
    manifest=json.loads((out/'artifact_manifest.json').read_text())
    for entry in manifest['files']:
        path=out/entry['file']
        assert path.stat().st_size==entry['size_bytes'] and sha(path)==entry['sha256'],path
    config=json.loads((out/'config.json').read_text())
    for name,digest in config['source_hashes'].items():
        assert sha(ROOT/name)==digest,name
    boundary=rows(out/'boundary_grid.csv')
    for r in boundary:
        dt,q,rate,service=(F(r[k]) for k in ('dt_s','q_start','rate_packet_s','service_packet_s'))
        v=rate-service
        end=max(0,q+v*dt)
        # Integral of positive affine function via a positive-part antiderivative.
        area=q*dt if v==0 else (end**2-q**2)/(2*v)
        d13=dt*end
        term=dt*(end-q)/2
        assert F(r['q_end'])==end and F(r['fluid_area'])==area
        assert F(r['d13'])==d13 and F(r['error'])==d13-area
        assert F(r['crossing_correction'])==d13-area-term>=0
    trips=rows(out/'round_trip_grid.csv')
    for r in trips:
        dt,seconds=F(r['dt_s']),F(r['seconds_requested'])
        n=round(seconds/dt)
        assert int(r['slots'])==n and F(r['error_s'])==n*dt-seconds
        assert abs(F(r['error_s']))<=dt/2
    persistence=rows(out/'persistence_comparison.csv')
    with localcontext() as ctx:
        ctx.prec=60
        for r in persistence:
            dt,T=F(r['dt_s']),F(r['T_mode_s'])
            n=int(r['age_slots'])
            if r['law']=='R1':
                lam=1-2*dt/T
                assert F(r['lambda_slot'])==lam and F(r['correlation'])==lam**n
            else:
                expo=Decimal(-2*dt.numerator)*Decimal(T.denominator)/(Decimal(dt.denominator)*Decimal(T.numerator))
                lam=expo.exp()
                assert math.isclose(float(lam),float(r['lambda_slot']),rel_tol=1e-12,abs_tol=1e-14)
                assert math.isclose(float(lam**n),float(r['correlation']),rel_tol=1e-12,abs_tol=1e-14)
    cards=rows(out/'anchor_cards.csv')
    assert len(cards)==2
    expected={'a':(42,F(63,12500),F(3,500)),'b':(17,F(51,250),F(3,5))}
    for c in cards:
        n,represented,drain=expected[c['anchor']]
        assert int(c['age_slots'])==n and F(c['age_represented_s'])==represented
        assert F(c['capacity_packet_slot'])==10 and F(c['T_drain_pre_B_s'])==drain
        assert F(c['z_pre_represented'])==drain/represented
    data=json.loads((out/'results.json').read_text())
    total=0
    for name,t in data['tests'].items():
        cases=list(ET.parse(out/t['junit']).iter('testcase'))
        assert len(cases)==t['total']
        assert all(c.find('failure') is None and c.find('error') is None and c.find('skipped') is None for c in cases)
        if name=='full_suite': total=len(cases)
    checked=dict(author='Doan Van Tai',status='PASS',verifier_sha256=sha(Path(__file__)),
                 existing_manifest_files_checked=len(manifest['files']),source_hashes_checked=len(config['source_hashes']),
                 boundary_rows= len(boundary),round_trip_rows=len(trips),persistence_rows=len(persistence),anchor_rows=len(cards),
                 full_suite_passed=total,methods=['Fraction positive-part antiderivative','Decimal exp precision60','CSV/JUnit/SHA256'],
                 random_draws=0)
    text=json.dumps(checked,ensure_ascii=False,indent=2)+'\n'
    (out/'independent_artifact_audit.json').write_text(text)
    (out/'independent_artifact_audit.txt').write_text(text)
    files=[dict(file=p.name,size_bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
           if p.is_file() and p.name!='artifact_manifest.json']
    (out/'artifact_manifest.json').write_text(json.dumps(dict(author='Doan Van Tai',files=files),indent=2)+'\n')
    print(text,end='')


if __name__=='__main__': main()
