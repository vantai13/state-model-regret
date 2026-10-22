"""v1.1 ĐK1 — analytic path-wise dominance screen (plant parameters only).

Provenance: soạn bởi Claude (AI) theo yêu cầu của Doan Van Tai, 22/10/2026,
sau DL-026. Tác giả chưa xác nhận các lựa chọn thiết kế đi kèm (DL-027).

Scientific purpose: phát hiện, KHÔNG cần tính J hay chạy pipeline, những state
mà một action không thể tốt hơn action kia trên mọi tương lai. Screen s_bt của
v1 chỉ kiểm "có queue nào có thể idle" (tầng 1 của không suy biến) và đã bỏ lọt
vùng Stay áp đảo (DL-026). Module này kiểm tầng 2 bằng bốn điều kiện đủ:

  SD1  B không thể idle dưới Stay                     -> C(Switch,w) >= C(Stay,w)
  SD2  backlog A cuối mọi slot = 0 dưới Stay, mọi path -> C(Switch,w) >= C(Stay,w)
  WD1  A không thể idle dưới Switch                   -> C(Switch,w) <= C(Stay,w)
  WD2  backlog B cuối mọi slot = 0 dưới Switch, mọi path -> C(Switch,w) <= C(Stay,w)

SD1 và WD1 cùng đúng là vùng bảo toàn (Delta = 0 trên mọi path).
Chứng minh: notes/design/design_conditions_v1_1.md, ĐK1.

Giả định dùng được hai path cực trị: recurrence q'=[q+a-c]^+ đơn điệu; mode của
slot 0 thuộc state; từ slot 1 mọi mode có thể chuyển và lưu lại với xác suất
dương (R2 với T_mode hữu hạn), hoặc queue chỉ có một mode (tất định).
Mọi lượng tính theo packet/slot; nên dùng Fraction để so sánh chính xác.

Tích hợp và kiểm chứng: Doan Van Tai, 23/10/2026. Attribution nguồn ở trên
được giữ nguyên. Phân loại ô dùng chứng chỉ trên mọi state có probability > 0;
không dùng tolerance để bỏ qua support hiếm hoặc chấp nhận support rỗng.
"""

import math
from collections.abc import Mapping
from numbers import Rational


def _nonnegative_finite(value, name):
    try:
        finite = isinstance(value, Rational) or math.isfinite(value)
        valid = finite and value >= 0
    except (TypeError, ValueError, OverflowError):
        valid = False
    if not valid:
        raise ValueError(f'{name} must be finite and nonnegative')


def _check_queue(rates, capacity, horizon):
    if not isinstance(rates, Mapping) or not rates:
        raise ValueError('rates must be a nonempty mapping of nonnegative per-slot amounts')
    for rate in rates.values():
        _nonnegative_finite(rate, 'rate')
    _nonnegative_finite(capacity, 'capacity')
    if type(horizon) is not int or horizon < 1:
        raise ValueError('capacity >= 0 and integer horizon >= 1 required')


def can_idle_within(q0, mode0, rates, extra, capacity, horizon):
    """True nếu có tương lai (xác suất dương) làm queue bỏ phí capacity ở một slot 0..H-1.

    Path ít arrival nhất: mode0 ở slot 0, mode có rate nhỏ nhất từ slot 1.
    Nhờ tính đơn điệu, path này idle nhiều nhất ở mọi slot. Kiểm idle bằng bất
    đẳng thức chặt q + a < c (chạm 0 đúng bằng capacity không phải idle).
    """
    _check_queue(rates, capacity, horizon)
    _nonnegative_finite(q0, 'initial backlog')
    _nonnegative_finite(extra, 'managed amount')
    if mode0 not in rates:
        raise ValueError('invalid initial backlog, managed amount or mode')
    first = rates[mode0] + extra
    if q0 + first < capacity:
        return True
    if horizon == 1:
        return False
    q1 = q0 + first - capacity
    tail = min(rates.values()) + extra
    if tail >= capacity:
        return False
    # Backlog giảm đều (capacity - tail) mỗi slot; slot cuối H-1 là ứng viên idle muộn nhất.
    q_last = max(0, q1 - (horizon - 2)*(capacity - tail))
    return q_last + tail < capacity


def empty_after_every_slot(q0, mode0, rates, extra, capacity, horizon):
    """True nếu backlog cuối mọi slot k=1..H bằng 0 trên MỌI path.

    Path nhiều arrival nhất: mode0 ở slot 0, mode có rate lớn nhất từ slot 1.
    Cost D13 chỉ đếm k>=1, nên q0 > 0 vẫn được nếu slot 0 xả hết.
    """
    _check_queue(rates, capacity, horizon)
    _nonnegative_finite(q0, 'initial backlog')
    _nonnegative_finite(extra, 'managed amount')
    if mode0 not in rates:
        raise ValueError('invalid initial backlog, managed amount or mode')
    if q0 + rates[mode0] + extra > capacity:
        return False
    return horizon == 1 or max(rates.values()) + extra <= capacity


def classify_state(qA, mA, qB, mB, plant):
    """Nhãn dominance của một state, chỉ từ tham số plant.

    plant: dict(ratesA, ratesB, cA, cB, u, H) — lượng mỗi slot. Stay đưa u vào A,
    Switch đưa u vào B. Trả về các cờ SD1, SD2, WD1, WD2 và một nhãn:
    'conservation' (SD1 và WD1), 'SD', 'WD' hoặc 'none'.
    """
    rA, rB, cA, cB, u, H = (plant[k] for k in ('ratesA', 'ratesB', 'cA', 'cB', 'u', 'H'))
    flags = dict(
        SD1=not can_idle_within(qB, mB, rB, 0, cB, H),
        SD2=empty_after_every_slot(qA, mA, rA, u, cA, H),
        WD1=not can_idle_within(qA, mA, rA, 0, cA, H),
        WD2=empty_after_every_slot(qB, mB, rB, u, cB, H),
    )
    sd = flags['SD1'] or flags['SD2']
    wd = flags['WD1'] or flags['WD2']
    if flags['SD1'] and flags['WD1']:
        label = 'conservation'
    elif sd and wd:
        label = 'tie'          # cả hai chiều đúng: Delta = 0 trên mọi path
    elif sd:
        label = 'SD'
    elif wd:
        label = 'WD'
    else:
        label = 'none'
    return dict(flags, label=label)


def cell_masses(states, plant):
    """Khối lượng theo nhãn trên support của D.

    states: iterable của (qA, mA, qB, mB, probability). Trả m_SD (gồm mọi state
    có SD1 hoặc SD2), m_WD tương tự, m_conservation, m_none và tổng khối lượng.
    Hệ quả dùng ở ĐK2: P_D(a* = Switch) <= 1 - m_SD.
    """
    out = dict(m_SD=0, m_WD=0, m_conservation=0, m_none=0, total=0,
               all_SD=True, all_WD=True, all_conservation=True, positive_states=0)
    for qA, mA, qB, mB, prob in states:
        _nonnegative_finite(prob, 'probability')
        if prob == 0:
            continue
        c = classify_state(qA, mA, qB, mB, plant)
        sd, wd = bool(c['SD1'] or c['SD2']), bool(c['WD1'] or c['WD2'])
        out['positive_states'] += 1
        out['all_SD'] &= sd
        out['all_WD'] &= wd
        out['all_conservation'] &= c['label'] == 'conservation'
        out['total'] += prob
        out['m_SD'] += prob if sd else 0
        out['m_WD'] += prob if wd else 0
        out['m_conservation'] += prob if c['label'] == 'conservation' else 0
        out['m_none'] += prob if c['label'] == 'none' else 0
    if not out['positive_states']:
        raise ValueError('nonempty positive-probability support required')
    _nonnegative_finite(out['total'], 'total mass')
    return out


def cell_label(masses, tol=0):
    """Nhãn của ô: 'SD-cell' nếu m_SD = 1 (ứng viên kiểm âm), 'WD-cell' nếu m_WD = 1
    (oracle-hằng, KHÔNG phải kiểm âm vì luật hoà), 'conservation-cell', hoặc 'candidate'."""
    _nonnegative_finite(tol, 'mass tolerance')
    total = masses['total']
    _nonnegative_finite(total, 'total mass')
    if total == 0 or masses.get('positive_states', 0) < 1:
        raise ValueError('use cell_masses with nonempty positive-probability support')
    for key in ('all_SD', 'all_WD', 'all_conservation'):
        if type(masses.get(key)) is not bool:
            raise ValueError('support certificates from cell_masses are required')
    # The certificate is exact over positive support. tol only checks mass sums,
    # never erases a small contrary state even if floating addition rounded it away.
    full = lambda key, certificate: masses[certificate] and abs(masses[key]-total) <= tol
    if full('m_conservation', 'all_conservation'):
        return 'conservation-cell'
    if full('m_SD', 'all_SD'):
        return 'SD-cell'
    if full('m_WD', 'all_WD'):
        return 'WD-cell'
    return 'candidate'
