"""Doan Van Tai — read saved discovery only AFTER labels are committed."""
import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path
import subprocess

from experiments.R3R_04_realism.run_screen import OUT,git_bytes,sha,write_csv,verify_freeze


def main():
    p=argparse.ArgumentParser();p.add_argument('--labels-commit',required=True);args=p.parse_args()
    commit=subprocess.check_output(['git','rev-parse',f'{args.labels_commit}^{{commit}}'],text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],check=True)
    for name in ['labels.csv','receipt.json','implied_features.csv']:
        path=OUT/name
        if path.read_bytes()!=git_bytes(commit,str(path)):raise ValueError(f'Labels checkpoint changed: {name}')
    receipt=json.loads((OUT/'receipt.json').read_text())
    freeze,spec,_=verify_freeze(receipt['freeze_commit'])
    subprocess.run(['git','merge-base','--is-ancestor',freeze,commit],check=True)
    if spec['overlay']['commit'] != subprocess.check_output(['git','rev-parse',f'{spec["overlay"]["tag"]}^{{commit}}'],text=True).strip():
        raise ValueError('pilot tag changed')
    # First outcome access in this runner occurs here, after checkpoint checks.
    raw=[];raw_hashes={}
    for stage in spec['main_stages']:
        path=f'results/explore_v13/{stage}/regimes.csv'
        data=git_bytes(spec['overlay']['commit'],path);raw_hashes[path]=sha(data)
        raw.extend(csv.DictReader(io.StringIO(data.decode())))
    saved={r['id']:r for r in raw}
    labels=list(csv.DictReader((OUT/'labels.csv').open()));overlay=[]
    for r in labels:
        old=saved[r['id']]
        mv=float(old['G_M_pctC'])>=spec['overlay']['MV_GM_pctC_at_least']
        harm=float(old['G_S_pctC'])<=spec['overlay']['SH_GS_pctC_at_most']
        overlay.append(dict(**r,MV=mv,SH=harm,overlap=mv and harm))
    dest=Path('results/lessons/l3r_4/overlay');write_csv(dest/'by_id.csv',overlay)
    summaries=[]
    for c in spec['contexts']:
        for factor in spec['f_sensitivity']:
            subset=[r for r in overlay if r['context']==c['id'] and float(r['f'])==factor]
            for region in ['ALL','MV','SH','overlap']:
                selected=subset if region=='ALL' else [r for r in subset if r[region]]
                distinct={r['coordinate']:r for r in selected}
                summaries.append(dict(context=c['id'],f=factor,region=region,ids=len(selected),distinct=len(distinct),
                                      **{f'IDs_{lab}':sum(r['label']==lab for r in selected) for lab in ['IN','EDGE','OUT','UNSOURCED']},
                                      **{f'distinct_{lab}':sum(r['label']==lab for r in distinct.values()) for lab in ['IN','EDGE','OUT','UNSOURCED']}))
    write_csv(dest/'summary.csv',summaries)
    summary=dict(owner=spec['owner'],label_commit=commit,freeze_commit=freeze,raw_commit=spec['overlay']['commit'],raw_hashes=raw_hashes,
                 outcome_source='Existing frozen discovery CSV only; no engine outcome run',
                 counts=summaries,decision={'MV':'(d) HOLD_REALISM_UNSOURCED','SH':'(d) HOLD_REALISM_UNSOURCED'},
                 empirical_prevalence_claim=False,new_CF_outcomes=False)
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='counts'},indent=2))


if __name__=='__main__':main()
