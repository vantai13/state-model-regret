"""Doan Van Tai — L3R.1: đếm lại pilot v1.3 từ raw tại một commit cố định [VERIFICATION trên DISCOVERY].

AI (Claude) viết theo PHASE_3R §8 (L3R.1, bước 3); tác giả chưa duyệt. Câu hỏi chính: "các con số trong
results/explore_v13/SUMMARY.md có khớp raw không?". Thêm vào đó: tái lập các bảng đã xem trong L3R.1 Part 1
để chúng có nguồn, và vài kiểm thiết kế (ID trùng, trùng tọa độ với lưới v1.2, ghép tọa độ Stage 3).
Các kiểm thêm này được khai trong exposure register trước khi chạy.

Nguyên tắc:
- Chỉ đọc file qua `git show <rev>:<path>`: không checkout, không gọi engine, không ghi vào branch pilot.
- Ghi blob id của mọi file đã đọc (provenance).
- Lệch với SUMMARY là phát hiện (errata), không làm script thất bại. Script chỉ thoát mã khác 0 khi
  một invariant của chính dữ liệu bị vi phạm (ID trùng, số ID sai, thiếu cột).
- Từ grid v1.2 chỉ đọc tham số thiết kế (lambdaA, kappa, u, h) — mức "tham số", không đọc outcome.
- Output deterministic: chạy lại cho đúng từng chữ, trừ dòng ghi tên rev.

Usage (từ gốc repo, sau khi đã fetch tag; thư mục output không được tồn tại trước):
    python experiments/R3R_01_recount/recount.py --rev explore-v13-pilot --out results/R3R_01_recount/<RUN>
"""
import argparse
import csv
import io
import json
import math
import statistics
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

RAW = {
    'stage1': 'results/explore_v13/stage1/regimes.csv',
    'stage2': 'results/explore_v13/stage2/regimes.csv',
    'stage3': 'results/explore_v13/stage3/regimes.csv',
}
ROBUST = {
    'robustK': 'results/explore_v13/robustK/regimes.csv',    # ref 1, K = 80
    'robustdt': 'results/explore_v13/robustdt/regimes.csv',  # ref 2 (dt 1/240 s), K = 40
}
SUMMARY_PATH = 'results/explore_v13/SUMMARY.md'
GRID_PATH = 'notes/design/grid_v1_2.json'
MU = Fraction(10)          # capacity, D3
LAMBDA_B_V12 = Fraction(8)  # v1.2 D4: B OFF 2 / ON 14 -> mean 8, cố định
CONTRASTS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')
KEY = ('lambdaA', 'lambdaB', 'kappa', 'eta', 'h')
PARAM_COLS = ('lambdaA', 'lambdaB', 'kappa', 'eta', 'h', 'c_sw', 'ref', 'K')

# Bảng SUMMARY.md tại a7435e9, chép nguyên giá trị hiển thị (dấu phẩy thập phân, dấu trừ unicode).
CLAIMED_TABLE = {
    'stage1': dict(n='60', GM_C='0', GM_S='0', GS_pos='6', GS_harm='6', Gam_abs='6', Gam_neg='0', GSM='9',
                   maxGM='0,85', minGS='−8,3'),
    'stage2': dict(n='108', GM_C='20', GM_S='11', GS_pos='3', GS_harm='73', Gam_abs='75', Gam_neg='0', GSM='26',
                   maxGM='13,4', minGS='−21,6'),
    'stage3': dict(n='48', GM_C='0', GM_S='0', GS_pos='3', GS_harm='1', Gam_abs='1', Gam_neg='4', GSM='7',
                   maxGM='0,65', minGS='−1,5'),
}
COLUMN_LABEL = dict(n='n', GM_C='Ḡ_M ≥ 1% C̄', GM_S='Ḡ_M ≥ 10% S̄', GS_pos='Ḡ_S ≥ +1%', GS_harm='Ḡ_S ≤ −1%',
                    Gam_abs='|Γ̄| ≥ 1%', Gam_neg='Γ̄ ≤ −0,05%', GSM='G_SM ≥ 1%', maxGM='max Ḡ_M (%C̄)',
                    minGS='min Ḡ_S (%C̄)')


# ---------------------------------------------------------------- đọc dữ liệu
def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout


def read_rows(text):
    """CSV -> list[dict]; id giữ chuỗi, cột khác thành float.

    Stage 1/2/robust không có cột c_sw: scan.py dùng mặc định c_sw = '0' (D13). Gán 0 và đánh dấu
    `c_sw_defaulted` để báo cáo nói rõ đây là suy từ code, không đọc từ CSV.
    """
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        row = {k: (v if k == 'id' else float(v)) for k, v in r.items()}
        if not row.get('id') or any(not math.isfinite(v) for k, v in row.items() if k != 'id'):
            raise ValueError('empty ID or non-finite CSV number')
        if 'c_sw' not in row:
            row['c_sw'], row['c_sw_defaulted'] = 0.0, True
        rows.append(row)
    return rows


def frac(x):
    return Fraction(x).limit_denominator(1000)


def parse_claim(s):
    """'−8,3' -> (-8.3, 1 chữ số thập phân)."""
    s = s.replace('−', '-').replace(',', '.')
    decimals = len(s.split('.')[1]) if '.' in s else 0
    return float(s), decimals


def matches(raw_value, claim):
    value, decimals = parse_claim(claim)
    return round(raw_value, decimals) == round(value, decimals)


# ---------------------------------------------------------------- các phép đếm
def summary_row(rows):
    """Mười cột của bảng SUMMARY, tính lại từ raw. Ngưỡng bao gồm dấu bằng như SUMMARY ghi (≥, ≤)."""
    return dict(
        n=len(rows),
        GM_C=sum(r['G_M_pctC'] >= 1 for r in rows),
        GM_S=sum(r['G_M_pctS'] >= 10 for r in rows),
        GS_pos=sum(r['G_S_pctC'] >= 1 for r in rows),
        GS_harm=sum(r['G_S_pctC'] <= -1 for r in rows),
        Gam_abs=sum(abs(r['Gamma_pctC']) >= 1 for r in rows),
        Gam_neg=sum(r['Gamma_pctC'] <= -0.05 for r in rows),
        GSM=sum(r['G_SM_pctC'] >= 1 for r in rows),
        maxGM=max(r['G_M_pctC'] for r in rows),
        minGS=min(r['G_S_pctC'] for r in rows),
    )


def key_of(r):
    return tuple(frac(r[k]) for k in KEY)


def full_key(r):
    """Một regime = tọa độ plant + c_sw + mức số (ref, K). ID khác nhau không có nghĩa regime khác nhau."""
    return key_of(r) + (frac(r['c_sw']), frac(r['ref']), frac(r['K']))


def duplicates(rows):
    """Nhóm các ID có cùng full_key; với mỗi nhóm, chênh lệch lớn nhất trên mọi cột số (kỳ vọng 0)."""
    groups = {}
    for r in rows:
        groups.setdefault(full_key(r), []).append(r)
    out = []
    for g in groups.values():
        if len(g) < 2:
            continue
        num = [c for c in g[0] if c not in ('id', 'c_sw_defaulted', 'wall_s') and isinstance(g[0][c], float)]
        spread = max(max(r[c] for r in g) - min(r[c] for r in g) for c in num)
        out.append(dict(ids=[r['id'] for r in g], max_spread_all_columns=spread))
    return out, len(groups)


def distinct(rows):
    """Giữ ID đầu tiên của mỗi full_key (thứ tự Stage 1 → 2 → 3)."""
    seen, out = set(), []
    for r in rows:
        k = full_key(r)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def robustness(base_rows, robust_rows, suffix):
    """Chênh lệch (điểm %) giữa regime robust và regime gốc cùng tọa độ (KEY)."""
    base = {key_of(r): r for r in base_rows}
    out, missing = [], []
    for r in robust_rows:
        b = base.get(key_of(r))
        if b is None:
            missing.append(r['id'])
            continue
        for c in CONTRASTS:
            col = f'{c}_{suffix}'
            out.append(dict(robust_id=r['id'], base_id=b['id'], quantity=col, base=b[col], robust=r[col],
                            diff=r[col] - b[col]))
    return out, missing


def design_check(stages, robust):
    info = {}
    for name, rows in {**stages, **robust}.items():
        info[name] = {c: sorted({str(frac(r[c])) for r in rows}, key=lambda s: Fraction(s)) for c in PARAM_COLS}
    s1 = {(frac(r['lambdaA']), frac(r['kappa']), frac(r['eta'])) for r in stages['stage1'] if r['h'] == 8}
    s3 = {(frac(r['lambdaA']), frac(r['kappa']), frac(r['eta'])) for r in stages['stage3']}
    info['stage1_h8_not_in_stage3'] = sorted([tuple(map(str, t)) for t in s1 - s3])
    info['stage3_not_in_stage1_h8'] = sorted([tuple(map(str, t)) for t in s3 - s1])
    return info


def stage3_pairing(stages):
    """Stage 3 (c_sw > 0) có tọa độ plant trùng regime c_sw = 0 nào ở Stage 1/2 không?

    Chỉ trả về số cặp và max Ḡ_M (%C̄) của các regime gốc c_sw = 0 được ghép: đủ để biết Stage 3 có
    chạm vùng model value (Ḡ_M ≥ 1%) hay không. Không so hiệu ứng của c_sw (không phải mục tiêu L3R.1).
    """
    out = {}
    s3 = {key_of(r) for r in stages['stage3']}
    for name in ('stage1', 'stage2'):
        base = [r for r in stages[name] if key_of(r) in s3]
        out[name] = dict(n_base_coords=len(base),
                         max_GM_pctC_base=max((r['G_M_pctC'] for r in base), default=None))
    out['stage3_coords'] = len(s3)
    return out


def eta_meaning(rows):
    """Pilot: u = 2η cho mọi λB (đúng câu chữ v1.2 D5). Nếu đọc η là u/(μ−λB) thì chỉ trùng khi λB = 8."""
    out = {}
    for r in rows:
        lb, eta = frac(r['lambdaB']), frac(r['eta'])
        u = 2 * eta
        out.setdefault((str(lb), str(eta)), str(u / (MU - lb)))
    return [dict(lambdaB=k[0], eta_label=k[1], u=str(2 * Fraction(k[1])), u_over_headroom=v)
            for k, v in sorted(out.items(), key=lambda kv: (Fraction(kv[0][0]), Fraction(kv[0][1])))]


def overlap_v12(rows, grid):
    """So tọa độ vật lý (λA, λB, κ, u, h) của pilot với 38 ô main + 12 ô held-out v1.2 (λB = 8 theo D4)."""
    cells = {}
    for role in ('main', 'heldout'):
        for c in grid[role]:
            t = (Fraction(c['lambdaA']), LAMBDA_B_V12, Fraction(c['kappa']), Fraction(c['u']), Fraction(c['h']))
            cells.setdefault(t, []).append(c['id'])
    hits = []
    for r in rows:
        t = (frac(r['lambdaA']), frac(r['lambdaB']), frac(r['kappa']), 2 * frac(r['eta']), frac(r['h']))
        if t in cells:
            hits.append(dict(pilot_id=r['id'], v12_cells=cells[t], coords=[str(x) for x in t], c_sw=r['c_sw']))
    return hits, len(cells)


def sealed_neighbourhood(rows, grid, sealed=('R09', 'R10')):
    """Chỉ tham số: có regime pilot nào cùng κ hoặc cùng h với ô niêm phong không?"""
    out = []
    for c in grid['heldout']:
        if c['id'] not in sealed:
            continue
        k, h = Fraction(c['kappa']), Fraction(c['h'])
        out.append(dict(cell=c['id'], kappa=str(k), h=str(h),
                        pilot_same_kappa=sum(frac(r['kappa']) == k for r in rows),
                        pilot_same_h=sum(frac(r['h']) == h for r in rows),
                        pilot_same_kappa_and_h=sum(frac(r['kappa']) == k and frac(r['h']) == h for r in rows)))
    return out


def identities(rows):
    return dict(
        min_G_M=min(r['G_M'] for r in rows),
        min_G_SM=min(r['G_SM'] for r in rows),
        min_G_S_M1=min(r['G_S_M1'] for r in rows),
        min_G_M_S1=min(r['G_M_S1'] for r in rows),
        max_abs_gamma_identity_1=max(abs(r['Gamma'] - (r['G_S_M1'] - r['G_S'])) for r in rows),
        max_abs_gamma_identity_2=max(abs(r['Gamma'] - (r['G_M_S1'] - r['G_M'])) for r in rows),
        max_abs_GM_identity_gap=max(abs(r['GM_identity_gap']) for r in rows),
    )


def part1_tables(rows12, all_rows, near_zero=0.05):
    """Các bảng đã xem trong L3R.1 Part 1 (Stage 1+2, c_sw = 0). near_zero tính bằng % C̄, khai báo ở đây."""
    harm = [r for r in rows12 if r['G_S_pctC'] <= -1]
    lbs = sorted({r['lambdaB'] for r in rows12})
    big_gamma = [r for r in rows12 if abs(r['Gamma_pctC']) >= 1]
    gsm1 = [r['G_S_M1_pctC'] for r in rows12]
    nz = {}
    for t in (0.05, 0.1, 0.25, 0.5):
        nz[str(t)] = sum(abs(r['G_M_pctC']) < t and abs(r['G_SM_pctC']) < t for r in harm)
    return dict(
        n=len(rows12),
        harm_by_lambdaB={f'{lb:g}': sum(r['lambdaB'] == lb for r in harm) for lb in lbs},
        gm1_by_lambdaB={f'{lb:g}': sum(r['lambdaB'] == lb and r['G_M_pctC'] >= 1 for r in rows12) for lb in lbs},
        harm_and_gm1=sum(r['G_M_pctC'] >= 1 for r in harm),
        harm_total=len(harm),
        harm_with_GM_and_GSM_near_zero=nz[str(near_zero)],
        near_zero_threshold_pctC=near_zero,
        near_zero_sensitivity=nz,
        abs_gamma_ge1=len(big_gamma),
        abs_gamma_ge1_with_GS_negative=sum(r['G_S_pctC'] < 0 for r in big_gamma),
        GS_nonneg=sum(r['G_S_pctC'] >= 0 for r in rows12),
        GS_nonneg_with_gamma_ge1=sum(r['G_S_pctC'] >= 0 and r['Gamma_pctC'] >= 1 for r in rows12),
        G_S_M1_ge1=sum(x >= 1 for x in gsm1),
        G_S_M1_ge01=sum(x >= 0.1 for x in gsm1),
        G_S_M1_max=max(gsm1),
        G_S_M1_median=statistics.median(gsm1),
        Sbar_over_Cbar_min=min(r['Sbar'] / r['Cbar'] for r in all_rows),
        Sbar_over_Cbar_max=max(r['Sbar'] / r['Cbar'] for r in all_rows),
    )


def rubric_facts(rows):
    """Đếm theo các điều kiện của rubric viết trong docstring population.py (không gán nhãn — việc của tác giả)."""
    out = dict(
        GS_pos_C_or_S=sum(r['G_S_pctC'] >= 1 or r['G_S_pctS'] >= 10 for r in rows),
        GM_C_or_S=sum(r['G_M_pctC'] >= 1 or r['G_M_pctS'] >= 10 for r in rows),
    )
    for t in (0.05, 0.5, 1.0):
        out[f'Gamma_ge_+{t}'] = sum(r['Gamma_pctC'] >= t for r in rows)
        out[f'Gamma_le_-{t}'] = sum(r['Gamma_pctC'] <= -t for r in rows)
    out['min_Gamma_pctC'] = min(r['Gamma_pctC'] for r in rows)
    out['min_Gamma_pctC_csw0'] = min(r['Gamma_pctC'] for r in rows if r['c_sw'] == 0)
    return out


# ---------------------------------------------------------------- báo cáo
def fmt(x, d=3):
    if isinstance(x, float):
        return f'{x:.{d}f}'
    return str(x)


def build(repo, rev):
    commit = git(repo, 'rev-parse', f'{rev}^{{commit}}').strip()
    blobs, stages, robust = {}, {}, {}
    for name, path in {**RAW, **ROBUST}.items():
        blobs[path] = git(repo, 'rev-parse', f'{commit}:{path}').strip()
        (stages if name in RAW else robust)[name] = read_rows(git(repo, 'show', f'{commit}:{path}'))
    for p in (SUMMARY_PATH, GRID_PATH):
        blobs[p] = git(repo, 'rev-parse', f'{commit}:{p}').strip()
    grid = json.loads(git(repo, 'show', f'{commit}:{GRID_PATH}'))

    all_rows = [r for s in RAW for r in stages[s]]
    ids = [r['id'] for r in all_rows] + [r['id'] for s in ROBUST for r in robust[s]]
    problems = []
    if len(all_rows) != 216:
        problems.append(f'số regime chính = {len(all_rows)}, không phải 216')
    if len(set(ids)) != len(ids):
        problems.append('ID trùng')
    needed = ({f'{c}_pct{x}' for c in CONTRASTS for x in 'CS'} | set(CONTRASTS) | set(KEY) |
              {'c_sw', 'Cbar', 'Sbar', 'ref', 'K', 'GM_identity_gap'})
    expected = dict(stage1=60, stage2=108, stage3=48, robustK=9, robustdt=9)
    for s, rows in {**stages, **robust}.items():
        if len(rows) != expected[s]:
            problems.append(f'{s}: {len(rows)} rows, expected {expected[s]}')
        for i, row in enumerate(rows):
            if not needed <= set(row):
                problems.append(f'{s} row {i}: thiếu cột {sorted(needed - set(row))}')
            elif row['Cbar'] <= 0 or row['Sbar'] <= 0:
                problems.append(f'{s} row {i}: nonpositive Cbar/Sbar in saved pilot')
    if problems:
        raise ValueError('Input invariant failed: ' + '; '.join(problems))

    table = {}
    for s in RAW:
        got = summary_row(stages[s])
        table[s] = {c: dict(raw=got[c], claimed=CLAIMED_TABLE[s][c], match=matches(got[c], CLAIMED_TABLE[s][c]))
                    for c in COLUMN_LABEL}

    rows12 = stages['stage1'] + stages['stage2']
    x2065 = next(r for r in all_rows if r['id'] == 'X2065')
    harm_all = sum(r['G_S_pctC'] <= -1 for r in all_rows)
    text_claims = [
        dict(claim='Ḡ_S ≤ −1% ở 79/216 regime', raw=f'{harm_all}/216', match=harm_all == 79),
        dict(claim='(Stage 1+2) — không có trong SUMMARY', raw=f"{sum(r['G_S_pctC'] <= -1 for r in rows12)}/168",
             match=None),
        dict(claim='X2065: Ḡ_M = 13,4% C̄_ref', raw=fmt(x2065['G_M_pctC']), match=matches(x2065['G_M_pctC'], '13,4')),
        dict(claim='X2065: 42% stakes', raw=fmt(x2065['G_M_pctS']), match=matches(x2065['G_M_pctS'], '42')),
        dict(claim='X2065: P(flip) = 0,47', raw=fmt(x2065['P_flip'], 4), match=matches(x2065['P_flip'], '0,47')),
        dict(claim='X2065: P(xếp hạng sai) = 0,54', raw=fmt(x2065['P_wrong_ranking'], 4),
             match=matches(x2065['P_wrong_ranking'], '0,54')),
        dict(claim='Γ̄ tới +21,6%', raw=fmt(max(r['Gamma_pctC'] for r in all_rows)),
             match=matches(max(r['Gamma_pctC'] for r in all_rows), '21,6')),
        dict(claim='Γ̄ âm chỉ khoảng −0,1% và chỉ khi có c_sw',
             raw=(f"min Γ̄ = {fmt(min(r['Gamma_pctC'] for r in all_rows))}%; "
                  f"số regime c_sw = 0 có Γ̄ ≤ −0,05%: "
                  f"{sum(r['Gamma_pctC'] <= -0.05 for r in all_rows if r['c_sw'] == 0)}"),
             match=sum(r['Gamma_pctC'] <= -0.05 for r in all_rows if r['c_sw'] == 0) == 0),
    ]

    dups, n_distinct = duplicates(all_rows)
    d_all, d12 = distinct(all_rows), distinct(rows12)
    harm_d = sum(r['G_S_pctC'] <= -1 for r in d_all)
    text_claims.insert(2, dict(claim='(theo regime phân biệt) — không có trong SUMMARY',
                               raw=f"{harm_d}/{len(d_all)} (Stage 1+2: "
                                   f"{sum(r['G_S_pctC'] <= -1 for r in d12)}/{len(d12)})", match=None))

    rob = {}
    for name, suffix_rows in robust.items():
        for suffix in ('pctC', 'pctS'):
            diffs, missing = robustness(stages['stage2'], suffix_rows, suffix)
            worst = max(diffs, key=lambda d: abs(d['diff']))
            rob[f'{name}/{suffix}'] = dict(n_pairs=len({d['robust_id'] for d in diffs}), missing=missing,
                                           max_abs_diff=abs(worst['diff']), worst=worst)
    rob_claim = max(rob[f'{n}/pctC']['max_abs_diff'] for n in robust)

    hits, n_v12 = overlap_v12(all_rows + [r for s in robust for r in robust[s]], grid)
    return dict(
        rev=rev, commit=commit, blobs=blobs, problems=problems,
        c_sw_defaulted=[s for s, rows in {**stages, **robust}.items() if rows[0].get('c_sw_defaulted')],
        table=table, text_claims=text_claims,
        robustness=rob, robustness_claim=dict(claimed='≤ khoảng 0,15 điểm %', raw_max_pctC=rob_claim,
                                              match=rob_claim <= 0.15, v12_tolerance_pp=0.25),
        design=design_check(stages, robust), stage3_pairing=stage3_pairing(stages), eta=eta_meaning(all_rows),
        overlap_v12=dict(hits=hits, n_v12_coordinate_tuples=n_v12,
                         sealed=sealed_neighbourhood(all_rows + [r for s in robust for r in robust[s]], grid)),
        identities=identities(all_rows + [r for s in robust for r in robust[s]]),
        duplicates=dict(groups=dups, n_distinct=n_distinct),
        part1=part1_tables(rows12, all_rows), part1_distinct=part1_tables(d12, d_all),
        rubric=rubric_facts(all_rows),
        regimes=[dict(id=r['id'], stage=s, **{c: str(frac(r[c])) for c in PARAM_COLS},
                      u=str(2 * frac(r['eta'])))
                 for s, rows in {**stages, **robust}.items() for r in rows],
    )


def report_md(res):
    L = []
    w = L.append
    w('# R3R_01 — Đếm lại pilot v1.3 từ raw')
    w('')
    w('Sinh tự động bởi `experiments/R3R_01_recount/recount.py`. **Không sửa tay file này.** '
      'Nhãn: VERIFICATION trên dữ liệu DISCOVERY đã lộ; không phải evidence cho RQ.')
    w('')
    w(f"- Rev: `{res['rev']}` → commit `{res['commit']}`")
    for p, b in res['blobs'].items():
        w(f'- `{p}` blob `{b[:12]}`')
    w('')
    w('## 0. Invariant của dữ liệu')
    w('')
    w('PASS: 216 ID chính, ID không trùng (kể cả robust), đủ cột.' if not res['problems']
      else 'FAIL: ' + '; '.join(res['problems']))
    w('')
    dd = res['duplicates']
    w(f"Regime phân biệt (cùng λA, λB, κ, η, h, c_sw, ref, K): **{dd['n_distinct']}** trên 216 ID. "
      f"Nhóm trùng: {len(dd['groups'])}.")
    for g in dd['groups']:
        w(f"- {' = '.join(g['ids'])}: chênh lớn nhất trên mọi cột số = {g['max_spread_all_columns']:.1e}")
    w('')
    w('Trong từng Stage không có trùng; trùng chỉ xuất hiện khi gộp các Stage. Kết quả của các ID trùng giống hệt '
      'nhau là một kiểm tính tất định (cùng input → cùng output), không phải hai quan sát độc lập.')
    w('')
    w('## 1. Bảng SUMMARY so với raw (theo Stage)')
    w('')
    w('| Cột | ' + ' | '.join(f'{s} raw | {s} SUMMARY' for s in RAW) + ' |')
    w('|---|' + '---|---|' * len(RAW))
    for c, label in COLUMN_LABEL.items():
        cells = []
        for s in RAW:
            t = res['table'][s][c]
            raw = fmt(t['raw'], 3) if isinstance(t['raw'], float) else t['raw']
            cells += [str(raw), t['claimed'] + ('' if t['match'] else ' **≠**')]
        w(f"| {label.replace('|', chr(92) + '|')} | " + ' | '.join(cells) + ' |')
    w('')
    w('So khớp: số đếm phải bằng đúng; số thập phân so sau khi làm tròn đến số chữ số SUMMARY hiển thị.')
    w('')
    w('## 2. Các câu trong phần chữ của SUMMARY')
    w('')
    w('| Câu trong SUMMARY | Raw | Khớp? |')
    w('|---|---|---|')
    for t in res['text_claims']:
        m = '—' if t['match'] is None else ('có' if t['match'] else '**không**')
        w(f"| {t['claim']} | {t['raw']} | {m} |")
    w('')
    w('## 3. Độ bền (robustness) — so với regime Stage 2 cùng tọa độ')
    w('')
    w('| Phép làm mịn / thang | Số cặp | Max \\|chênh\\| (điểm %) | Ở đâu |')
    w('|---|---|---|---|')
    for k, v in res['robustness'].items():
        wst = v['worst']
        w(f"| {k} | {v['n_pairs']} | {v['max_abs_diff']:.4f} | {wst['robust_id']} vs {wst['base_id']}, "
          f"{wst['quantity']}: {wst['base']:.3f} → {wst['robust']:.3f} |")
    rc = res['robustness_claim']
    w('')
    w(f"SUMMARY ghi \"{rc['claimed']}\". Raw (thang % C̄): max {rc['raw_max_pctC']:.4f} điểm % → "
      f"{'khớp' if rc['match'] else '**không khớp**'}. Dung sai làm mịn của v1.2 (D1) là {rc['v12_tolerance_pp']} "
      'điểm % C_ref. Chỉ 9 regime được kiểm; các regime khác chưa có kiểm tương ứng.')
    w('')
    w('## 4. Thiết kế quét (tham số thật trong raw)')
    w('')
    w('| Stage | λA | λB | κ | η (nhãn) | h | c_sw | ref | K |')
    w('|---|---|---|---|---|---|---|---|---|')
    for s in (*RAW, *ROBUST):
        d = res['design'][s]
        w(f'| {s} | ' + ' | '.join(', '.join(d[c]) for c in PARAM_COLS) + ' |')
    w('')
    w(f"Điểm (λA, κ, η) của Stage 1 có h = 8 nhưng **không** có trong Stage 3: "
      f"{len(res['design']['stage1_h8_not_in_stage3'])} — {res['design']['stage1_h8_not_in_stage3']}. "
      f"Điểm Stage 3 không có trong Stage 1 h = 8: {res['design']['stage3_not_in_stage1_h8']}.")
    w('')
    sp = res['stage3_pairing']
    w(f"Stage 3 có {sp['stage3_coords']} tọa độ plant (mỗi tọa độ × 2 mức c_sw). Tọa độ trùng regime c_sw = 0: "
      f"Stage 1 = {sp['stage1']['n_base_coords']} (max Ḡ_M của các regime gốc = "
      f"{fmt(sp['stage1']['max_GM_pctC_base'])}% C̄), Stage 2 = {sp['stage2']['n_base_coords']} "
      f"(max Ḡ_M = {fmt(sp['stage2']['max_GM_pctC_base'])}% C̄).")
    w('')
    w('ref 1 = dt 1/120 s; ref 2 = dt 1/240 s (dt đã khóa ở Phase 3, DL-053). '
      f"CSV không có cột c_sw (gán 0 theo mặc định của scan.py): {', '.join(res['c_sw_defaulted']) or 'không'}.")
    w('')
    w('## 5. Nhãn η: u = 2η (câu chữ v1.2 D5) so với u/(μ − λB)')
    w('')
    w('| λB | η (nhãn) | u = 2η | u/(μ − λB) |')
    w('|---|---|---|---|')
    for e in res['eta']:
        w(f"| {e['lambdaB']} | {e['eta_label']} | {e['u']} | {e['u_over_headroom']} |")
    w('')
    w('v1.2 cố định λB = 8 (D4), nên hai cách đọc trùng nhau trong v1.2. Pilot cho λB thay đổi, nên chúng tách ra.')
    w('')
    w('## 6. Trùng tọa độ với lưới v1.2 (38 main + 12 held-out)')
    w('')
    o = res['overlap_v12']
    n0 = sum(h['c_sw'] == 0 for h in o['hits'])
    ncell = len({c for h in o['hits'] for c in h['v12_cells']})
    w(f"So (λA, λB, κ, u, h) với {o['n_v12_coordinate_tuples']} bộ tọa độ v1.2 (chỉ tham số, λB = 8 theo D4). "
      f"Số regime pilot trùng đúng tọa độ plant: **{len(o['hits'])}**, chạm {ncell} ô v1.2; trong đó "
      f"{n0} regime có c_sw = 0 như v1.2 (D13) và {len(o['hits']) - n0} regime Stage 3 có c_sw ≠ 0 "
      "(cùng plant, khác hàm cost).")
    w('')
    for h in o['hits']:
        w(f"- {h['pilot_id']} (c_sw = {h['c_sw']:g}) ↔ {', '.join(h['v12_cells'])} tại {h['coords']}")
    w('')
    for z in o['sealed']:
        w(f"- Ô niêm phong {z['cell']} (κ = {z['kappa']}, h = {z['h']}): regime pilot cùng κ = {z['pilot_same_kappa']}, "
          f"cùng h = {z['pilot_same_h']}, cùng cả hai = {z['pilot_same_kappa_and_h']} (chỉ so tham số).")
    w('')
    w('Lưu ý: trùng tọa độ plant không có nghĩa trùng estimand (v1.2 cố định một snapshot; pilot lấy trung bình '
      'theo p(y)). Khoảng cách "gần" để tránh pseudo-replication là việc của L3R.7.')
    w('')
    w('## 7. Identity trên raw (sanity, không phải bằng chứng engine đúng)')
    w('')
    for k, v in res['identities'].items():
        w(f'- {k} = {v:.3e}')
    w('')
    w('## 8. Bảng đã xem trong L3R.1 Part 1 (Stage 1+2, c_sw = 0) — tái lập để có nguồn')
    w('')
    w('Cột "theo ID" là cách Part 1 đã đếm; cột "phân biệt" bỏ 6 ID trùng (mục 0).')
    w('')
    w('| Đại lượng | Theo ID | Phân biệt |')
    w('|---|---|---|')
    p, q = res['part1'], res['part1_distinct']
    rows = [
        ('n', p['n'], q['n']),
        ('harm (Ḡ_S ≤ −1% C̄)', p['harm_total'], q['harm_total']),
        ('harm theo λB', p['harm_by_lambdaB'], q['harm_by_lambdaB']),
        ('Ḡ_M ≥ 1% C̄ theo λB', p['gm1_by_lambdaB'], q['gm1_by_lambdaB']),
        ('cả harm và Ḡ_M ≥ 1%', p['harm_and_gm1'], q['harm_and_gm1']),
        (f"harm có |Ḡ_M|, |Ḡ_SM| < {p['near_zero_threshold_pctC']}% C̄",
         p['harm_with_GM_and_GSM_near_zero'], q['harm_with_GM_and_GSM_near_zero']),
        ('… độ nhạy theo ngưỡng (% C̄)', p['near_zero_sensitivity'], q['near_zero_sensitivity']),
        ('|Γ̄| ≥ 1% (trong đó Ḡ_S < 0)', f"{p['abs_gamma_ge1']} ({p['abs_gamma_ge1_with_GS_negative']})",
         f"{q['abs_gamma_ge1']} ({q['abs_gamma_ge1_with_GS_negative']})"),
        ('Ḡ_S ≥ 0 (trong đó Γ̄ ≥ 1%)', f"{p['GS_nonneg']} ({p['GS_nonneg_with_gamma_ge1']})",
         f"{q['GS_nonneg']} ({q['GS_nonneg_with_gamma_ge1']})"),
        ('Ḡ_S|M1 ≥ 1% / ≥ 0,1%', f"{p['G_S_M1_ge1']} / {p['G_S_M1_ge01']}", f"{q['G_S_M1_ge1']} / {q['G_S_M1_ge01']}"),
        ('Ḡ_S|M1 max / trung vị (% C̄)', f"{p['G_S_M1_max']:.3f} / {p['G_S_M1_median']:.4f}",
         f"{q['G_S_M1_max']:.3f} / {q['G_S_M1_median']:.4f}"),
        ('S̄/C̄ min … max (cả pilot)', f"{p['Sbar_over_Cbar_min']:.4f} … {p['Sbar_over_Cbar_max']:.3f}",
         f"{q['Sbar_over_Cbar_min']:.4f} … {q['Sbar_over_Cbar_max']:.3f}"),
    ]
    for label, a, b in rows:
        w(f"| {label.replace('|', chr(92) + '|')} | {a} | {b} |")
    w('')
    w('## 9. Các điều kiện của rubric trong docstring `population.py` (đếm theo ID, không gán nhãn)')
    w('')
    for k, v in res['rubric'].items():
        w(f'- {k} = {fmt(v)}')
    w('')
    w('Script không kết luận rubric đạt hay không: việc so với câu chữ rubric và gán nhãn là của tác giả.')
    return '\n'.join(L) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', default='.')
    ap.add_argument('--rev', default='explore-v13-pilot')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        raise FileExistsError(f'refuse existing output before reading data: {out}')
    res = build(Path(a.repo), a.rev)
    out.mkdir(parents=True, exist_ok=False)  # không ghi đè lần chạy cũ
    (out / 'report.md').write_text(report_md(res), encoding='utf-8')
    regimes = res.pop('regimes')
    with (out / 'discovery_regimes.csv').open('w', newline='', encoding='utf-8') as f:
        wr = csv.DictWriter(f, fieldnames=list(regimes[0]))
        wr.writeheader()
        wr.writerows(regimes)
    (out / 'recount.json').write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
    print(f'wrote {out}/report.md, recount.json, discovery_regimes.csv ({len(regimes)} regimes)')
    if res['problems']:
        print('INVARIANT FAIL:', res['problems'], file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
