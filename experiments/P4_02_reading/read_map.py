"""Doan Van Tai — L4.2 descriptions of exposed pilot CSVs; no engine calls.

These summaries do not select a card, a tolerance, a baseline, or a CF sample.
The optional short-horizon A-by-delta prediction exercise is deliberately absent.
"""
import csv
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import statistics as st

from experiments.P4_01_recount import recount_map as R

TABLE = Path('results/P4_01_recount/20261030_01/recounted_regimes.csv')
MANIFEST = TABLE.with_name('manifest.json')


def load_table():
    blob=(R.ROOT/TABLE).read_bytes()
    manifest=json.loads((R.ROOT/MANIFEST).read_text())
    if hashlib.sha256(blob).hexdigest()!=manifest['outputs_sha256'][TABLE.name]:
        raise ValueError('L4.1 CSV hash mismatch; stop before analysis')
    rows=[]
    for raw in csv.DictReader(blob.decode().splitlines()):
        row={k:raw[k] for k in ('id','batch','class')}
        row['_key']=tuple(F(raw[c]) for c in R.COORDS)
        for c in (*R.COORDS,*R.NUM,'Cbar'):
            row[c]=float(raw[c])
            if not math.isfinite(row[c]):
                raise ValueError(f'nonfinite {row["id"]}/{c}')
        if R.cls(row)!=row['class']:
            raise ValueError(f'class disagrees with L4.1: {row["id"]}')
        rows.append(row)
    return rows


def same_scaled_age_pairs(rows):
    base={R.scaled_key(r):r for r in rows if r['_key'][5]==1}
    pairs=[]
    for row in rows:
        if row['_key'][5]==1 or R.scaled_key(row) not in base:
            continue
        other=base[R.scaled_key(row)]
        field=max(R.NUM,key=lambda c:abs(row[c]-other[c]))
        pairs.append(dict(id=row['id'],age=row['age'],base_id=other['id'],
                          label=row['class'],base_label=other['class'],same_class=row['class']==other['class'],
                          max_contrast_abs_difference_pp=abs(row[field]-other[field]),max_field=field,
                          base_value_pctC=other[field],age_value_pctC=row[field]))
    return pairs


def boundary_rows(rows, radius=.15):
    # Union over rows, not sum of distances/events. Radius is supplied descriptive
    # post-hoc threshold; it does not become a native audit tolerance.
    out=[]
    for row in rows:
        field,bound=min(((c,b) for c in R.NUM[:2] for b in (-1,1)),key=lambda cb:abs(row[cb[0]]-cb[1]))
        distance=abs(row[field]-bound)
        if distance<=radius:
            out.append(dict(id=row['id'],label=row['class'],nearest_contrast=field,
                            boundary_pctC=bound,distance_pp=distance))
    return out


def delta_slice(rows):
    kept=[]
    for row in rows:
        a,b,k,e,h,amp=R.scaled_key(row)
        if amp==6 and F(1,20)<=k<=F(3,20) and 4<=h<=8 and F(5,8)<=e<=F(7,8):
            kept.append(row)
    return kept


def cross_table(rows):
    by=defaultdict(list)
    for row in rows:
        by[row['_key'][:2]].append(row)
    out=[]
    for (a,b),rs in sorted(by.items()):
        count=R.counts(rs)
        largest=max(count.values())
        out.append(dict(lambdaA=str(a),lambdaB=str(b),delta=str(b-a),delta_over_mu=str((b-a)/10),
                        headroom_ratio=str((10-b)/(10-a)),n=len(rs),**count,
                        plurality_labels='|'.join(c for c in R.LABELS if count[c]==largest),
                        plurality_count=largest,has_strict_majority=2*largest>len(rs)))
    return out


def summarize(rows):
    ages=same_scaled_age_pairs(rows)
    boundary=boundary_rows(rows)
    groups={k:[r for r in rows if r['class']==k] for k in R.LABELS}
    A,B,C,AB=groups['A'],groups['B'],groups['C'],groups['AB']
    mv=[r for r in rows if R.in_mv_plus(r)]
    selected=delta_slice(rows)
    by=defaultdict(list)
    for row in selected:
        a,b,*_=R.scaled_key(row)
        by[b-a].append(row)
    delta=[dict(delta=str(d),delta_over_mu=str(d/10),n=len(rs),**R.counts(rs)) for d,rs in sorted(by.items())]
    mechanism=dict(
        C_n=len(C),C_min_GM_S1_pctC=min(r['G_M_S1_pctC'] for r in C),
        C_oracle_bound_violations=sum(r['G_M_S1_pctC'] < abs(r['G_S_pctC'])+r['G_M_pctC']-R.TOL for r in C),
        A_n=len(A),A_min_GS_minus_GM_pctC=min(r['G_S_pctC']-r['G_M_pctC'] for r in A),
        A_information_bound_violations=sum(r['G_S_M1_pctC']<r['G_S_pctC']-r['G_M_pctC']-R.TOL for r in A),
        C_GS_M1_lt_point1=sum(r['G_S_M1_pctC']<.1 for r in C),
        A_GM_S1_lt_point5=sum(r['G_M_S1_pctC']<.5 for r in A),
        AB_n=len(AB),AB_median_GS_M1_pctC=st.median(r['G_S_M1_pctC'] for r in AB),
        AB_GS_M1_lt_point5=sum(r['G_S_M1_pctC']<.5 for r in AB),
        AB_GS_M1_ge_1=sum(r['G_S_M1_pctC']>=1 for r in AB))
    a_base=[r for r in A if r['_key'][5:]==(F(1),F(6))]
    summary=dict(
        status='DESCRIPTIVE_DISCOVERY',map_rows=len(rows),classes=R.counts(rows),
        age_pairs=dict(n=len(ages),same_class=sum(p['same_class'] for p in ages),
                       max_difference_pp=max(p['max_contrast_abs_difference_pp'] for p in ages),
                       worst_pair=max(ages,key=lambda p:p['max_contrast_abs_difference_pp'])),
        near_boundary=dict(radius_pp=.15,n=len(boundary),A_age1_amp6_n=len(a_base),
                           A_age1_amp6_GS_lt_1point15=sum(r['G_S_pctC']<1.15 for r in a_base)),
        MV_plus=dict(n=len(mv),classes=R.counts(mv),GM_ge_1=sum(r['G_M_pctC']>=1 for r in mv),
                     min_GM_pctC=min(r['G_M_pctC'] for r in mv),min_GS_pctC=min(r['G_S_pctC'] for r in mv)),
        mechanism=mechanism,delta_slice=dict(n=len(selected),by_delta=delta,
                  left_n=sum(len(rs) for d,rs in by.items() if d<0),
                  left_C=sum(r['class']=='C' for d,rs in by.items() if d<0 for r in rs)),
        A_all_scope_GS_range_pctC=[min(r['G_S_pctC'] for r in A),max(r['G_S_pctC'] for r in A)],
        A_age1_amp6_GS_range_pctC=[min(r['G_S_pctC'] for r in a_base),max(r['G_S_pctC'] for r in a_base)],
        optional_A_by_delta='NOT_RUN; no author prediction supplied',
        native_map_audit='NOT_RUN; E11/E12 pending L4.3',new_coordinates=0,confirmation_outcomes=0)
    # These are checks against numbers printed in the supplied lessons; no
    # experiment threshold/region is tuned to make these agree.
    checks=dict(age_pairs_18_same_class=summary['age_pairs']['n']==summary['age_pairs']['same_class']==18,
                age_pair_max_rounds_to_point201=round(summary['age_pairs']['max_difference_pp'],3)==.201,
                near_boundary_148=summary['near_boundary']['n']==148,
                fragile_A_28_of_211=(summary['near_boundary']['A_age1_amp6_n']==211 and summary['near_boundary']['A_age1_amp6_GS_lt_1point15']==28),
                MV_18_meet_GM=summary['MV_plus']['n']==summary['MV_plus']['GM_ge_1']==18,
                C_information_small_255_of_334=(len(C)==334 and mechanism['C_GS_M1_lt_point1']==255),
                A_model_small_286_of_301=(len(A)==301 and mechanism['A_GM_S1_lt_point5']==286),
                AB_heterogeneous_67_each=(len(AB)==161 and mechanism['AB_GS_M1_lt_point5']==mechanism['AB_GS_M1_ge_1']==67),
                delta_slice_238=len(selected)==238,
                oracle_inequalities=(mechanism['C_oracle_bound_violations']==mechanism['A_information_bound_violations']==0))
    summary['lesson_numeric_checks']=checks
    summary['verification_status']='PASS' if all(checks.values()) else 'MISMATCH_WITH_SUPPLIED_LESSON'
    return summary,ages,boundary,cross_table(selected)
