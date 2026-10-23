"""DISCOVERY extra check (declared in the report §3.2, not in the plan): DK1 labels for five
structurally locked probe cells. Claude (AI) for Doan Van Tai. Sign probabilities and labels only."""
import json
from fractions import Fraction as F
from experiments.explore.reformulate_grid import slices, task, OUT

PROBES = [('S32', F(7)), ('S35', F(7)), ('S29', F(7)), ('S26', F(6)), ('S20', F(8))]

if __name__ == '__main__':
    defs = {s['slice']: s for s in slices()}
    with (OUT / 'probe_labels.jsonl').open('w') as handle:
        for name, lam in PROBES:
            row = task((defs[name], lam, (1, 2), True))
            handle.write(json.dumps(row) + '\n')
            print(name, lam, row['status'], row.get('label_1'), row.get('label_2'))
