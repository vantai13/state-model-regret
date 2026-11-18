import multiprocessing as mp, json, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, '/home/vantai/state-model-regret')
from experiments.letter import v7_3_test as Run, v7_3_test_common as C
if __name__ == '__main__':
    params = dict(C.read_json(C.ROOT/C.PARAMS)); params['N_test'] = 2; params['test_seed'] = 7372001
    out = Path('/tmp/v73pool/run')
    dates = ['2005-05-06', '2005-05-11']
    training, arrays, config, tasks, labels = Run.prepare_inputs(params, out, training_only=True, dates=dates)
    sel = [t for t in tasks if t[0] in ('DAY1', 'DAY3')][:3]
    print('selected', sel, flush=True)
    with ProcessPoolExecutor(3, mp_context=mp.get_context('spawn')) as pool:
        futs = [pool.submit(Run.write_record, training, arrays, config, params, out, g, d, labels[(g, d)], training_only=True) for g, d in sel]
        for f in as_completed(futs):
            print(json.dumps(f.result()), flush=True)
    print('POOL OK', sorted(p.name for p in (out/'records').iterdir()))
