"""Doan Van Tai — L3R.6 logged discovery summaries for drawing regions (DISCOVERY ONLY).

Steps (each appends to the forking-paths log):
  --entry0      record what was seen before any rule (lesson tables, earlier records)
  --part-a      reproduce the lesson's Part 2 discovery tables from saved pilot raw
  --candidates  summarize the candidate rules fixed in CANDIDATES below (committed first)
Guards: the log's entry 0 and this source must be committed before --part-a/--candidates.
Never: engine call, new regime, CF/R09/R10 outcome, outcome-defined region.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from experiments.R3R_06_cards import discovery as D
from experiments.R3R_06_cards.regions import Box, sealed_and_exposed

OUT = Path('results/lessons/l3r_6')
LOG = OUT / 'forking_paths.jsonl'
SRC = ('experiments/R3R_06_cards/run_discovery.py', 'experiments/R3R_06_cards/discovery.py',
       'experiments/R3R_06_cards/regions.py')
WHO = 'AI (Claude) theo yêu cầu triển khai L3R.6 của Doan Van Tai'
MV, SH = ('G_M_pctC', '>=', 1), ('G_S_pctC', '<=', -1)

# Fixed scope pins shared by every candidate: primary c_sw=0, u in the pilot range.
U = ('u', '1', '3/2')
C0 = ('c_sw', '0', '0')


def box(rule_id, role, *bounds, note=''):
    return Box(rule_id, tuple(bounds) + (U, C0), role=role, note=note)


CANDIDATES = [
    box('MV+A', 'MV_plus', ('lambdaB', '8', '8'), ('lambdaA', '7', '15/2'), ('kappa', '1/10', '3/10'), ('h', '12', '16'),
        note='lesson illustrative box; hugs the 16 seen points'),
    box('MV+B', 'MV_plus', ('lambdaB', '8', '8'), ('lambdaA', '7', '15/2'), ('kappa', '1/10', '3/10'), ('h', '8', '16'),
        note='wider horizon, includes kappa=.3/h=8'),
    box('MV-ii', 'MV_minus', ('lambdaB', '8', '8'), ('lambdaA', '7', '15/2'), ('kappa', '1', '3'), ('h', '12', '16'),
        note='flip kappa only; pilot never sampled this box (extrapolation)'),
    box('MV-i', 'MV_minus', ('lambdaB', '6', '7'), ('lambdaA', '7', '15/2'), ('kappa', '1/10', '3/10'), ('h', '12', '16'),
        note='flip headroom only; risk of obviousness'),
    box('MV-BND', 'MV_bnd', ('lambdaB', '8', '8'), ('lambdaA', '7', '15/2'), ('kappa', '3/10', '1'), ('h', '12', '16'),
        note='descriptive band between plus and minus kappa'),
    box('SH+A', 'SH_plus', ('lambdaB', '6', '7'), ('lambdaA', '7', '8'), ('kappa', '1/10', '3/10'), ('h', '8', '16'),
        note='B with headroom'),
    box('SH+B', 'SH_plus', ('lambdaB', '6', '8'), ('lambdaA', '7', '8'), ('kappa', '1/10', '3/10'), ('h', '8', '16'),
        note='includes lambdaB=8 and overlaps MV'),
    box('SH-ii', 'SH_minus', ('lambdaB', '6', '7'), ('lambdaA', '7', '8'), ('kappa', '1', '3'), ('h', '8', '16'),
        note='flip kappa only; pilot never sampled this box (extrapolation)'),
    box('SH-i', 'SH_minus', ('lambdaB', '8', '8'), ('lambdaA', '7', '8'), ('kappa', '1/10', '3/10'), ('h', '8', '16'),
        note='flip headroom to lambdaB=8'),
    box('G-A', 'Gamma', ('lambdaB', '8', '8'), ('lambdaA', '7', '15/2'), ('kappa', '1/10', '3/10'), ('h', '12', '16'),
        note='same box as MV+A'),
    box('G-B', 'Gamma', ('lambdaB', '8', '8'), ('lambdaA', '15/2', '15/2'), ('kappa', '1/10', '3/10'), ('h', '12', '16'),
        note='lambdaA near 7.5 to reduce harm regimes'),
    box('G-C', 'Gamma', ('lambdaB', '8', '8'), ('lambdaA', '7', '8'), ('kappa', '1/10', '3/10'), ('h', '8', '16'),
        note='broader lambdaB=8 slow-B box'),
]

GAMMA_PRED = {
    'GS_nonneg': ('G_S_pctC', '>=', 0),
    'informative_min_gt_epsE': ('min(G_S_pctC,G_M_pctC)', '>', 0.5),
    'Gamma_meets': ('Gamma_pctC', '>=', -0.5),
    'Gamma_fails': ('Gamma_pctC', '<', -0.5),
    'Gamma_negative': ('Gamma_pctC', '<', 0),
}


def _git(*a): return subprocess.run(['git', *a], check=True, capture_output=True).stdout


def require_committed():
    committed = _git('show', f'HEAD:{LOG}')
    first = json.loads(committed.splitlines()[0])
    if first.get('seq') != 0 or first.get('kind') != 'exposure_before_rules':
        raise SystemExit('entry 0 missing from committed log')
    if not LOG.read_bytes().startswith(committed):
        raise SystemExit('log is not an append-only extension of the committed log')
    if subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', *SRC]).returncode:
        raise SystemExit('commit candidate rules/source before reading outcomes')


def entry0():
    log = D.ForkingLog(LOG)
    if log.entries(): raise SystemExit('log already started')
    log.append(dict(kind='exposure_before_rules', who='AI (lesson author, Part 2) + phiên triển khai',
        purpose='Mục 0: những gì đã xem trước khi viết luật vùng',
        seen=['Lesson Part 2 bốn bảng: phủ (lambdaB,kappa,h) kèm số MV/SH; danh sách lambdaB=8,kappa<=.3,h>=8; '
              'MV theo lambdaA ở lambdaB=8; góc lambdaA=8',
              'Lesson Part 2 số trích: rhoA=.9 cặp (8,1)->G_M 0.00 và (7.5,1.5)->5.85..13.41; G_S -8.47..-21.57 '
              'ở lambdaB=8,lambdaA=7; G_M 1.33..2.56 ở kappa=.3; SH 36/36,21/36,0/40,0/20',
              'Lesson Part 1 §8: S1..S10 từ discovery record §5 và DL-063',
              'Discovery record §2-§6, L3R.4 overlay MV20/SH80/giao14, contract/T07 đã đọc trước phiên'],
        tooling_note='tests/test_r3r_06_cards.py nạp outcome của pilot chỉ để kiểm 6 cặp trùng có chênh 0 '
                     '(E4 đã biết); không tạo bảng/tóm tắt',
        rules_tried=0, pilot_commit=D.PILOT_COMMIT, git_head=D.head()))
    print(f'entry 0 written to {LOG}')


def cell(lb, k, h):
    return Box(f'cell lB{lb} k{k} h{h}', (('lambdaB', lb, lb), ('kappa', k, k), ('h', h, h), C0))


def part_a(disc, log):
    res = {}
    cells = [(f'lB={lb},kappa={k},h={h}', cell(lb, k, h)) for lb in ('6', '7', '8')
             for k in ('1/10', '3/10', '1', '3') for h in ('2', '8', '12', '16')]
    rows = D.table(disc, cells, dict(MV=MV, SH=SH), log, who=WHO, purpose='Part2 §5.1 coverage reproduction')
    res['coverage'] = [r for r in rows if r['n']]
    res['mv_by_lambdaA_lB8'] = D.table(disc, [(f'lambdaA={a}', Box(f'lA{a}', (('lambdaB', '8', '8'), ('lambdaA', a, a),
                                       ('kappa', '1/10', '3/10'), ('h', '12', '16'), C0)))
                                       for a in ('6', '13/2', '7', '15/2', '8')], dict(MV=MV, SH=SH), log, who=WHO,
                                       purpose='Part2 table 3: MV by lambdaA at lambdaB=8, kappa<=.3, h>=12')
    res['rhoA_pair'] = D.values(disc, Box('rhoA.9', (('lambdaB', '8', '8'), ('kappa', '1/10', '1/10'), ('rhoA', '9/10', '9/10'), C0)),
                                ('G_M_pctC', 'G_S_pctC', 'P_flip'), log, who=WHO, purpose='Part2 §6 rhoA=.9 pair')
    res['lB8_listing'] = D.values(disc, Box('lB8 k<=.3 h>=8', (('lambdaB', '8', '8'), ('kappa', '1/10', '3/10'), ('h', '8', '16'), C0)),
                                  ('G_M_pctC', 'G_S_pctC', 'Gamma_pctC', 'G_SM_pctC', 'P_flip'), log, who=WHO,
                                  purpose='Part2 table 2 reproduction')
    res['corner_lA8'] = D.table(disc, [(f'lambdaA=8,lambdaB={lb}', Box(f'lA8 lB{lb}', (('lambdaA', '8', '8'), ('lambdaB', lb, lb), C0)))
                                       for lb in ('6', '7', '8')],
                                dict(GM_gt_009=('G_M_pctC', '>', 0.09), Pflip_gt0=('P_flip', '>', 0), MV=MV),
                                log, who=WHO, purpose='Part2 table 4: corner lambdaA=8')
    res['sh_counts'] = D.table(disc, [('lambdaB=6', Box('lB6', (('lambdaB', '6', '6'), C0))),
                                      ('lambdaB=7', Box('lB7', (('lambdaB', '7', '7'), C0))),
                                      ('lambdaB=8,kappa>=1', Box('lB8k1', (('lambdaB', '8', '8'), ('kappa', '1', '3'), C0))),
                                      ('h=2', Box('h2', (('h', '2', '2'), C0)))],
                               dict(SH=SH, MV=MV), log, who=WHO, purpose='Part2 §8.3 SH counts reproduction')
    return res


def candidates(disc, log):
    res = []
    for rule in CANDIDATES:
        pred = dict(MV=MV, SH=SH, **(GAMMA_PRED if rule.role == 'Gamma' else {}))
        if rule.role.startswith('SH'):
            pred['SH_and_GSM_lt_epsE'] = [SH, ('abs(G_SM_pctC)', '<', 0.5)]
        n, counts, desc = D.summarize(disc, rule, pred, log, who=WHO, purpose=f'candidate {rule.role}',
                                      describe=('G_M_pctC', 'G_S_pctC', 'Gamma_pctC'))
        res.append(dict(rule=rule.as_json(), text=rule.text(), n=n, counts=counts, describe=desc,
                        active=rule.active(fixed=('c_sw', 'u')), exposure=sealed_and_exposed(rule)))
    gall = Box('ALL c_sw=0', (C0,))
    n, counts, desc = D.summarize(disc, gall, GAMMA_PRED, log, who=WHO, purpose='Gamma clamp diagnostic over all',
                                  describe=('Gamma_pctC',))
    return dict(candidates=res, gamma_all=dict(n=n, counts=counts, describe=desc))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--entry0', action='store_true')
    ap.add_argument('--part-a', action='store_true')
    ap.add_argument('--candidates', action='store_true')
    a = ap.parse_args(argv)
    if a.entry0: return entry0()
    require_committed()
    disc, log = D.load(), D.ForkingLog(LOG)
    meta = dict(n_distinct=len(disc), duplicates=disc.duplicates, blobs=disc.blobs, pilot_commit=D.PILOT_COMMIT,
                git_head=D.head(), label='DISCOVERY ONLY: saved pilot raw; not evidence, not CF')
    (OUT / 'discovery').mkdir(parents=True, exist_ok=True)
    if a.part_a:
        (OUT / 'discovery' / 'part_a.json').write_text(json.dumps(dict(meta=meta, **part_a(disc, log)), indent=1, ensure_ascii=False))
    if a.candidates:
        (OUT / 'discovery' / 'candidates.json').write_text(json.dumps(dict(meta=meta, **candidates(disc, log)), indent=1, ensure_ascii=False))
    print(json.dumps(dict(log_entries=len(log.entries())), ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())
