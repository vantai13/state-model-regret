"""Doan Van Tai — EV-B replication of the alarm sign reversal at q75 and q95 on a fresh panel [AI (Claude) theo ủy
quyền 14/11/2026]. Reuses alarm.py unchanged (its EV-B lock stays valid); only the panel, the seed and Q_ALARM differ.

    python -m experiments.ext_validity.alarm_rep design|predict|truth|score --q 0.75
"""
import argparse
import json
import sys

from experiments.ext_validity import alarm as A

ROOT = A.ROOT
BASE = ROOT / 'results/ext_validity/ev_b_rep'


def configure(q):
    A.Q_ALARM = q
    A.SEED = 20261152
    A.OUT = BASE / f'q{int(round(q * 100))}'
    A.CASES = BASE / 'cases.json'                    # one fresh panel shared by both alarm levels
    A.PRED, A.TRUTH = A.OUT / 'predictions.csv', A.OUT / 'truth.csv'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['design', 'predict', 'truth', 'score'])
    ap.add_argument('--q', type=float, required=True)
    ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    configure(a.q)
    A.OUT.mkdir(parents=True, exist_ok=True)
    if a.cmd == 'design':
        seen_extra = json.loads((ROOT / 'results/ext_validity/ev_b/cases.json').read_text())
        orig = A.design.__globals__['seen_all'] if 'seen_all' in A.design.__globals__ else None
        import experiments.explore_ctmc.csw_harm as H
        base_seen = H.seen_all
        H.seen_all = lambda: base_seen() | {tuple(A.F(x) for x in c['parameters'][:4]) for c in seen_extra}
        A.OUT = BASE
        A.design()
        H.seen_all = base_seen
    else:
        sys.argv = ['alarm', a.cmd, '--workers', str(a.workers)]
        if a.cmd == 'truth' and not (BASE / 'lock.json').exists():
            raise RuntimeError('replication predictions are not locked')
        if a.cmd == 'truth':
            (A.OUT / 'lock.json').write_text((BASE / 'lock.json').read_text())
        A.main()


if __name__ == '__main__':
    main()
