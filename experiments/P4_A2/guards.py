"""Doan Van Tai — A2 identity, replay and receipt checks; no engine import."""
from fractions import Fraction as F
import math

from experiments.P4_03_map_audit.common import require

METRICS = ('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1')
REPLAY_FIELDS = ('Cref','losses','cost_error','contrast_error','normalized_error',
                 'uncertain_action_mass','Stay','Stay_error','baseline',*METRICS,
                 'Sbar','Sbar_error','GM_identity_gap','P_flip',
                 'zero_action_certificate','identical_models_test')
BRANCHES = ('B1_CLAIM_LEVEL_ROBUSTNESS','B2_READY_SUBSET_NARROW')


def validate_decisions(d, n=8):
    hi,lo=d['ladder_resolves_if_at_least'],d['ladder_fails_if_at_most']
    require(type(hi) is int and type(lo) is int and 0<=lo<hi<=n,'invalid decision thresholds')
    require(d['branch_if_ladder_fails'] in BRANCHES,'invalid predeclared failure branch')
    require(type(d['cpu_cap_hours']) is int and d['cpu_cap_hours']>0,'invalid CPU budget')


def validate_row(row, case, level, fp, rhos, *, complete=True):
    require(row.get('id')==case['id'] and row.get('parameters')==case['parameters'], 'ROW_IDENTITY_MISMATCH')
    require((row.get('K'),row.get('ref'))==tuple(level), 'ROW_LEVEL_MISMATCH')
    require(row.get('dt')==str(F(1,120*level[1])), 'ROW_DT_MISMATCH')
    require(row.get('a2_prereg_sha256')==fp and row.get('CF_computed') is False,'ROW_RECEIPT_OR_CF_MISMATCH')
    cpu=row.get('call_cpu_seconds',0)
    require(math.isfinite(float(cpu)) and cpu>=0,'ROW_CPU_INVALID')
    if complete:
        require(row.get('status')=='COMPLETED' and not row.get('a1_bug_reasons'), 'ROW_NOT_VALID_COMPLETED')
        require([b['rho'] for b in row['baseline']]==list(rhos),'ROW_RHO_GRID_MISMATCH')
        require(F(row['Cref'])>0 and all(k in row for k in REPLAY_FIELDS),'ROW_NUMERICAL_SCHEMA_INVALID')


def _same_bits(a,b):
    # Compare the significant bits recovered from the saved numerical strings;
    # padding bytes and variable timing/cache metadata are not physical outputs.
    if isinstance(a,dict):
        return a.keys()==b.keys() and all(_same_bits(a[k],b[k]) for k in a)
    if isinstance(a,list):
        return len(a)==len(b) and all(_same_bits(x,y) for x,y in zip(a,b))
    if a is None or isinstance(a,bool):
        return a is b
    if isinstance(a,str) and '/' in a:
        return F(a)==F(b)  # rho is an exact design coordinate
    from experiments.P4_04_baseline.margin import significant_bits,LD
    return significant_bits(LD(a))==significant_bits(LD(b))


def reproduction(old,new):
    unequal=[k for k in REPLAY_FIELDS if old.get(k)!=new.get(k)]
    bits=[k for k in REPLAY_FIELDS if k not in unequal and not _same_bits(old[k],new[k])]
    return dict(saved_numerical_fields_equal=not unequal,
                reparsed_significant_bits_equal=not unequal and not bits,
                unequal_fields=unequal,bit_mismatch_fields=bits,
                scope='Saved numerical fields and their reparsed significant bits; no claim about original ABI padding/timing bytes')


def require_run_complete(summary, fp, target_ids):
    require(summary.get('status')=='PASS','RUN_NOT_PASS: no decision on stopped or partial run')
    require(summary.get('a2_prereg_sha256')==fp,'RUN_RECEIPT_MISMATCH')
    require(summary.get('completed_ids')==list(target_ids),'RUN_TARGET_SET_INCOMPLETE')
