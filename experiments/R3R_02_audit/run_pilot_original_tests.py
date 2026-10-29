"""Doan Van Tai — original 19 toy tests, unchanged bytes, import alias only."""
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import pytest
from experiments.R3R_02_audit import pilot_population as population

package = types.ModuleType('experiments.explore_v13')
package.population = population
sys.modules['experiments.explore_v13'] = package
sys.modules['experiments.explore_v13.population'] = population

if __name__ == '__main__':
    raise SystemExit(pytest.main(['-q', str(Path(__file__).with_name('pilot_tests_original.py')),
                                '--junitxml=' + str(ROOT / 'results/lessons/l3r_3/pilot_original_tests.xml')]))
