"""v1.1 ĐK1 — kiểm screen áp đảo giải tích bằng vét cạn (không RNG, không seed).

Provenance: soạn bởi Claude (AI) theo yêu cầu của Doan Van Tai, 22/10/2026.
Không tính J, gap hay contrast trên bất kỳ ô lưới nào; phần v1 chỉ đọc tham số
và support của D đã có (DL-026).
"""
from fractions import Fraction as F
from itertools import product

import numpy as np
import pytest

from smr.design import design_cells, episode_law
from smr.dominance import (can_idle_within, cell_label, cell_masses, classify_state,
                           empty_after_every_slot)

MODES = ('off', 'on')


# ---------- tham chiếu độc lập: liệt kê tường minh mọi path ----------

def _paths(mode0, H):
    for rest in product(MODES, repeat=H-1):
        yield (mode0,) + rest


def _prob(seq, keep):
    p = F(1)
    for a, b in zip(seq, seq[1:]):
        p *= keep if a == b else 1-keep
    return p


def _rollout(q, seq, rates, extra, c):
    backlogs, idles = [], []
    for m in seq:
        a = rates[m] + extra
        idles.append(max(0, c-q-a))
        q = max(0, q+a-c)
        backlogs.append(q)
    return backlogs, idles


def _cost(state, seqA, seqB, plant, action):
    qA, _, qB, _ = state
    uA = plant['u'] if action == 'Stay' else 0
    uB = plant['u'] if action == 'Switch' else 0
    a, _ = _rollout(qA, seqA, plant['ratesA'], uA, plant['cA'])
    b, _ = _rollout(qB, seqB, plant['ratesB'], uB, plant['cB'])
    return sum(a) + sum(b)


def _m0_cost(state, plant, action):
    """Mean rollout có điều kiện theo mode slot 0 (định nghĩa M0 của contract)."""
    total = F(0)
    for q, m, rates, extra, c, keep in (
            (state[0], state[1], plant['ratesA'], plant['u'] if action == 'Stay' else 0,
             plant['cA'], plant['keepA']),
            (state[2], state[3], plant['ratesB'], plant['u'] if action == 'Switch' else 0,
             plant['cB'], plant['keepB'])):
        p_on = F(1) if m == 'on' else F(0)
        for _ in range(plant['H']):
            q = max(F(0), q + p_on*rates['on'] + (1-p_on)*rates['off'] + extra - c)
            total += q
            p_on = p_on*keep + (1-p_on)*(1-keep)
    return total


def _small_plants():
    """9.216 ca nguồn +3.456 ca low-arrival/H1; mỗi state <=16 cặp path.

    Doan Van Tai,23/10: ca nguồn chưa bao giờ kích hoạt SD2/WD2 (ON+u>c).
    Bổ sung kiểm coverage, không phải chọn tham số của lưới nghiên cứu.
    """
    for H, cA, cB, u, rA, rB, kA, kB in product(
            (2, 3), (2, 3), (2, 3), (1, 2), ((0, 3), (1, 5)), ((0, 3), (1, 5)),
            (F(1, 4), F(3, 4)), (F(1, 4), F(3, 4))):
        plant = dict(H=H, cA=cA, cB=cB, u=u, keepA=kA, keepB=kB,
                     ratesA=dict(zip(MODES, rA)), ratesB=dict(zip(MODES, rB)))
        for qA, qB, mA, mB in product((0, 1, 4), (0, 1, 4), MODES, MODES):
            yield plant, (qA, mA, qB, mB)
    for H,cA,cB,u,kA,kB in product((1,2,3),(2,3),(2,3),(1,2),
                                   (F(1,4),F(3,4)),(F(1,4),F(3,4))):
        plant=dict(H=H,cA=cA,cB=cB,u=u,keepA=kA,keepB=kB,
                   ratesA=dict(off=0,on=1),ratesB=dict(off=0,on=1),
                   verification_group='integration_low_arrival')
        for qA,qB,mA,mB in product((0,1,4),(0,1,4),MODES,MODES):
            yield plant,(qA,mA,qB,mB)


def test_closed_forms_match_explicit_rollouts():
    for plant, (qA, mA, qB, mB) in _small_plants():
        for q, m, rates, c in ((qA, mA, plant['ratesA'], plant['cA']),
                               (qB, mB, plant['ratesB'], plant['cB'])):
            for extra in (0, plant['u']):
                runs = [_rollout(q, s, rates, extra, c) for s in _paths(m, plant['H'])]
                assert can_idle_within(q, m, rates, extra, c, plant['H']) == \
                    any(any(i > 0 for i in idles) for _, idles in runs)
                assert empty_after_every_slot(q, m, rates, extra, c, plant['H']) == \
                    all(all(v == 0 for v in back) for back, _ in runs)


def test_four_conditions_hold_pathwise_and_for_m0():
    checked = dict(SD1=0, SD2=0, WD1=0, WD2=0, conservation=0, switch_strict=0)
    for plant, (qA, mA, qB, mB) in _small_plants():
        state = (qA, mA, qB, mB)
        flags = classify_state(qA, mA, qB, mB, plant)
        for name in ('SD1','SD2','WD1','WD2'):
            checked[name] += bool(flags[name])
        diffs = []
        for sA in _paths(mA, plant['H']):
            for sB in _paths(mB, plant['H']):
                d = _cost(state, sA, sB, plant, 'Switch') - _cost(state, sA, sB, plant, 'Stay')
                diffs.append(d)
                if d < 0:
                    # Điều kiện cần cho "Switch thắng trên path này": B idle dưới Stay
                    # VÀ A có backlog cuối một slot nào đó dưới Stay.
                    checked['switch_strict'] += 1
                    _, idleB = _rollout(qB, sB, plant['ratesB'], 0, plant['cB'])
                    backA, _ = _rollout(qA, sA, plant['ratesA'], plant['u'], plant['cA'])
                    assert any(i > 0 for i in idleB) and any(v > 0 for v in backA)
        m0_gap = _m0_cost(state, plant, 'Switch') - _m0_cost(state, plant, 'Stay')
        if flags['SD1'] or flags['SD2']:
            assert min(diffs) >= 0 and m0_gap >= 0
        if flags['WD1'] or flags['WD2']:
            assert max(diffs) <= 0 and m0_gap <= 0
        if flags['label'] == 'conservation':
            checked['conservation'] += 1
            assert all(d == 0 for d in diffs)
    # Lưới phải thật sự chạm cả bốn loại, nếu không test này không kiểm gì.
    assert min(checked.values()) > 0, checked


def test_tie_rule_makes_wd_cells_not_zero_controls():
    """WD1 đúng nhưng M0 dự đoán hoà -> luật hoà chọn Stay -> regret 1/2.
    Vì vậy ô WD không được dùng làm ô kiểm âm (ĐK1, ĐK6)."""
    plant = dict(H=3, cA=3, cB=3, u=1, keepA=F(1, 2), keepB=F(1, 2),
                 ratesA=dict(off=5, on=5), ratesB=dict(off=1, on=5))
    state = (10, 'on', 0, 'on')
    flags = classify_state(*state, plant)
    assert flags['WD1'] and not (flags['SD1'] or flags['SD2'])
    J = {a: sum(_prob(sA, plant['keepA'])*_prob(sB, plant['keepB'])*_cost(state, sA, sB, plant, a)
                for sA in _paths('on', 3) for sB in _paths('on', 3))
         for a in ('Stay', 'Switch')}
    assert J == {'Stay': F(109, 2), 'Switch': F(54)}
    assert _m0_cost(state, plant, 'Stay') == _m0_cost(state, plant, 'Switch') == 54
    regret_m0 = J['Stay'] - J['Switch']        # M0 hoà -> Stay; oracle -> Switch
    assert regret_m0 == F(1, 2)


def test_v1_grid_classification_documents_dl026():
    """Post-hoc, chỉ tham số + support D đã có. Không tính J/gap/contrast (DL-026)."""
    labels = {}
    for cell in design_cells():
        qa, quantum, mass, dt, _ = episode_law(cell)
        H = cell['horizon']/dt
        assert H.denominator == 1
        plant = dict(ratesA={'det': 5*dt}, ratesB={0: 2*dt, 1: 14*dt},
                     cA=10*dt, cB=10*dt, u=2*cell['eta']*dt, H=int(H))
        states = [(qa, 'det', int(q)*quantum, int(m), float(mass[q, m]))
                  for q, m in zip(*np.nonzero(mass))]
        labels[cell['id']] = cell_label(cell_masses(states, plant), tol=1e-12)
    sd = {c for c, lab in labels.items() if lab == 'SD-cell'}
    assert sd == {f'M{i:02}' for i in range(1, 13)} | {'S01'}
    assert {'M01', 'M02', 'M10'} <= sd            # cả ba ô calibration của v1
    assert labels['N01'] == labels['N02'] == 'conservation-cell'
    assert all(labels[f'M{i:02}'] == 'candidate' for i in range(13, 25))
    assert labels['S02'] == 'candidate'


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        can_idle_within(-1, 'on', dict(on=1), 0, 2, 2)
    with pytest.raises(ValueError):
        empty_after_every_slot(0, 'x', dict(on=1), 0, 2, 2)
    with pytest.raises(ValueError):
        can_idle_within(0, 'on', dict(on=1), 0, 2, 0)


def test_nonfinite_and_empty_support_are_rejected():
    """Doan Van Tai — integration guards, 23/10/2026."""
    plant = dict(ratesA={'det': 1}, ratesB={'off': 0, 'on': 10},
                 cA=3, cB=3, u=1, H=2)
    for bad in (float('nan'), float('inf'), -float('inf')):
        for function in (can_idle_within, empty_after_every_slot):
            for args in ((bad, 'on', {'on': 1}, 0, 2, 2),
                         (0, 'on', {'on': bad}, 0, 2, 2),
                         (0, 'on', {'on': 1}, bad, 2, 2),
                         (0, 'on', {'on': 1}, 0, bad, 2)):
                with pytest.raises(ValueError):
                    function(*args)
        with pytest.raises(ValueError):
            cell_masses([(0, 'det', 0, 'off', bad)], plant)
    for support in ([], [(0, 'det', 0, 'off', F(0))]):
        with pytest.raises(ValueError): cell_masses(support, plant)
    with pytest.raises(ValueError):
        cell_label(dict(total=0, m_SD=0, m_WD=0, m_conservation=0))


def test_rare_positive_state_is_not_removed_by_mass_tolerance():
    plant = dict(ratesA={'det': 1}, ratesB={'off': 0, 'on': 10},
                 cA=3, cB=3, u=1, H=2)
    masses = cell_masses([(0, 'det', 0, 'off', 1.0),
                          (4, 'det', 0, 'off', 1e-40)], plant)
    assert masses['m_SD'] == masses['total'] == 1.0  # rounded sums alone mislead
    assert masses['positive_states'] == 2 and not masses['all_SD']
    assert cell_label(masses, tol=1e-12) == 'candidate'
    only_sd = cell_masses([(0, 'det', 0, 'off', F(1)),
                           (4, 'det', 0, 'off', F(0))], plant)
    assert only_sd['positive_states'] == 1
    assert cell_label(only_sd) == 'SD-cell'


def test_single_slot_and_generalized_empty_condition():
    # q0 can be positive: D13 counts only end-of-slot backlog.
    assert empty_after_every_slot(F(1), 'off', {'off': 1, 'on': 100}, F(1), 3, 1)
    assert not can_idle_within(F(1), 'off', {'off': 1, 'on': 100}, F(1), 3, 1)
    assert not empty_after_every_slot(F(1), 'off', {'off': 1, 'on': 100}, F(1), 3, 2)
