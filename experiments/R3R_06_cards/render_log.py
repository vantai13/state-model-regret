"""Doan Van Tai — render the L3R.6 forking-paths JSONL as a readable table (no data access)."""
import json
import sys
from pathlib import Path

LOG = Path('results/lessons/l3r_6/forking_paths.jsonl')
OUT = Path('notes/phases/PHASE_3R_forking_paths.md')


def row(e):
    k = e['kind']
    if k == 'exposure_before_rules':
        return [e['seq'], e['utc'][:19], e['who'], '— (không phải luật)', '; '.join(e['seen']), '—', e['purpose']]
    if k == 'rule':
        return [e['seq'], e['utc'][:19], 'AI', e['rule'], f"n={e['n']} · " + ', '.join(f'{a}={b}' for a, b in e['counts'].items()),
                '', e['purpose']]
    if k in ('table', 'listing'):
        what = f"{len(e['cells'])} ô" if k == 'table' else f"{e['n']} cấu hình"
        return [e['seq'], e['utc'][:19], 'AI', f'{k}: ' + e['purpose'], what, '—', 'tái lập bảng lesson']
    if k == 'declaration':
        return [e['seq'], e['utc'][:19], 'AI', e['rule'], 'không nhìn dữ liệu', 'Giữ (mô tả)', e['purpose']]
    if k == 'decision':
        kept = '; '.join(f'{a}: {b}' for a, b in e['kept'].items())
        dropped = '; '.join(f'{a}: {b}' for a, b in e['dropped'].items())
        return [e['seq'], e['utc'][:19], 'Tác giả chọn, AI ghi', '—', f"rules_tried={e['rules_tried']}",
                f'Giữ: {kept} · Bỏ: {dropped}', e['not_a_rule_choice']]
    return [e['seq'], e['utc'][:19], e.get('who', ''), k, '', '', '']


def main():
    entries = [json.loads(x) for x in LOG.read_text().splitlines() if x.strip()]
    lines = ['# Phase 3R — Nhật ký forking paths L3R.6', '',
             'Người phụ trách: **Doan Van Tai**. Bản đọc được sinh từ',
             f'[forking_paths.jsonl](../../{LOG}) bằng `experiments/R3R_06_cards/render_log.py`;',
             'JSONL là nguồn. Mọi số là DISCOVERY trên pilot đã lộ, không phải evidence. Cột “Ai” = AI',
             'nghĩa là phiên triển khai chạy tóm tắt; lựa chọn giữ/bỏ là của tác giả (DL-073).', '',
             '| # | UTC | Ai | Luật / bảng | Đã xem | Giữ/Bỏ | Mục đích / lý do |', '|---|---|---|---|---|---|---|']
    for e in entries:
        lines.append('| ' + ' | '.join(str(c).replace('|', '\\|') for c in row(e)) + ' |')
    lines += ['', f'Tổng {len(entries)} dòng; 13 luật được tóm tắt trên discovery, 1 luật khai không nhìn dữ liệu.']
    OUT.write_text('\n'.join(lines) + '\n')
    print(OUT)


if __name__ == '__main__':
    sys.exit(main())
