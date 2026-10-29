"""Doan Van Tai — L3R.6 discovery reader and logged summaries (DISCOVERY only).

Exact design comes from the pilot specs.json at the frozen tag; saved outcomes come
from regimes.csv at the same tag and stay inside this module. Every outcome summary
goes through `summarize`, which appends one line to the forking-paths log first.
No engine call, no new regime, no CF/R09/R10 outcome.
"""
import csv
import hashlib
import io
import json
import subprocess
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

from experiments.R3R_05_contract.schema import from_pilot
from experiments.R3R_06_cards.regions import DesignView, in_region

PILOT_TAG = 'explore-v13-pilot'
PILOT_COMMIT = 'a7435e9a3cb0d1625479c942041ec6748444014a'
STAGES = ('stage1', 'stage2', 'stage3')
OUTCOMES = ('G_S_pctC', 'G_M_pctC', 'G_SM_pctC', 'Gamma_pctC', 'G_S_M1_pctC', 'G_M_S1_pctC',
            'P_flip', 'Cbar', 'Sbar')
RELATIONS = {'>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b, '>': lambda a, b: a > b,
             '<': lambda a, b: a < b}


def _git(*args, repo='.'):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True).stdout


def head(repo='.'):
    return _git('rev-parse', 'HEAD', repo=repo).decode().strip()


class Discovery:
    """Distinct pilot configurations; outcomes are private to logged summaries."""

    def __init__(self, records, blobs, duplicates):
        self._records = records          # list of (id, stage, DesignView, outcome dict)
        self.blobs = blobs               # path -> sha256 at the tag
        self.duplicates = duplicates     # [(kept_id, dropped_id, max_abs_outcome_diff)]

    def __len__(self): return len(self._records)
    def ids(self): return [r[0] for r in self._records]
    def designs(self): return [(r[0], r[1], r[2]) for r in self._records]


def load(stages=('stage1', 'stage2'), *, c_sw_zero=True, repo='.'):
    tagged = _git('rev-list', '-n1', PILOT_TAG, repo=repo).decode().strip()
    if tagged != PILOT_COMMIT:
        raise RuntimeError(f'{PILOT_TAG} moved: {tagged}')
    blobs, rows = {}, []
    for st in stages:
        if st not in STAGES: raise ValueError(st)
        sp, cp = f'results/explore_v13/{st}/specs.json', f'results/explore_v13/{st}/regimes.csv'
        sb, cb = _git('show', f'{PILOT_COMMIT}:{sp}', repo=repo), _git('show', f'{PILOT_COMMIT}:{cp}', repo=repo)
        blobs[sp], blobs[cp] = hashlib.sha256(sb).hexdigest(), hashlib.sha256(cb).hexdigest()
        specs = {s[0]: s for s in json.loads(sb)}
        for r in csv.DictReader(io.StringIO(cb.decode())):
            reg = from_pilot(specs[r['id']])
            d = DesignView(reg)
            for k in ('lambdaA', 'lambdaB', 'kappa', 'h'):      # CSV floats must agree with exact spec
                if abs(float(d[k]) - float(r[k])) > 1e-12: raise ValueError(f'{r["id"]}: {k} spec/CSV mismatch')
            if abs(float(d['u']) - 2*float(r['eta'])) > 1e-12: raise ValueError(f'{r["id"]}: u/eta mismatch')
            if c_sw_zero and d['c_sw'] != 0: continue
            rows.append((r['id'], st, d, {k: float(r[k]) for k in OUTCOMES}))
    if len({r[0] for r in rows}) != len(rows): raise ValueError('duplicate pilot IDs')
    kept, seen, dups = [], {}, []
    for r in rows:
        k = r[2].key()
        if k in seen:
            first = seen[k]
            dups.append((first[0], r[0], max(abs(first[3][c] - r[3][c]) for c in OUTCOMES)))
            continue
        seen[k] = r
        kept.append(r)
    return Discovery(kept, blobs, dups)


class ForkingLog:
    """Append-only JSONL log; sequence numbers continue from existing lines."""

    def __init__(self, path):
        self.path = Path(path)

    def entries(self):
        if not self.path.exists(): return []
        return [json.loads(x) for x in self.path.read_text().splitlines() if x.strip()]

    def append(self, entry):
        e = dict(seq=len(self.entries()), utc=datetime.now(timezone.utc).isoformat(), **entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a') as f:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + '\n')
        return e


def _value(outcome, expr):
    if expr.startswith('min(') and expr.endswith(')'):
        return min(outcome[c.strip()] for c in expr[4:-1].split(','))
    if expr.startswith('abs(') and expr.endswith(')'):
        return abs(outcome[expr[4:-1]])
    return outcome[expr]


def _holds(outcome, spec):
    """spec: (expr, relation, threshold) or a list of such triples (conjunction)."""
    if isinstance(spec, list): return all(_holds(outcome, s) for s in spec)
    expr, rel, thr = spec
    return RELATIONS[rel](_value(outcome, expr), float(thr))


def _spec_text(spec):
    return [_spec_text(s) for s in spec] if isinstance(spec, list) else list(map(str, spec))


def summarize(disc, rule, predicates, log, *, who, purpose, keep='', reason='', describe=(), repo='.'):
    """Count a rule's discovery configurations and named outcome predicates.

    predicates: {name: (expr, relation, threshold) or [triples...] for AND}; expr is an
    outcome column, 'min(a,b)' or 'abs(a)'. The rule sees only DesignView. The log line is written before return.
    """
    inside = [r for r in disc._records if in_region(rule, r[2])]
    counts = {name: sum(_holds(r[3], spec) for r in inside) for name, spec in predicates.items()}
    desc = {}
    for expr in describe:
        vals = sorted(_value(r[3], expr) for r in inside)
        desc[expr] = None if not vals else dict(min=vals[0], median=vals[len(vals)//2] if len(vals) % 2 else
                                                 (vals[len(vals)//2 - 1] + vals[len(vals)//2])/2, max=vals[-1])
    entry = dict(kind='rule', who=who, purpose=purpose, rule=getattr(rule, 'text', lambda: repr(rule))(),
                 rule_id=getattr(rule, 'rule_id', None), n=len(inside),
                 predicates={k: _spec_text(v) for k, v in predicates.items()}, counts=counts,
                 describe=desc, ids=[r[0] for r in inside], keep=keep, reason=reason,
                 basis=f'{len(disc)} distinct configs, stages {sorted({r[1] for r in disc._records})}',
                 pilot_commit=PILOT_COMMIT, git_head=head(repo))
    log.append(entry)
    return len(inside), counts, desc


def table(disc, cells, predicates, log, *, who, purpose, repo='.'):
    """Several design-only cells in one logged call (e.g. a coverage table)."""
    rows = []
    for label, rule in cells:
        inside = [r for r in disc._records if in_region(rule, r[2])]
        rows.append(dict(cell=label, rule=rule.text(), n=len(inside),
                         counts={n: sum(_holds(r[3], spec) for r in inside) for n, spec in predicates.items()}))
    log.append(dict(kind='table', who=who, purpose=purpose, cells=rows,
                    predicates={k: _spec_text(v) for k, v in predicates.items()},
                    basis=f'{len(disc)} distinct configs', pilot_commit=PILOT_COMMIT, git_head=head(repo)))
    return rows


def values(disc, rule, columns, log, *, who, purpose, repo='.'):
    """Per-configuration listing inside a rule (logged)."""
    inside = [r for r in disc._records if in_region(rule, r[2])]
    out = [dict(id=r[0], stage=r[1], **{k: str(r[2][k]) for k in ('lambdaA', 'lambdaB', 'u', 'kappa', 'h')},
                **{c: r[3][c] for c in columns}) for r in inside]
    log.append(dict(kind='listing', who=who, purpose=purpose, rule=rule.text(), n=len(out), columns=list(columns),
                    ids=[r['id'] for r in out], pilot_commit=PILOT_COMMIT, git_head=head(repo)))
    return out
