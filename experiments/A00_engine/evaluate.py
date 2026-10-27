"""Doan Van Tai — experimental evaluate_cell; guard precedes cell/D loading."""
import argparse
import json
from fractions import Fraction as F

from experiments.A00_engine.factorial_core import aggregate
from experiments.A00_engine.cells_adapter import load_cell
from experiments.A00_engine.guard import guard
from experiments.A00_engine.physical import side_table
from experiments.A00_engine.precision import enclose


def evaluate_sides(A, B, *, refinement, dt):
    if type(refinement) is not int or refinement < 1 or dt <= 0:
        raise ValueError('positive refinement and dt required')
    result = aggregate(A, B)
    result.update(enclose(A, B, result))
    result['reference_context'] = dict(refinement=refinement, dt_s=str(dt))
    result['refinement'] = refinement
    result['dt_s'] = str(dt)
    result['nominal_actions'] = {'00': int(result['E_delta_hat'] < 0), '01': int(result['E_delta'] < 0)}
    minimum_ref = result['intervals']['C_ref'][0]
    gains = tuple(result['G'])
    within = minimum_ref > 0 and all(result['e_num'][k] <= .0025 * minimum_ref for k in gains)
    result['numeric_budget_met'] = within
    result['status'] = ('BOUNDED' if within and result['a00'] is not None and
                        max(result['unresolved_mass'].values()) <= .01 else 'HOLD_PRECISION')
    result['not_computed'] = ['future_EVPI', 'flip_mass_2D']
    return result


def evaluate_cell(cell_id, ref, *, extended=True, **authorization):
    receipt = guard(cell_id, **authorization)
    cell = load_cell(cell_id)
    A, _ = side_table(cell, 'A', ref, extended=extended, **authorization)
    B, _ = side_table(cell, 'B', ref, extended=extended, **authorization)
    result = evaluate_sides(A, B, refinement=ref, dt=F(1, 120 * ref))
    result.update(cell_id=cell_id, provenance=receipt)
    return result


def main():
    p = argparse.ArgumentParser(description='Experimental engine: no grid run before L3.3')
    p.add_argument('cell_id')
    p.add_argument('--ref', type=int, default=1)
    p.add_argument('--allow-grid', action='store_true')
    p.add_argument('--allow-heldout', action='store_true')
    p.add_argument('--purpose', choices=('A01', 'A04', 'A05-T'))
    args = p.parse_args()
    result = evaluate_cell(args.cell_id, args.ref, allow_grid=args.allow_grid,
                           allow_heldout=args.allow_heldout, purpose=args.purpose)
    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
