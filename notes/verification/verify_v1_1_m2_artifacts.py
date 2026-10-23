"""Doan Van Tai — read back mốc 2 artifacts and kill cost-subtraction mutants.

This is a fresh-process technical audit, not independent human validation.
The original run/legacy manifests are read only. Audit outputs have a separate
receipt so their creation does not rewrite the evidence from the first run.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal as D, localcontext
from fractions import Fraction as F

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/v1_1_m2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def manifest_check(directory):
    manifest = load(directory / 'artifact_manifest.json')
    for item in manifest['files']:
        path = directory / item['file']
        assert path.stat().st_size == item['size_bytes'], str(path)
        assert digest(path) == item['sha256'], str(path)
    return len(manifest['files'])


def junit(path):
    root = ET.parse(path).getroot()
    cases = list(root.iter('testcase'))
    failed = sum(any(c.tag in ('error', 'failure') for c in case) for case in cases)
    return len(cases), failed


def mutate(model,output):
    function = 'subtract_truth' if model == 'M1' else 'subtract_mean'
    test = 'truth' if model == 'M1' else 'mean'
    xml = output / f'mutant_{model}.xml'
    command = [sys.executable, '-c',
        'import sys,pytest; import smr.idle_gap as module; '
        f'from experiments.lessons.v1_1_numerics import {function}; '
        f'module.gap_from_idle=lambda state,plant,model="M1": {function}(state,plant); '
        f'sys.exit(pytest.main(["-q","tests/test_v1_1_numerics.py::test_{test}_structural_ties_and_subtraction_mutant",'
        f'"--junitxml={xml}"]))']
    environment = dict(os.environ, PYTHONPATH=f'{ROOT / "src"}:{ROOT}')
    proc = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True)
    (output / f'mutant_{model}.txt').write_text(proc.stdout + proc.stderr)
    count,failed = junit(xml)
    assert proc.returncode == 1 and count == failed == 1, proc.stdout + proc.stderr
    return dict(returncode=proc.returncode, tests=count, failed=failed, killed=True,
                command=command, source_files_modified=False)


def audit(output):
    if output.exists():
        raise SystemExit('Audit output exists; preserve it before rerunning')
    output.mkdir(parents=True)
    counts = {name:manifest_check(ROOT / 'results/lessons' / name) for name in
              ('l1_8_a','l1_8_b','l1_8_cde','l1_8_v1_1_b1','v1_1_m2')}
    config = load(OUT / 'config.json')
    assert all(digest(ROOT / p) == sha for p,sha in config['source_hashes'].items())
    assert all(digest(Path(p['path'])) == p['sha256'] for p in config['inputs'])
    assert junit(OUT / 'baseline.xml') == (154,0)
    assert junit(OUT / 'lesson.xml') == (11,0)
    assert junit(OUT / 'full_suite.xml') == (165,0)
    ties = rows(OUT / 'structural_ties.csv')
    assert len(ties) == 768
    totals = {}
    for model,count in (('M1',300),('M0',468)):
        part = [r for r in ties if r['model'] == model]
        assert len(part) == count
        assert all(F(r['idle_gap']) == 0 and r['wrong_switch_after'] == 'False' for r in part)
        before = sum(F(r['subtraction_gap']) < 0 for r in part)
        assert all((F(r['subtraction_gap']) < 0) == (r['wrong_switch_before'] == 'True') for r in part)
        totals[model] = dict(cases=count,subtraction_wrong=before,idle_wrong=0)
    result = load(OUT / 'results.json')
    assert result['N1'] == totals
    canonical = load(OUT / 'N2_lemma.json')
    assert canonical['exact_two_state_cases'] == 1875 and canonical['violations'] == 0
    assert F(canonical['canonical']['G_M']) == F(1,4)
    references = rows(OUT / 'stationary_certificates.csv')
    actual_tv = {}
    with np.load(OUT / 'stationary_reference_masses.npz') as arrays:
        for row in references:
            case = row['case']; mass = arrays[f'case_{case}']
            assert len(mass) == int(row['cutoff']) + 1
            assert np.all(mass >= 0) and abs(float(mass.sum())-1) < 1e-14
            assert D(row['tail_bound']) <= D('1e-20')
            assert D(row['infinite_law_error_upper']) <= D('1e-10')
            # Independent Decimal closed form, not the stationary solver API.
            if case in ('1','2','3'):
                with localcontext() as c:
                    c.prec = 70
                    fraction = F(row['keep']); s = D(fraction.numerator)/D(fraction.denominator)
                    r = (-(1-s)+((1-s)**2+4*s*s).sqrt())/(2*s)
                    b = r*(1+r); A = 1/(b/(1-s)+(1+b)*r/(1-r))
                    distance = D(0)
                    for q in range(len(mass)):
                        for mode in (0,1):
                            exact = (A*b*(s/(1-s) if mode == 0 else 1) if q == 0
                                     else A*r**q*(b if mode else 1))
                            distance += abs(D.from_float(float(mass[q,mode]))-exact)
                    actual = (distance+A*(1+b)*r**len(mass)/(1-r))/2
                    assert actual <= D(row['infinite_law_error_upper'])
                    actual_tv[case] = str(actual)
    parameters = rows(OUT / 'feasibility_parameters.csv')
    assert len(parameters) == 10
    status_counts = {}
    for row in parameters:
        status = row['status']; status_counts[status] = status_counts.get(status,0)+1
        assert F(row['A_OFF']) == F(row['lambdaA'])-6 >= 0
        assert F(row['A_ON']) == F(row['lambdaA'])+6
        assert F(row['rhoA_stay']) == (F(row['lambdaA'])+F(row['u']))/10 < 1
        if status == 'HOLD_CAP':
            assert int(row['required_cap']) > 50000
            assert row['qA90_low_packet'] == row['law_error_bound'] == ''
        else:
            assert status == 'CERTIFIED_STATIONARY_PROTOTYPE'
            assert int(row['required_cap']) <= 50000
            assert F(row['qA90_low_packet']) == F(row['qA90_high_packet'])
            assert D(row['law_error_bound']) <= D('1e-10')
            assert float(row['posterior_error_bound']) <= 1e-8
    assert status_counts == result['feasibility_status_counts']
    assert not any(result[p] for p in ('candidate_grid_created','p_switch_computed',
                                      'A01_A04_run','tag_v1_1_created','headsup_sent',
                                      'human_artifacts_verified','new_rng_draws'))
    target = subprocess.check_output(['git','rev-parse','contract-v1^{}'],cwd=ROOT,text=True).strip()
    assert target == '6bb631f9181cc06bfade9d71e54ad57ca3bbb284'
    subprocess.run(['git','merge-base','--is-ancestor','27eeed4','HEAD'],cwd=ROOT,check=True)
    mutants = {model:mutate(model,output) for model in ('M1','M0')}
    assert manifest_check(OUT) == counts['v1_1_m2']
    receipt = dict(author='Doan Van Tai',status='PASS',artifact_counts=counts,
                   source_hashes_checked=len(config['source_hashes']),inputs_checked=len(config['inputs']),
                   N1=totals,N2_exact_cases=1875,stationary_closed_form_actual_TV=actual_tv,
                   feasibility_status_counts=status_counts,mutants=mutants,
                   contract_v1_target=target,preregistration_commit='27eeed4',
                   original_manifest_sha256=digest(OUT / 'artifact_manifest.json'),
                   outputs=[dict(file=str(p.relative_to(OUT) if p.is_relative_to(OUT) else p),sha256=digest(p))
                            for p in sorted(output.iterdir()) if p.is_file()])
    (output / 'verification_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=OUT / 'audit',
                        help='Fresh directory for audit/mutant receipts; original artifacts stay read only')
    audit(parser.parse_args().output_dir.resolve())
