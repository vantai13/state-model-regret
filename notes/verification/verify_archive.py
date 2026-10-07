"""Reproduce archive checks and F7 calculations; no new research simulation.

Requires Python 3.10+ and scipy. With no --archive-repo, clones the public
historical repository into a temporary directory. Only --output-dir is written.
"""
import argparse
import csv
import hashlib
import io
import json
import statistics
import subprocess
import tempfile
from pathlib import Path

from scipy.stats import t

URL = 'https://github.com/vantai13/dt4n-decision-risk-project.git'
TAG = 'archive-switch-or-stay-2026-10-02'
AUX = TAG + '-wip-local-2026-10-07'
TARGET = 'e669f5c8053a81d6de192de9f9d0d6304ee67802'
AUX_TARGET = '2e7543b2794a85645d60c0a55afb5a670166a099'


def git(repo, *args, check=True):
    r = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if check and r.returncode:
        raise RuntimeError(r.stderr.decode())
    return r


def value(repo, *args):
    return git(repo, *args).stdout.decode().strip()


def ci(xs):
    n = len(xs)
    m = statistics.mean(xs)
    half = float(t.ppf(.975, n-1))*statistics.stdev(xs)/n**.5
    return {'n': n, 'mean': m, 'ci95_half': half, 'lower': m-half, 'upper': m+half}


def difference(a, b):
    assert len(a) == len(b)
    return [x-y for x, y in zip(a, b)]


def audit(repo, out):
    report = {'date': '2026-10-07', 'timezone': 'Asia/Saigon',
              'kind': 'archive audit and recalculation; no new simulation',
              'target': TARGET, 'branches': [], 'sources': [], 'f7': {}}
    for tag, expected in [(TAG, TARGET), (AUX, AUX_TARGET)]:
        assert value(repo, 'rev-parse', tag+'^{commit}') == expected
        remote = value(repo, 'ls-remote', '--tags', 'origin', 'refs/tags/'+tag+'^{}')
        assert remote.split()[0] == expected
    report['remote_primary_tag_verified'] = True
    report['remote_auxiliary_tag_verified'] = True
    for ref in value(repo, 'for-each-ref', '--format=%(refname:short)', 'refs/remotes/origin').splitlines():
        if ref == 'origin/HEAD':
            continue
        included = git(repo, 'merge-base', '--is-ancestor', ref, TAG, check=False).returncode == 0
        preserved = git(repo, 'merge-base', '--is-ancestor', ref, AUX, check=False).returncode == 0
        assert included or preserved, ref
        report['branches'].append({'ref': ref, 'in_primary': included, 'in_auxiliary': preserved})

    def blob(path, tag=TAG):
        data = git(repo, 'show', tag+':'+path).stdout
        report['sources'].append({'ref': tag+':'+path, 'bytes': len(data),
                                  'sha256': hashlib.sha256(data).hexdigest()})
        return data

    data = json.loads(blob('experiments/results/f07/f07_outcome.json'))
    assert data['valid'] and all(all(g.values()) for g in data['gates'].values())
    for world in ('AA', 'BB', 'AB'):
        p = data[world]['per']
        assert len(p['headroom']) == 90
        center = difference(p['gain_SCdir'], p['gain_ref'])
        pure = difference(p['gain_K2'], p['gain_SCdir'])
        safety = difference(p['gain_K2inf'], p['gain_K2'])
        info = difference(p['headroom'], p['gain_K2inf'])
        gap = difference(p['gain_K2'], p['gain_ref'])
        residual = [h-r-c-u-s-i for h,r,c,u,s,i in zip(p['headroom'],p['gain_ref'],center,pure,safety,info)]
        assert max(map(abs,residual)) < 1e-10
        h = statistics.mean(p['headroom'])
        row = {key: ci(xs) for key,xs in [('headroom',p['headroom']),('static',p['gain_ref']),
               ('center',center),('pure',pure),('safety',safety),('information',info),('gap',gap)]}
        row['information_share_percent'] = 100*statistics.mean(info)/h
        row['pure_share_percent'] = 100*statistics.mean(pure)/h
        row['absolute_contrast'] = ci([x-8.1 for x in gap])
        row['relative_contrast'] = ci([x-.1*y for x,y in zip(gap,p['headroom'])])
        row['decomposition_residual_max'] = max(map(abs,residual))
        absolute, relative = row['absolute_contrast'], row['relative_contrast']
        row['practical_verdict'] = ('not meaningful' if absolute['upper'] < 0 or relative['upper'] < 0
                                  else 'meaningful' if absolute['lower'] > 0 and relative['lower'] > 0
                                  else 'undetermined')
        report['f7'][world] = row
        print(f"{world}: n=90; info={row['information_share_percent']:.4f}%; "
              f"pure={row['pure']['mean']:.6f} +/- {row['pure']['ci95_half']:.6f} ms "
              f"({row['pure_share_percent']:.4f}%); gap={row['gap']['mean']:.6f} "
              f"+/- {row['gap']['ci95_half']:.6f} ms")
    report['f7_validity'] = True
    report['f7_tests'] = data['tests']
    rows = list(csv.DictReader(io.StringIO(blob('results/gocheck/reproduction_contrasts.csv').decode())))
    selected = next(r for r in rows if r['contrast']=='SC_FIX_minus_SC_SYM'
                    and float(r['alpha'])==.002 and float(r['cooldown_s'])==0)
    report['gocheck_posthoc'] = selected
    assert abs(float(selected['mean_ms'])-2.985597896617483) < 1e-12
    for name in ('n02_H0.5_rho0.80_run.json', 'n02_H0.5_rho0.70_run.json'):
        run = json.loads(blob('experiments/results/'+name, AUX))
        assert run['seeds']==list(range(9101,9111))
        assert run['cell']['name']=='POS_probeB' and run['cell']['H']==.5
    report['n02_seeds_verified'] = list(range(9101,9111))
    report['n02_scope'] = 'PSA, POS_probeB, G_all, H=0.5; no action-induced load feedback'
    report['counterexamples'] = []
    for error in (3, 1.5):
        gaps = [-2+2*error,-2+error,-2+error,-2]
        costs = [18 if gap<0 else 20 for gap in gaps]
        gamma = costs[1]+costs[2]-costs[0]-costs[3]
        report['counterexamples'].append({'error':error,'gaps':gaps,'costs':costs,'gamma':gamma})
    assert [c['gamma'] for c in report['counterexamples']]==[2,-2]
    report['limitations'] = ['Literature primary papers not independently re-read.',
                            'Original full review is represented by a digest and public reading note.',
                            'Local bundles and raw data are not downloaded or independently recovered by this script.']
    print('Remote branches covered:',len(report['branches']))
    print('GO-check post-hoc SC FIX-SYM:',selected['mean_ms'],'ms')
    print('N2 seeds: 9101-9110; threshold counterexamples: +2 and -2')
    out.mkdir(parents=True,exist_ok=True)
    (out/'verification_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-repo', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.archive_repo:
        audit(args.archive_repo,args.output_dir)
    else:
        with tempfile.TemporaryDirectory(prefix='l01-archive-') as tmp:
            repo=Path(tmp)/'source'
            subprocess.run(['git','clone',URL,str(repo)],check=True,capture_output=True)
            audit(repo,args.output_dir)


if __name__=='__main__':
    main()
