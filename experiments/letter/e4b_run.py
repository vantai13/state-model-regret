"""E4b: replication of E4 on a new test seed, same 17 GEANT regimes, same locked E4 code.

Thin wrapper (Claude, 16/11/2026). It only sets e4_geant.TEST_SEED and OUT, then
calls e4_geant.main. Workers receive the seed through their task tuple, so the
spawned processes use the new seed even though they re-import e4_geant.
"""
import sys

from experiments.letter import e4_geant as E

E4B_SEED = 5000001
E.TEST_SEED = E4B_SEED
E.OUT = E.ROOT / 'results/letter/e4b'

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--out' not in argv:
        argv += ['--out', str(E.OUT)]
    E.main(argv)
