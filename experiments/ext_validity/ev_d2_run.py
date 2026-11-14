# Claude: resume of the EV-D test seed after a local OOM. Same code, same per-(case, h) seeds; existing outputs untouched.
import json, sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
from experiments.ext_validity import packet as P


def main():
    O = Path('results/ext_validity/ev_d2')
    tasks = []
    for c in json.loads((O / 'cases_c1.json').read_text()):
        tr = json.loads((O / 'train' / f"{c['id']}_s{c['seed']}.json").read_text())
        assert tr['case_sha256'] == P.signature(c)
        for m in c['h_mult']:
            out = O / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json"
            if not out.exists():
                tasks.append(('test', c, tr, m, out, False))
    tasks.sort(key=lambda t: -t[3] * t[2]['T_int'])
    print(len(tasks), 'tasks', flush=True)
    with ProcessPoolExecutor(max_workers=int(sys.argv[1]), mp_context=get_context('spawn')) as pool:
        for r in pool.map(P.job, tasks):
            print(json.dumps(r), flush=True)
    print('RESUME_DONE', flush=True)


if __name__ == '__main__':
    main()
