"""Doan Van Tai — parameter-only predictions for the fixed future panel, before truth."""
import csv
from fractions import Fraction as F
import json
import resource
import signal
import time

from .discovery import ROOT, PROTOCOL, exposure_audit, write_json
from .predictor import StationaryCache, predict, nearest


def main():
    base=ROOT/'results/lessons/l4_9_v2'
    output=base/'future_predictions.jsonl'
    if output.exists():raise FileExistsError('do not overwrite frozen predictions')
    if not (ROOT/'notes/design/analysis_plan_v1.md').exists():raise FileNotFoundError('analysis plan required')
    protocol=json.loads(PROTOCOL.read_text())
    training=list(csv.DictReader((base/'discovery/nn_training.csv').open()))
    exposure_audit(protocol,training)
    resource.setrlimit(resource.RLIMIT_CPU,(180,181))
    signal.alarm(240)
    cache=StationaryCache(ROOT,base/'native_cache');begin=time.process_time();count=0
    with output.open('x') as f:
        for case in protocol['future_panel']:
            a,b,k,e,h,c=case['parameters']
            key='|'.join(map(str,map(F,(a,b,str(2*F(e)),k,h,c))))
            row=predict(case['parameters'],cache,ref=4,K=320)
            nn=nearest(key,training)
            row.update(id=case['id'],key=key,NN_pred_pctC=float(nn['GM_S1_pctC']),NN_key=nn['key'],
                       role='EXPLORATORY_ONLY',finite_h_M1_outcome_computed=False)
            f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');f.flush();count+=1
    signal.alarm(0)
    status=dict(status='COMPLETE',predictions=count,CPU_seconds=time.process_time()-begin,
                finite_h_M1_outcomes=0,panel_not_changed=True)
    write_json(base/'future_predictions_status.json',status)
    print(json.dumps(status))


if __name__=='__main__':main()
