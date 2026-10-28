"""Doan Van Tai — staged A05-F prereg/theta/prediction content and order guards."""
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.A03_card.provenance import ROOT,CARD,metadata,_tracked_clean
from experiments.A04_discovery.provenance import verify as verify_A04,require_score_commit

BASE='experiments/A05_freeze/'
PREREG=BASE+'prereg.md'
CONFIG=BASE+'config.json'
CHOICES=BASE+'author_choices.json'
CARRY=BASE+'carry_K5.json'
SOURCE_LOCK=BASE+'source.lock.json'
PREDICTIONS=BASE+'predictions_heldout.json'
DISCRIMINATION=BASE+'discrimination.json'
FEATURES=BASE+'features_heldout.json'
FREEZE_LOCK=BASE+'freeze.lock.json'
CANONICAL='notes/lessons/A05_F_preregistration.md'
FITDIR='results/A05_F/20261028_01'
THETA=FITDIR+'/theta.json'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def ancestor(before,after,repo=ROOT,strict=False):
    if strict and before==after:
        raise PermissionError('stages require distinct commits')
    if subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',before,after],capture_output=True).returncode:
        raise PermissionError('A05-F commit order failed')


def sources(repo=ROOT):
    paths=[*Path(repo).glob(BASE+'*.py'),*[Path(repo)/p for p in (CONFIG,PREREG,CHOICES,CARRY)]]
    return {str(p.relative_to(repo)):sha(p) for p in sorted(paths)}


def validate_config(cfg):
    if (cfg['architecture']!='A' or cfg['rho_fixed']!=0 or cfg['coefficients_per_model']!=12 or
        cfg['candidates_per_model']!=2 or cfg['maximum_feature_tier']!=2 or cfg['heldout_D_allowed'] or
        cfg['heldout_outcomes_allowed_in_A05_F'] or cfg['primary_dt_s']!='1/240' or
        cfg['primary_metric']!=['G_S','G_M','Gamma'] or cfg['metric_weights']!=['1/3']*3 or
        cfg['margin']!='1/400' or cfg['C1_threshold']!='1/200'):
        raise PermissionError('configuration differs from this registered comparison')


def verify_prereg(repo=ROOT):
    inherited=verify_A04(repo)
    require_score_commit(Path(repo)/'results/A04/20261027_01',repo)
    dc,raw=_tracked_clean(CHOICES,repo)
    decision=json.loads(raw)
    if (decision['D25_interpretation']!='ii' or not decision['technical_details_delegated'] or
            not decision['freeze_C1'] or not decision['carry_K5_unchanged']):
        raise PermissionError('author selection does not authorize this architecture')
    pc,_=_tracked_clean(PREREG,repo)
    ancestor(dc,pc,repo,strict=True)
    _,raw=_tracked_clean(SOURCE_LOCK,repo)
    lock=json.loads(raw)
    actual=sources(repo)
    if lock['source_sha256']!=actual:
        raise PermissionError('registered A05-F code/config/prereg changed')
    for path in actual:_tracked_clean(path,repo)
    validate_config(read(Path(repo)/CONFIG))
    carry=read(Path(repo)/CARRY)
    text=(Path(repo)/CARD).read_text();meta=metadata(text)
    section=text[text.index('## 4. Hai mức K5'):text.index('## 5. Hệ quả')]
    if (carry['rule']!=meta['K5_rule'] or carry['P5']!=meta['predictions']['P5'] or
            carry['verbatim_card_section_4']!=section or carry['locked_rule_count']!=1):
        raise PermissionError('K5 carry differs from the original frozen card')
    return dict(author_decision_commit=dc,prereg_commit=pc,
                source_sha256=actual,prediction_card_sha256=inherited['prediction_card_sha256'],
                inherited_A04_receipt=inherited['receipt_commit'],heldout_D_allowed=False)


def verify_theta(repo=ROOT):
    r=verify_prereg(repo)
    tc,raw=_tracked_clean(THETA,repo)
    theta=json.loads(raw)
    if theta['prereg_commit']!=r['prereg_commit'] or theta['source_sha256']!=r['source_sha256']:
        raise PermissionError('theta was not fitted under the committed prereg')
    ancestor(r['prereg_commit'],tc,repo,strict=True)
    if theta['fit_ids']!=[f'M{i:02}' for i in range(1,39)]:
        raise PermissionError('theta uses a wrong training domain')
    return dict(**r,theta_commit=tc,theta_sha256=hashlib.sha256(raw).hexdigest())


def verify_prediction_checkpoint(repo=ROOT):
    r=verify_theta(repo)
    commits=[]
    for path in (PREDICTIONS,DISCRIMINATION,FEATURES):
        commit,_=_tracked_clean(path,repo);commits.append(commit)
    if len(set(commits))!=1:
        raise PermissionError('prediction/discrimination/feature outputs must share a checkpoint')
    ancestor(r['theta_commit'],commits[0],repo,strict=True)
    pred=read(Path(repo)/PREDICTIONS)
    if (pred['theta_sha256']!=r['theta_sha256'] or pred['prereg_commit']!=r['prereg_commit'] or
            pred['theta_commit']!=r['theta_commit'] or pred['source_sha256']!=r['source_sha256']):
        raise PermissionError('predictions differ from frozen theta/source context')
    return dict(**r,prediction_commit=commits[0],
                predictions_sha256=sha(Path(repo)/PREDICTIONS),
                discrimination_sha256=sha(Path(repo)/DISCRIMINATION),features_sha256=sha(Path(repo)/FEATURES))


def verify_frozen(repo=ROOT):
    r=verify_prediction_checkpoint(repo)
    fc,raw=_tracked_clean(FREEZE_LOCK,repo)
    cc,_=_tracked_clean(CANONICAL,repo)
    receipt=json.loads(raw)
    if receipt['status']!='FROZEN_A05_F' or receipt['checkpoint']!=r:
        raise PermissionError('A05-F freeze hash/order mismatch')
    if fc!=cc:
        raise PermissionError('canonical freeze and lock must share a commit')
    ancestor(r['prediction_commit'],fc,repo,strict=True)
    for path,h in receipt['artifact_sha256'].items():
        _tracked_clean(path,repo)
        if sha(Path(repo)/path)!=h:raise PermissionError('frozen artifact changed: '+path)
    return dict(**r,freeze_commit=fc,A05_F_performs_A05_T=False)
