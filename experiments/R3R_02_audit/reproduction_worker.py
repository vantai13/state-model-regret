"""Doan Van Tai — run only the engine imported from the isolated pilot clone."""
import json
from pathlib import Path
import sys

import numpy as np
from experiments.explore_v13.population import evaluate

spec = json.loads(Path(sys.argv[1]).read_text())
spec[6], spec[7] = int(spec[6]), int(spec[7])
row, pairs = evaluate(spec)
Path(sys.argv[2] + '.json').write_text(json.dumps(row, indent=2) + '\n')
np.savez_compressed(sys.argv[2] + '.npz', pairs=np.asarray(pairs, dtype=str))
