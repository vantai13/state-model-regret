"""Doan Van Tai — card set v2 (DL-095): checks, one-time lock, fail-closed verify. AI (Claude) theo ủy quyền.

Card v2 differs from card v1 only in measure_rules.rounding (lambdaA/lambdaB/u = 1/100). The nine L3R.6 checks
are run with the unchanged check_cards code pointed at the v2 file. The lock mirrors the v1 receipt: the freeze
commit must be an ancestor of HEAD and every frozen file must equal its blob there and the recorded SHA-256.

  python -m experiments.R3R_14_lean_close.cards_v2 check
  python -m experiments.R3R_14_lean_close.cards_v2 lock <card_commit>
  python -m experiments.R3R_14_lean_close.cards_v2 verify
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

CARD = Path('notes/phases/PHASE_3R_hypothesis_cards_v2.md')
CHECKS = Path('results/lessons/l3r_7/lean_close/card_v2_checks.json')
LOCK = Path('notes/phases/PHASE_3R_hypothesis_cards_v2.lock.json')
FROZEN = (str(CARD), 'notes/phases/PHASE_3R_forking_paths.md', 'notes/01_claim_boundary_v1_3.md',
          'results/lessons/l3r_6/forking_paths.jsonl', str(CHECKS), 'results/lessons/l3r_6/author_choices.json',
          'results/lessons/l3r_7/lean_close/author_choices.json', 'results/lessons/l3r_7/lean_close/representation_selection.json',
          'experiments/R3R_06_cards/verdict.py', 'experiments/R3R_06_cards/stats.py',
          'experiments/R3R_06_cards/regions.py', 'experiments/R3R_06_cards/check_cards.py')
CONTRACT = ('contract-v1.3', '3d2359b32d7bd24f9e9072d5b5b8131bd33fffa0')


def _git(*a, check=True):
    return subprocess.run(['git', *a], capture_output=True, check=check)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(path=CARD):
    m = re.search(r'<!-- L3R6_CARDS\n(.*?)\n-->', Path(path).read_text(), re.S)
    return json.loads(m.group(1))


def check():
    """Unchanged L3R.6 check code, pointed at the v2 card and a v2 output path."""
    from experiments.R3R_06_cards import check_cards
    check_cards.CARD, check_cards.OUT = CARD, CHECKS
    check_cards.load_card.__defaults__ = (CARD,)
    code = check_cards.main()
    v1, v2 = load('notes/phases/PHASE_3R_hypothesis_cards.md'), load(CARD)
    same = {k: v1[k] == v2[k] for k in v1 if k not in ('version', 'measure_rules')}
    r1, r2 = dict(v1['measure_rules']), dict(v2['measure_rules'])
    rounding_diff = {k: (r1['rounding'][k], r2['rounding'][k]) for k in r1['rounding'] if r1['rounding'][k] != r2['rounding'][k]}
    r1.pop('rounding'), r2.pop('rounding')
    result = json.loads(CHECKS.read_text())
    result['v2_vs_v1'] = dict(identical_keys=same, all_other_keys_identical=all(same.values()) and r1 == r2,
                              rounding_changes=rounding_diff,
                              added_keys=sorted(set(v2) - set(v1)))
    result['all_ok'] = result['all_ok'] and result['v2_vs_v1']['all_other_keys_identical'] \
        and set(rounding_diff) == {'lambdaA', 'lambdaB', 'u'}
    CHECKS.write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str))
    print(json.dumps(dict(all_ok=result['all_ok'], v2_vs_v1=result['v2_vs_v1'], nine={k: c['ok'] for k, c in result['checks'].items()}),
                     ensure_ascii=False, indent=1))
    return code


def lock(card_commit):
    if LOCK.exists():
        raise SystemExit('v2 lock exists; a further card change needs v3 + DL')
    files = {p: sha(_git('show', f'{card_commit}:{p}').stdout) for p in FROZEN}
    for p, h in files.items():
        if sha(Path(p).read_bytes()) != h:
            raise SystemExit(f'working copy differs from freeze commit: {p}')
    checks = json.loads(CHECKS.read_text())
    if not checks['all_ok'] or checks['card_sha256'] != files[str(CARD)]:
        raise SystemExit('v2 card checks missing/failed or run on another card text')
    rec = dict(schema_version=1, card_set_id='L3R6', version=2, owner='Doan Van Tai',
               created_utc=datetime.now(timezone.utc).isoformat(),
               card_commit=_git('rev-parse', card_commit).stdout.decode().strip(),
               contract_tag=CONTRACT[0], contract_commit=CONTRACT[1], sha256=files, checks_all_ok=True,
               primaries=['Hyp-MV', 'Hyp-SH'], secondary=None, supersedes_version=1,
               provenance='AI (Claude) drafted v2 under DL-095; only the rate rounding step differs from v1 (author-approved content, DL-073)',
               scope='before any CF frame/sample/outcome; not evidence; G1 unchanged')
    LOCK.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + '\n')
    return rec


def verify():
    errors = []
    try:
        rec = json.loads(LOCK.read_text())
        if (rec.get('schema_version'), rec.get('card_set_id'), rec.get('version')) != (1, 'L3R6', 2):
            raise ValueError('unsupported card receipt identity/schema')
        if (rec.get('contract_tag'), rec.get('contract_commit')) != CONTRACT:
            raise ValueError('contract identity mismatch')
        if rec.get('checks_all_ok') is not True or set(rec.get('sha256', {})) != set(FROZEN):
            raise ValueError('receipt must cover the exact frozen v2 path set')
    except (OSError, ValueError, TypeError) as exc:
        return dict(status='FAIL', errors=[str(exc)])
    if _git('merge-base', '--is-ancestor', rec['card_commit'], 'HEAD', check=False).returncode:
        errors.append('card commit is not an ancestor of HEAD')
    if _git('rev-list', '-n1', CONTRACT[0], check=False).stdout.decode().strip() != CONTRACT[1]:
        errors.append('contract tag moved or missing')
    for p, h in rec['sha256'].items():
        blob = _git('show', f'{rec["card_commit"]}:{p}', check=False)
        if blob.returncode or sha(blob.stdout) != h:
            errors.append(f'freeze blob mismatch: {p}')
        elif not Path(p).exists() or sha(Path(p).read_bytes()) != h:
            errors.append(f'working file changed: {p}')
    return dict(status='PASS' if not errors else 'FAIL', errors=errors, card_commit=rec['card_commit'], files=len(rec['sha256']))


def verified_card():
    result = verify()
    if result['status'] != 'PASS':
        raise ValueError('card v2 receipt FAIL: ' + '; '.join(result['errors']))
    return load(CARD)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'check':
        sys.exit(check())
    elif cmd == 'lock':
        print(json.dumps(lock(sys.argv[2]), indent=1, ensure_ascii=False))
    elif cmd == 'verify':
        print(json.dumps(verify(), indent=1))
