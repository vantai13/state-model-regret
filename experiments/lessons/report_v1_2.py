"""Doan Van Tai — render notes/design/grid_v1_2.md from grid_v1_2.json (no new computation)."""
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = json.loads((ROOT / 'notes/design/grid_v1_2.json').read_text())


def num(x, d=3):
    return f'{float(F(x)):.{d}f}'.replace('.', ',')


def q(a):
    return f'q{int(F(a) * 100)}'


def p(c, l):
    return num((c[f'p_{l}'][0] + c[f'p_{l}'][1]) / 2)


def row(c):
    targets = ', '.join(num(a['target'], 1) for a in c['anchors'])
    br = ', '.join(a['bracketing'] for a in c['anchors'])
    return (f"| {c['id']} | {c['group']} | {num(c['kappa'], 1)} | {q(c['alphaA'])} | {q(c['alphaB'])} | {num(c['eta'], 3)} | "
            f"{c['horizon']} | {targets} | {num(c['lambdaA'], 2)} | {num(c['psi'], 3)} | {p(c, 1)} / {p(c, 2)} / {p(c, 4)} | "
            f"{br} | {num(c['updates_16'] / 1e9, 1)} | {'C' if c.get('calibration') else ''} |")


HEAD = ('| Ô | Nhóm | κ | A | B | η | h (s) | Mục tiêu | λA | ψ | p_sw dt / dt/2 / dt/4 | Kẹp | Budget dt/16 (×10⁹) | Cal. |\n'
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')

lines = [
    '# Lưới v1.2 — ACCEPTED' if G['status'] == 'ACCEPTED' else '# Lưới v1.2 — ' + G['status'], '',
    'Người phụ trách: **Doan Van Tai** · 23/10/2026. Sinh tự động từ [grid_v1_2.json](grid_v1_2.json) bằng '
    '`experiments/lessons/report_v1_2.py`. Protocol: [v1_2_protocol.md](v1_2_protocol.md) (commit '
    f"`{G['protocol_commit'][:7]}`, trước lần chạy). Quyết định: DL-038, DL-039.", '',
    f"**{len(G['main'])} ô chính**, **{len(G['heldout'])} ô held-out**, {len(G['controls'])} ô kiểm âm, "
    f"{len(G['probes'])} đầu dò cấu trúc. Calibration A01: {', '.join(c['id'] for c in G['calibration'])}.", '',
    'Mọi ô chính và held-out: $p_{\\text{sw}}$ trong $[0{,}1;0{,}9]$ ở dt, dt/2, dt/4; nhãn ĐK1 `candidate`; '
    'budget trong trần $2\\times10^{11}$ ở dt/16. Chỉ có xác suất dấu của oracle; **không** có $J$, margin, contrast hay regret.', '',
    '## Ô chính', '', HEAD, *[row(c) for c in G['main']], '',
    'Mục tiêu không neo được (giữ làm ghi nhận, không thay ô khác):', '',
    *[f"- {f['slice']}, mục tiêu {num(f['target'], 1)}: điểm gần nhất λA {num(f['lambdaA'], 2)} có p {num(f['p_coarse'])} ({f['bracketing']})."
      for f in G['main_failures']], '',
    '## Held-out', '',
    'Tọa độ khai báo trong protocol trước khi tính. Không dùng cho discovery hay calibration; $p_{\\text{sw}}$ và '
    'λA riêng của held-out không được làm biến đầu vào cho $H_0/H_1$.', '', HEAD, *[row(c) for c in G['heldout']], '',
    '## Ô kiểm âm và đầu dò', '',
    '| Ô | Vai trò | Nhãn dt / dt/2 | p_sw dt |', '|---|---|---|---|',
    *[f"| {c['id']} | {c['role']} | {c['label_1']} / {c['label_2']} | {num((c['p_low_1'] + c['p_high_1']) / 2)} |" for c in G['controls']],
    *[f"| {c['id']} | đầu dò cấu trúc | {c['label_1']} / {c['label_2']} | {num((c['p_low_1'] + c['p_high_1']) / 2)} |" for c in G['probes']], '',
    'Ở SD-cell và conservation-cell, sáu contrast phải bằng 0 chính xác khi Phase 3 tính; sai lệch là bug.', '',
    '## Đọc bảng', '',
    '- **Kẹp** (`bracketed`): mục tiêu nằm giữa hai điểm thang. `floor`: mọi điểm thang đều cao hơn mục tiêu, nên điểm cắt sẽ cần λA dưới đáy vật lý 6.',
    '- So sánh giữa các lát là ở **cùng độ khó**, không cùng tải; λA thay đổi theo lát. Báo $p_{\\text{sw}}$ thực, không coi như đúng 0,3 hay 0,7.',
    '- ψ = (λA − 8)/10 là đại lượng dẫn xuất. Kết quả chỉ áp dụng cho khoảng ψ trong bảng.',
]
(ROOT / 'notes/design/grid_v1_2.md').write_text('\n'.join(lines) + '\n')
print('written', len(lines), 'lines')
