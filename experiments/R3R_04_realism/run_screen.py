"""Doan Van Tai — A2 design-only mapping, after committed envelope/rules.

No outcomes/decision imports. A separate overlay step requires committed labels.
"""
import argparse
import csv
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

from experiments.R3R_04_realism.implied import implied, delay_exceedance
from experiments.R3R_04_realism.classify import classify

CONFIG = Path('notes/realism/envelope_v1.json')
OUT = Path('results/lessons/l3r_4/screen')
COORDINATES = ('lambdaA', 'lambdaB', 'kappa', 'u', 'h', 'c_sw', 'ref', 'K')


def sha(data): return hashlib.sha256(data).hexdigest()


def git_bytes(commit, path):
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'])


def verify_freeze(commit):
    full = subprocess.check_output(['git', 'rev-parse', f'{commit}^{{commit}}'], text=True).strip()
    subprocess.run(['git', 'merge-base', '--is-ancestor', full, 'HEAD'], check=True)
    spec = json.loads(CONFIG.read_text())
    hashes = {}
    for path in spec['freeze_paths']:
        data = Path(path).read_bytes()
        if data != git_bytes(full, path): raise ValueError(f'Frozen source changed: {path}')
        hashes[path] = sha(data)
    return full, spec, hashes


def key(row): return '|'.join(str(F(row[k])) for k in COORDINATES)


def designs(spec):
    reader = csv.DictReader(Path(spec['design_csv']).open())
    if set(reader.fieldnames) != {'id','stage','lambdaA','lambdaB','kappa','eta','h','c_sw','ref','K','u'}:
        raise ValueError('design-only column contract violated')
    rows = [r for r in reader if r['stage'] in spec['main_stages']]
    if len(rows) != spec['expected_ids'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('main ID universe mismatch')
    if len({key(r) for r in rows}) != spec['expected_distinct']: raise ValueError('distinct universe mismatch')
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--freeze', required=True); args = p.parse_args()
    commit, spec, hashes = verify_freeze(args.freeze)
    rows = designs(spec); features, labels = [], []
    for row in rows:
        numeric = {k: float(F(row[k])) for k in COORDINATES}
        for context in spec['contexts']:
            x = implied(numeric['lambdaA'], numeric['lambdaB'], numeric['u'], numeric['kappa'],
                        numeric['h'], tau_anchor_s=context['illustrative_tau_s'],
                        windows_s=spec['fixed_windows_s'], c_sw_model=numeric['c_sw'], ref=int(numeric['ref']))
            feat = dict(id=row['id'], context=context['id'], coordinate=key(row), stage=row['stage'], **numeric)
            feat.update({k:v for k,v in x.items() if not isinstance(v, dict)})
            feat['anchor_role'] = 'ILLUSTRATIVE_NOT_EMPIRICAL_NO_IN_CERTIFICATE'
            for queue in ['A_pre','A_post','B_pre','B_post']:
                for field, value in x[queue].items():
                    if field == 'CV_windows':
                        for w, cv in value.items(): feat[f'{queue}_CV_{w}s'] = cv
                    else: feat[f'{queue}_{field}'] = value
                for ratio in spec['buffer_ratio_sensitivity']:
                    feat[f'{queue}_tail_delay_{ratio}T_sensitivity_only'] = delay_exceedance(x[queue],10,ratio*x['T_mode_s'])
            feat.update(buffer_flag='UNSOURCED',actuation_flag='UNSOURCED',mode_oracle_flag=True,
                        buffer_time_s=None,actuation_s=None)
            features.append(feat)
            # v1 empirical ranges are deliberately absent. No fitted conversion,
            # no substituted anchor. Later sourced versions need a new prereg.
            if context['tau_eff_s'] is not None or any(c['allowed_tau_s'] is not None for c in context['constraints']):
                raise ValueError('v1 runner supports the frozen incomplete envelope only; new ranges require versioned conversion')
            for factor in spec['f_sensitivity']:
                result = classify(context['tau_eff_s'],context['constraints'],k=spec['k'])
                labels.append(dict(id=row['id'],context=context['id'],f=factor,coordinate=key(row),
                                   label=result['label'],missing=';'.join(result['missing']),
                                   buffer_flag=feat['buffer_flag'],actuation_flag=feat['actuation_flag'],mode_oracle_flag=True))
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT/'implied_features.csv',features);write_csv(OUT/'labels.csv',labels)
    receipt = dict(owner=spec['owner'],created_utc=datetime.now(timezone.utc).isoformat(),freeze_commit=commit,
                   freeze_hashes=hashes,design_sha256=sha(Path(spec['design_csv']).read_bytes()),
                   ids=len(rows),distinct=len({key(r) for r in rows}),contexts=len(spec['contexts']),
                   feature_rows=len(features),label_rows=len(labels),
                   counts={f'{c["id"]}:f={factor}':dict(Counter(r['label'] for r in labels if r['context']==c['id'] and r['f']==factor))
                           for c in spec['contexts'] for factor in spec['f_sensitivity']},
                   outcomes_opened=False,CF_opened=False,
                   outputs={str(OUT/n):sha((OUT/n).read_bytes()) for n in ['implied_features.csv','labels.csv']})
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__ == '__main__': main()
