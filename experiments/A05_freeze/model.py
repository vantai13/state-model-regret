"""Doan Van Tai — identical 12-coefficient Gaussian regressors for H0/H1."""
import numpy as np
from scipy.optimize import least_squares

from experiments.A05_freeze.ledger import gaussian


def standardize(X, fitted=None):
    X=np.asarray(X,dtype=float)
    if fitted is None:
        mean=X[:,:,1:].mean(axis=0)
        scale=X[:,:,1:].std(axis=0)
        scale=np.where(scale>1e-12,scale,1.)
        fitted=dict(mean=mean.tolist(),scale=scale.tolist())
    result=X.copy()
    result[:,:,1:]=(X[:,:,1:]-np.asarray(fitted['mean']))/np.asarray(fitted['scale'])
    return result,fitted


def forward(X,beta,cfg):
    beta=np.asarray(beta).reshape(4,3)
    z=np.einsum('nhp,hp->nh',X,beta)
    logs=np.clip(z[:,[1,3]],*cfg['log_scale_prediction_clip'])
    return gaussian(z[:,0],np.exp(logs[:,0]),z[:,2],np.exp(logs[:,1]),cfg['rho_fixed'])


def fit_model(X,y,cfg):
    X,scaling=standardize(X)
    y=np.asarray(y,dtype=float)
    if X.shape!=(len(y),4,3) or y.shape[1]!=4 or cfg['coefficients_per_model']!=12:
        raise ValueError('matched twelve-coefficient model required')
    low=np.full((4,3),-1.);high=np.full((4,3),1.)
    low[[1,3]]=-6.;high[[1,3]]=6.
    low[[1,3],0]=-12.;high[[1,3],0]=1.
    initial=np.zeros((4,3))
    initial[0]=np.linalg.lstsq(X[:,0,:],y[:,0],rcond=None)[0]
    initial[2]=np.linalg.lstsq(X[:,2,:],y[:,1]-y[:,0],rcond=None)[0]
    runs=[]
    def residual(beta):
        prediction=forward(X,beta,cfg)
        penalty=np.sqrt(cfg['ridge'])*beta.reshape(4,3)[:,1:].ravel()
        return np.r_[(prediction-y).ravel()/np.sqrt(y.size),penalty]
    for sigma,tau in cfg['starts_per_fit']:
        b=initial.copy();b[1,0]=np.log(sigma);b[3,0]=np.log(tau)
        b=np.clip(b,low+1e-8,high-1e-8)
        result=least_squares(residual,b.ravel(),bounds=(low.ravel(),high.ravel()),
             method='trf',jac='2-point',max_nfev=cfg['max_nfev'],
             ftol=cfg['optimizer_tolerance'],xtol=cfg['optimizer_tolerance'],gtol=cfg['optimizer_tolerance'])
        runs.append(dict(success=bool(result.success),objective=float(np.dot(result.fun,result.fun)),
                         nfev=int(result.nfev),message=result.message,beta=result.x.reshape(4,3).tolist()))
    usable=[(i,r) for i,r in enumerate(runs) if r['success']]
    if not usable:
        raise ArithmeticError('all registered optimizer starts failed; no fit/prediction freeze')
    chosen=min(usable,key=lambda v:(v[1]['objective'],v[0]))[0]
    selected=runs[chosen]
    pred=forward(X,selected['beta'],cfg)
    return dict(beta=selected['beta'],scaling=scaling,k=12,rho=cfg['rho_fixed'],
                chosen_start=chosen,starts=runs,training_summary_MSE=float(np.mean((pred-y)**2)),
                training_summary_MAE=float(np.mean(abs(pred-y))))


def predict_model(X,theta,cfg):
    X,_=standardize(X,theta['scaling'])
    return forward(X,theta['beta'],cfg)
