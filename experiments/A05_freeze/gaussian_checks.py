"""Doan Van Tai — synthetic Monte Carlo check of Gaussian formulas, not plant data."""
import json
from pathlib import Path
import numpy as np

from experiments.A05_freeze.ledger import gaussian, contrasts, CONTRASTS


def main():
    rows=[]
    for seed,pars in ((13601,(.5,1.,0.,2.,0.)),(13602,(-.2,.8,.4,.7,.35))):
        mu,sd,bias,tau,rho=pars
        n=2000000
        rng=np.random.default_rng(seed)
        z=rng.standard_normal((2,n))
        delta=mu+sd*z[0]
        hat=delta+bias+tau*(rho*z[0]+np.sqrt(1-rho*rho)*z[1])
        samples=np.stack((delta,hat,np.maximum(0,-delta),delta*(hat<0)))
        estimates=samples.mean(axis=1)
        se=samples.std(axis=1,ddof=1)/np.sqrt(n)
        expected=gaussian(*pars)
        error=abs(estimates-expected)
        rows.append(dict(seed=seed,samples=n,parameters=list(pars),
                         closed_form=expected.tolist(),MC=estimates.tolist(),MC_standard_error=se.tolist(),
                         absolute_error=error.tolist(),max_standardized_error=float(max(error/se)),
                         pass_=bool(np.all(error<=6*se+1e-12))))
    golden=[dict(tau=t,**dict(zip(CONTRASTS,contrasts(gaussian(.5,1,0,t,0)).tolist()))) for t in (0,.5,1,2)]
    out=Path(__file__).resolve().parents[2]/'results/lessons/l3_6/preflight/gaussian_MC.json'
    out.write_text(json.dumps(dict(responsible='Doan Van Tai',synthetic_only=True,grid_outcomes_computed=False,
                                  Monte_Carlo_not_used_for_A04_or_fit=True,checks=rows,golden=golden),indent=2)+'\n')
    for row in rows:print('synthetic Gaussian',row['seed'],row['samples'],'PASS',row['pass_'],
                          'max abs error',max(row['absolute_error']),'max MC-SE',row['max_standardized_error'])
    assert all(r['pass_'] for r in rows)


if __name__=='__main__':main()
