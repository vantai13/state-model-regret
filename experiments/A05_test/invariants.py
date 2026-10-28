"""Doan Van Tai — A05-T tier-1 bug invariants and pre-declared diagnostics.

AI (Claude) viết theo ủy quyền (L3.7, DL-059). Invariants are bug checks applied
identically to every opened cell-level. Diagnostics carry the label
DIAGNOSTIC_NOT_VERDICT: they are computed for every opened cell and contrast,
whatever the verdict, and are never read by the frozen scorer.
"""
from fractions import Fraction as F

from experiments.A03_card.grading import get, ratio, validate_reference

PC4 = ('G_S', 'G_M', 'Gamma')
LABEL = 'DIAGNOSTIC_NOT_VERDICT'


def q(x):
    return x if isinstance(x, F) else F(str(x))


def extra_checks(cid, ref, r, record, cell):
    """Checks beyond A04 ledger_checks: identity of the record, dt, reference, regrets."""
    out = dict(cell_id_match=bool(
        cell['id'] == cid == record['id'] and
        all(cell[k] == q(record[k]) for k in ('kappa', 'eta', 'h', 'yA', 'yB')) and
        cell['H_coarse'] == int(record['H_coarse'])))
    dt = F(1, 120 * ref)
    out['dt_match'] = bool(r['refinement'] == ref and q(r['dt_s']) == dt and
                           r['reference_context']['refinement'] == ref and
                           q(r['reference_context']['dt_s']) == dt)
    try:
        validate_reference(r)
        out['reference_is_L11'] = True
    except ValueError:
        out['reference_is_L11'] = False
    # An oracle cannot lose to any pipeline: no regret interval lies wholly below zero.
    out['regrets_not_below_zero'] = all(get(r, k).hi >= 0 for k in ('R00', 'R01', 'R10'))
    s, g, m1 = get(r, 'G_S'), get(r, 'Gamma'), get(r, 'G_S_M1')
    out['GS_plus_Gamma_meets_GS_M1'] = bool(s.lo + g.lo <= m1.hi and m1.lo <= s.hi + g.hi)
    return out


def position(lo, hi, p0, p1):
    """Where the truth interval sits relative to the two frozen point predictions."""
    a, b = min(p0, p1), max(p0, p1)
    if a <= lo and hi <= b:
        return 'between_predictions'
    if hi < a or lo > b:
        nearer = a if hi < a else b
        return 'beyond_H0_side' if nearer == p0 and p0 != p1 else 'beyond_H1_side' if p0 != p1 else 'beyond_both'
    return 'straddles_a_prediction'


def contribution(lo, hi, p0, p1):
    ends = [abs(p0 - y) - abs(p1 - y) for y in (lo, hi)]
    return min(ends), max(ends)


def mean(values):
    values = list(values)
    return sum(values) / len(values)


def group_level_shape(entries):
    """Per contrast: level vs shape split, truth at interval midpoints (diagnostic)."""
    out = {}
    for g in PC4:
        rows = [e for e in entries if e['contrast'] == g]
        if not rows:
            continue
        p0 = [e['_p0'] for e in rows]
        p1 = [e['_p1'] for e in rows]
        y = [(e['_lo'] + e['_hi']) / 2 for e in rows]
        m0, m1, my = mean(p0), mean(p1), mean(y)
        out[g] = dict(
            n_cells=len(rows),
            D_contrast=float(mean(abs(a - b) for a, b in zip(p0, p1))),
            level_gap_abs_mean_difference=float(abs(m0 - m1)),
            mean_signed_error_H0=float(m0 - my), mean_signed_error_H1=float(m1 - my),
            MAE_midpoint_H0=float(mean(abs(a - t) for a, t in zip(p0, y))),
            MAE_midpoint_H1=float(mean(abs(b - t) for b, t in zip(p1, y))),
            shape_only_MAE_H0=float(mean(abs((a - m0) - (t - my)) for a, t in zip(p0, y))),
            shape_only_MAE_H1=float(mean(abs((b - m1) - (t - my)) for b, t in zip(p1, y))))
    return out


def diagnostics(data, predictions, disc, records, verdict_eligible=None):
    """All opened cells; units are fractions of the same row's Cref unless noted."""
    cells = {}
    for cid, fine in sorted(data['fine'].items()):
        C = get(fine, 'C_ref')
        a00, a01 = fine['nominal_actions']['00'], fine['nominal_actions']['01']
        entry = dict(a00_nominal=a00, a01_nominal=a01, G_M_structurally_zero=bool(a00 == a01),
                     engine_p_sw=str(fine['p_sw']), public_design_p_2=records[cid]['p_2'])
        if C.lo > 0:
            R = ratio(get(fine, 'R00'), C)
            entry.update(R00_over_Cref=[str(R.lo), str(R.hi)],
                         headroom_upper_below_1_200=bool(R.hi < F(1, 200)),
                         headroom_upper_below_1_100=bool(R.hi < F(1, 100)))
        cells[cid] = entry
    groups = {}
    for name, info in disc['groups'].items():
        if not info['comparison_open']:
            groups[name] = dict(comparison_open=False, truth_used=False)
            continue
        entries = []
        for cid in info['ids']:
            fine = data['fine'].get(cid)
            if fine is None or get(fine, 'C_ref').lo <= 0:
                continue
            for g in PC4:
                band = ratio(get(fine, g), get(fine, 'C_ref'))
                p0 = q(predictions[cid]['H0']['contrasts'][g])
                p1 = q(predictions[cid]['H1']['contrasts'][g])
                c = contribution(band.lo, band.hi, p0, p1)
                entries.append(dict(cell=cid, contrast=g, truth_ratio=[str(band.lo), str(band.hi)],
                                    H0=str(p0), H1=str(p1), position=position(band.lo, band.hi, p0, p1),
                                    d_contribution=[str(c[0]), str(c[1])], saturation_bound=str(abs(p0 - p1)),
                                    _p0=p0, _p1=p1, _lo=band.lo, _hi=band.hi))
        counts = {}
        for e in entries:
            counts[e['position']] = counts.get(e['position'], 0) + 1
        groups[name] = dict(comparison_open=True, scope='all opened cells with positive Cref',
                            verdict_eligible_ids=(verdict_eligible or {}).get(name),
                            position_counts=counts, level_shape=group_level_shape(entries),
                            entries=[{k: v for k, v in e.items() if not k.startswith('_')} for e in entries])
    return dict(label=LABEL, units='fraction of Cref (multiply by 100 for percentage points)',
                cells=cells, PC4_groups=groups)
