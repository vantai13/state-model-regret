"""Doan Van Tai — L4.1 raw recount; AI soạn theo ủy quyền, không author verification.

Read immutable git blobs, never import exploration/native engines. Thresholds are
the archived reading rules, not a new contract or a confirmation scoring rule.
Run: .venv/bin/python -m experiments.P4_01_recount.recount_map --out <new-directory>
"""
import argparse
import csv
from collections import Counter, defaultdict
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import statistics as st
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
TAG = 'explore-v13-regime-map'
COMMIT = '574a36fb4213a79d3d2aa305a489701cfc3059f2'
BATCHES = ('stage1', 'stage2', 'map1', 'map2', 'map3age', 'map4amp')
COORDS = ('lambdaA', 'lambdaB', 'kappa', 'eta', 'h', 'age', 'amp')
NUM = ('G_S_pctC', 'G_M_pctC', 'G_SM_pctC', 'Gamma_pctC', 'G_S_M1_pctC', 'G_M_S1_pctC')
LABELS = ('A', 'B', 'AB', 'J', 'C', 'D')
LONG = dict(STATE_DOM='A', MODEL_DOM='B', BOTH='AB', JOINT='J', STATE_HARM='C', NEITHER='D')
INV = 'results/lessons/l3r_7/lean_close/collision_inventory_v3.json'
TOL = 1e-12  # algebra/roundoff diagnostic in pp; NOT the native tolerance for L4.3


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True, capture_output=True).stdout


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def read_rows(blob, batch):
    rows = []
    for row in csv.DictReader(io.StringIO(blob)):
        row.setdefault('age', '1')
        row.setdefault('amp', '6')
        row.setdefault('c_sw', '0')
        exact = tuple(F(row[c]) for c in COORDS)
        parsed = {'id': row['id'], 'batch': batch, '_key': exact}
        for field, value in row.items():
            if field == 'id':
                continue
            number = float(value)
            if not math.isfinite(number):
                raise ValueError(f'non-finite {batch}/{row["id"]}/{field}')
            parsed[field] = number
        if parsed['c_sw'] != 0:
            continue
        if parsed['age'] <= 0 or parsed['amp'] <= 0:
            raise ValueError('age/amp must be positive')
        if parsed.get('Cbar', 1) <= 0:
            raise ValueError('nonpositive Cbar: percentages undefined')
        for field in NUM:
            if field not in parsed:
                raise ValueError(f'missing {field}')
        rows.append(parsed)
    return rows


def dedup(rows):
    seen, dropped = {}, []
    for row in rows:
        key = row['_key']
        if key not in seen:
            seen[key] = row
            continue
        first = seen[key]
        # Check all shared deterministic numeric outputs, not just six contrasts.
        fields = sorted((set(first) & set(row)) - {'id', 'batch', '_key', 'wall_s'})
        differences = [c for c in fields if first[c] != row[c]]
        if differences:
            raise ValueError(f'conflicting duplicate {first["id"]}/{row["id"]}: {differences}')
        dropped.append(dict(kept_id=first['id'], dropped_id=row['id'],
                            kept_batch=first['batch'], dropped_batch=row['batch'],
                            compared_fields=len(fields), all_equal=True))
    return list(seen.values()), dropped


def cls(row):
    gs, gm, gsm, gamma = (row[c] for c in NUM[:4])
    if gs <= -1:
        return 'C'
    if gs >= 1:
        return 'A' if gm < 1 else 'AB'
    if gm >= 1:
        return 'B'
    if gsm >= 1 and gamma >= max(gs, gm):
        return 'J'
    return 'D'


def counts(rows):
    c = Counter(cls(r) for r in rows)
    return {label: c[label] for label in LABELS}


def q_linear(values, q):
    values = sorted(values)
    if not values or not 0 <= q <= 1:
        raise ValueError('nonempty values and q in [0,1] required')
    p = (len(values) - 1) * q
    i = int(p)
    return values[i] if i + 1 == len(values) else values[i] + (p - i) * (values[i + 1] - values[i])


def scaled_key(row):
    a, b, k, e, h, age, amp = row['_key']
    return a, b, k / age, e, h / age, amp


def namespace_key(row):
    a, b, k, e, h, amp = scaled_key(row)
    ns = 'v1.3_fixed_plant' if amp == 6 else f'explore_amplitude_{amp}'
    return ns, '|'.join(map(str, (a, b, 2 * e, k, h, F(0))))


def in_mv_plus(row):
    a, b, k, e, h, amp = scaled_key(row)
    return (amp == 6 and b == 8 and 7 <= a <= F(15, 2) and 1 <= 2*e <= F(3, 2)
            and F(1, 10) <= k <= F(3, 10) and 12 <= h <= 16)


def summarize(raw, table):
    base_a = [r for r in table if r['age'] == 1 and r['amp'] == 6 and cls(r) == 'A']
    ab = [r for r in table if cls(r) == 'AB']
    harm = [r for r in table if cls(r) == 'C']
    joint = [r for r in table if cls(r) == 'J']
    by_delta = defaultdict(list)
    for r in table:
        a, b, k, e, h, amp = scaled_key(r)
        if amp == 6 and F(1, 20) <= k <= F(3, 20) and 4 <= h <= 8 and F(5, 8) <= e <= F(7, 8):
            by_delta[b - a].append(r)
    delta = [dict(delta=str(d), n=len(rs), **counts(rs)) for d, rs in sorted(by_delta.items())]
    age_groups = defaultdict(list)
    for r in table:
        if r['amp'] == 6:
            age_groups[tuple(r['_key'][i] for i in (0, 1, 2, 3, 4, 6))].append(r)
    monotonic = [sorted(rs, key=lambda r:r['age']) for rs in age_groups.values() if len(rs) > 1]
    mono_pass = sum(all(y['G_S_M1_pctC'] >= x['G_S_M1_pctC'] - TOL
                        for x, y in zip(rs, rs[1:])) for rs in monotonic)
    base = {r['_key'][:6]: r for r in table if r['amp'] == 6}
    amp_ratios = []
    for r in table:
        if r['amp'] == 4 and r['_key'][:6] in base:
            b = base[r['_key'][:6]]
            amp_ratios.append(dict(id=r['id'], base_id=b['id'], Cbar_ratio=r['Cbar']/b['Cbar'],
                                   GM_S1_absolute_ratio=(r['G_M_S1']/b['G_M_S1'] if b['G_M_S1'] else None)))
    identities = dict(
        tolerance_pp=TOL,
        S11_state_max_abs_pp=max(abs(r['Gamma_pctC'] - (r['G_S_M1_pctC'] - r['G_S_pctC'])) for r in table),
        S11_model_max_abs_pp=max(abs(r['Gamma_pctC'] - (r['G_M_S1_pctC'] - r['G_M_pctC'])) for r in table),
        minima_pp={c:min(r[c] for r in table) for c in ('G_M_pctC','G_SM_pctC','G_S_M1_pctC','G_M_S1_pctC')},
        lower_bound_violations=sum(r['Gamma_pctC'] < -min(r['G_S_pctC'],r['G_M_pctC'])-TOL for r in table),
        S12_harm_violations=sum(r['Gamma_pctC'] < abs(r['G_S_pctC'])-TOL for r in harm),
        harm_min_Gamma_pp=min(r['Gamma_pctC'] for r in harm))
    s = dict(raw_count=len(raw), table_count=len(table),
             batch_raw=dict(Counter(r['batch'] for r in raw)),
             batch_kept=dict(Counter(r['batch'] for r in table)), classes=counts(table),
             map1_raw_classes=counts([r for r in raw if r['batch']=='map1']),
             numerical_levels=sorted({(r['K'],r['ref']) for r in raw}),
             identities=identities,
             A_age1_amp6=dict(n=len(base_a), median_GS_pp=st.median(r['G_S_pctC'] for r in base_a),
                             q90_linear_GS_pp=q_linear([r['G_S_pctC'] for r in base_a], .9),
                             max_GS_pp=max(r['G_S_pctC'] for r in base_a),
                             median_GM_pp=st.median(r['G_M_pctC'] for r in base_a)),
             AB=dict(n=len(ab), gamma_negative=sum(r['Gamma_pctC'] < 0 for r in ab),
                     median_GS_pp=st.median(r['G_S_pctC'] for r in ab),
                     median_GS_M1_pp=st.median(r['G_S_M1_pctC'] for r in ab),
                     near_substitution={str(t):sum(abs(r['Gamma_pctC']+min(r['G_S_pctC'],r['G_M_pctC']))<t for r in ab)
                                        for t in (.1,.05)}),
             J=dict(n=len(joint), negative_GS=sum(r['G_S_pctC']<0 for r in joint),
                    nonnegative_GS_max_Gamma_pp=max(r['Gamma_pctC'] for r in joint if r['G_S_pctC']>=0)),
             MV_plus_classes=counts([r for r in table if in_mv_plus(r)]), delta_table=delta,
             age_monotonic=dict(groups=len(monotonic), nondecreasing=mono_pass,
                                complete_five_ages=sum(len(rs)==5 for rs in monotonic)),
             amp4_vs_amp6=dict(pairs=len(amp_ratios),median_Cbar_ratio=st.median(r['Cbar_ratio'] for r in amp_ratios),
                              positive_denominator_absolute_ratios=sum(r['GM_S1_absolute_ratio'] is not None for r in amp_ratios),
                              median_GM_S1_absolute_ratio=st.median(r['GM_S1_absolute_ratio'] for r in amp_ratios
                                                                    if r['GM_S1_absolute_ratio'] is not None)),
             X2065=[dict(id=r['id'], label=cls(r), **{c:r[c] for c in NUM}) for r in table if r['id']=='X2065'])
    return s


def csv_write(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build():
    if git('cat-file','-t',TAG).decode().strip() != 'tag' or git('rev-parse',TAG+'^{}').decode().strip() != COMMIT:
        raise ValueError('annotated map tag missing or moved')
    sources, raw = {}, []
    for batch in BATCHES:
        path = f'results/explore_v13/{batch}/regimes.csv'
        blob = git('show',f'{COMMIT}:{path}')
        sources[f'{COMMIT}:{path}'] = digest(blob)
        raw.extend(read_rows(blob.decode(),batch))
    table, dropped = dedup(raw)
    summary = summarize(raw,table)
    archived_path = 'results/explore_v13/regime_map/regime_map_table.csv'
    archived_blob = git('show',f'{COMMIT}:{archived_path}')
    sources[f'{COMMIT}:{archived_path}'] = digest(archived_blob)
    archived = {tuple(F(r[c]) for c in COORDS):r
                for r in csv.DictReader(io.StringIO(archived_blob.decode()))}
    mismatches = []
    for r in table:
        old = archived.get(r['_key'])
        if old is None or LONG.get(old['class']) != cls(r) or any(float(old[c]) != r[c] for c in NUM):
            mismatches.append(r['id'])
    inv_blob = (ROOT/INV).read_bytes()
    sources[INV] = digest(inv_blob)
    inv = json.loads(inv_blob)
    keys = {(r['namespace'],r['key']) for r in inv['records']}
    missing = [r['id'] for r in raw if namespace_key(r) not in keys]
    distinct = len({r['key'] for r in inv['records'] if r['namespace']=='v1.3_fixed_plant'})
    inventory = dict(path=INV, distinct_v13_keys=distinct, reported_distinct_v13_keys=inv['distinct_v13_keys'],
                     source_record_counts=inv['source_record_counts'], map_raw_missing_ids=missing,
                     session_probe_records=[r for r in inv['records'] if r['source']=='ai_session_probe_unsaved'],
                     K6_link='UNRESOLVED: input gives no coordinates or saved native probe output; do not equate the two sets of eight')
    numeric = summary['identities']
    checks = dict(tag_pinned=True,duplicates_exact=all(d['all_equal'] for d in dropped),
                  archived_table_matches=(not mismatches and len(archived)==len(table)),
                  S11_state=numeric['S11_state_max_abs_pp']<=TOL,
                  S11_model=numeric['S11_model_max_abs_pp']<=TOL,
                  S07_S08=all(v>=-TOL for v in numeric['minima_pp'].values()),
                  Gamma_lower_bound=numeric['lower_bound_violations']==0,
                  S12=numeric['S12_harm_violations']==0,
                  inventory_covers_all_raw=not missing,
                  inventory_distinct_count=distinct==inv['distinct_v13_keys'])
    summary.update(duplicates_dropped=len(dropped), checks=checks,
                   status='PASS' if all(checks.values()) else 'FAIL', inventory=inventory,
                   archived_table_mismatch_ids=mismatches)
    return raw,table,dropped,summary,sources


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out.exists():
        raise FileExistsError('output exists; stop before reading data')
    raw,table,dropped,summary,sources=build()
    args.out.mkdir(parents=True)
    (args.out/'recount.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    csv_write(args.out/'duplicates.csv',dropped,list(dropped[0]))
    csv_write(args.out/'delta_classes.csv',summary['delta_table'],['delta','n',*LABELS])
    fields=['id','batch',*COORDS,'class','Cbar',*NUM]
    csv_write(args.out/'recounted_regimes.csv',
              [{**{k:r[k] for k in fields if k!='class'},'class':cls(r)} for r in table],fields)
    csv_write(args.out/'discovery_parameters.csv',
              [dict(id=r['id'],batch=r['batch'],**dict(zip(COORDS,map(str,r['_key']))),c_sw='0') for r in raw],
              ['id','batch',*COORDS,'c_sw'])
    manifest=dict(responsible='Doan Van Tai',provenance='AI theo ủy quyền; tác giả chưa kiểm',
                  created_utc=datetime.now(timezone.utc).isoformat(), input_tag=TAG,input_commit=COMMIT,
                  head=git('rev-parse','HEAD').decode().strip(),source_sha256=sources,
                  script_sha256=digest(Path(__file__).read_bytes()),
                  configuration=dict(order=list(BATCHES),c_sw_filter=0,first_duplicate_kept=True,
                                     coordinate_key='exact rational decimal values, no rounding',
                                     epsilon_class_pctC=1,roundoff_diagnostic_tolerance_pp=TOL,
                                     quantile='linear: p=(n-1)*q',seed=None,engine_calls=0),
                  native_E11_E12='NOT_RUN',confirmation_outcomes=0,
                  outputs_sha256={p.name:digest(p.read_bytes()) for p in sorted(args.out.iterdir())})
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('status','raw_count','table_count','duplicates_dropped','classes',
                                           'map1_raw_classes','identities','A_age1_amp6','AB','MV_plus_classes','checks')},indent=2))
    return 0 if summary['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
