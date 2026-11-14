"""Doan Van Tai — EV-D independent DES validation; fixed seeds, no scored study."""
from fractions import Fraction as F
import json

import numpy as np
import pytest

from experiments.ext_validity import packet as P
from experiments.explore_ctmc import ctmc as C


def case(**kwargs):
    return dict(dict(id='validation', cls='mmpp2', lamA=7., lamB=7.5, u=1.,
                     params=dict(kappa=.5), seed=90210, warmup=1000., n_inst=24000), **kwargs)


def identity_nowcast():
    return {p: dict(beta=[0., 1., 0.], gamma=[0., 1., 0.]) for p in ('A', 'B')}


def exact_backlog_only():
    """Different from ctmc's mode-aware M0: n-only fresh; plug-in y stale."""
    ev = C.evaluate(F(7),F(15,2),F(1),F(1,2),[F(3)],arrays=True,disagree=False)
    a = ev['_arrays']
    chs = [C.chain(F(8),F(1,2),a['NA']), C.chain(F(15,2),F(1,2),a['NB'])]
    inputs = []
    for j, ch in enumerate(chs):
        parts = P.fluid_parts(np.arange(ch.N+1), [7.,7.5][j], 1., 3., j)
        inputs.append((ch.pi, np.repeat(parts,2), a[['dA','dB'][j]][0],
                       ch.pi.reshape(-1,2).sum(1), parts, a[['dAo','dBo'][j]][0]))
    A,B = inputs
    fresh = C.pair_sum(*A[:3],*B[:3],0.)[1]
    stale = C.pair_sum(*A[3:],*B[3:],0.)[1]
    return stale-fresh


def test_physics_stationary_and_conditional():
    rng = np.random.default_rng(41027)
    bg = P.arrivals('mmpp2',7.,dict(kappa=.5),51000.,rng)
    run = bg,P.departures(bg,rng.exponential(.1,len(bg)))
    stats = P.batch_stats(P.backlog(run,np.arange(1000.,51000.,.1)),100)
    exact = C.chain(F(7),F(1,2),160)
    print('\nstationary mean, se, exact:',stats,exact.r)
    assert abs(stats['mean']-exact.r) <= 4*stats['se']
    n,h = 6000,2.
    for q,mode in [(0,0),(4,1),(12,0)]:
        rows = [P.arrivals('mmpp2',7.,dict(kappa=.5,initial_mode=mode),h,rng) for _ in range(n)]
        at = np.full((n,max(map(len,rows))),np.inf)
        for i,row in enumerate(rows):
            at[i,:len(row)] = row
        vals = P.lindley_cost(np.full(n,q),at,rng.exponential(.1,at.shape),rng.exponential(.1,(n,q)),h)
        stats = P.batch_stats(vals,40)
        target = exact.V([h])[0,2*q+mode]
        print('conditional q/mode, mean, se, exact:',q,mode,stats,target)
        assert abs(stats['mean']-target) <= 4*stats['se']


def test_pipeline_vs_exact():
    ev = P.simulate(case(),3.,dict(s_train=0.,T_int=1.,nowcast=identity_nowcast()))
    stats, target = ev['twins']['fluid'],exact_backlog_only()
    print('\npipeline GS, exact, CPU:',stats,target,ev['CPU'])
    assert abs(stats['G_S']-target) <= 4*stats['se']
    assert ev['spacing'] >= ev['h']+P.TAU
    assert ev['seed'] == 1090210


def test_lindley_brute_and_crn():
    at,sv,h,q = np.array([.2,.4,1.8]),np.array([.7,.3,.8]),2.,2
    initial = np.array([.5,.6])
    clock,total,n = 0.,0.,q
    deps = [.5,1.1]
    for t,s in zip(at,sv):
        deps.append(max(t,deps[-1])+s)
    events = sorted([(t,1) for t in at]+[(t,-1) for t in deps]+[(h,0)])
    for t,change in events:
        if t > h:
            break
        total += n*(t-clock); clock=t; n+=change
    got = P.lindley_cost(np.array([q]),at[None,:],sv[None,:],initial[None,:],h)[0]
    assert got == pytest.approx(total,abs=1e-14)
    c = case(u=0.)
    bg = [np.array([.1,.6,1.2]),np.array([.2,.8])]
    costs = P.futures(np.array([[3,1],[0,2]]),np.array([0.,.1]),bg,c,h,np.random.default_rng(7))
    np.testing.assert_array_equal(costs[:,0],costs[:,1])
    assert P.fluid_gap(np.array([[0,0],[100,100]]),case(),h).tolist() == [0.,0.]
    np.testing.assert_allclose(P.fluid_cost([0,1,4],9.,2.),[0.,.5,6.])
    np.testing.assert_allclose(P.fluid_cost([0,1],11.,2.),[2.,4.])
    qs = np.array([[0,0],[2,4],[6,1],[100,100]])
    direct = P.fluid_cost(qs[:,0],7.,h)-P.fluid_cost(qs[:,0],8.,h)
    direct += P.fluid_cost(qs[:,1],8.5,h)-P.fluid_cost(qs[:,1],7.5,h)
    np.testing.assert_allclose(P.fluid_gap(qs,case(),h),direct,atol=1e-14)


def test_pareto_means_and_aggregate():
    rng = np.random.default_rng(123456)
    params = dict(K=4,f=.3,T_c=1.5,b=2.,alpha=1.5,cap=8.)
    for mean in (params['f']*params['T_c'],(1-params['f'])*params['T_c']):
        draws = P.durations(mean,params,rng,300000)
        print('\nPareto requested/observed mean:',mean,draws.mean())
        assert abs(draws.mean()/mean-1) < .02
        assert draws.max() <= params['cap']*mean
        # Stationary residual E[R] = E[L²]/(2 E[L]); tests length bias.
        residual = P.durations(mean,params,rng,300000,True)
        assert residual.mean() == pytest.approx((draws**2).mean()/(2*draws.mean()),rel=.02)
    for cls in ('onoff_exp','onoff_pareto'):
        times = P.arrivals(cls,7.,params,20000.,rng)
        print('aggregate class/rate:',cls,len(times)/20000.)
        assert abs(len(times)/20000./7-1) < .02
        assert np.all(np.diff(times)>=0) and times.min()>=0 and times.max()<=20000.


def test_cli_write_once_and_timing_only(tmp_path):
    c = case(train_T=1000.,warmup=0.,n_inst=80,batches=4,h_mult=[1],spacing_mult=3,
             params=dict(kappa=.5,rate_window=2.))
    cases = tmp_path/'cases.json'
    cases.write_text(json.dumps([c]))
    tr,te = tmp_path/'train',tmp_path/'test'
    P.main(['train','--cases',str(cases),'--out',str(tr)])
    train = json.loads(next(tr.glob('*.json')).read_text())
    assert 'D' not in train and 'E_stay' not in train
    nowcast_shares = {f'F_old_{name}' for name in
                      ('fluid_nowcast','ratefluid_nowcast','ratefluid_nowcast_hybrid_train')}
    assert set(train['shares']['1']) == {'F_old','F_new','F_old_rate','F_new_rate'} | nowcast_shares
    assert set(train['nowcast']) == {'A','B'}
    assert all(set(v) == {'beta','gamma','r2_backlog','r2_rate'} for v in train['nowcast'].values())
    assert all(0 <= v <= 1 for v in train['shares']['1'].values())
    argv = ['test','--cases',str(cases),'--train',str(tr),'--out',str(te),'--workers','2']
    P.main(argv)
    result = json.loads(next(te.glob('*.json')).read_text())
    assert set(result['twins']) == {'fluid','hybrid_mm1','hybrid_train','ratefluid','ratefluid_hybrid_train',
                                  'fluid_nowcast','ratefluid_nowcast','ratefluid_nowcast_hybrid_train'}
    assert all(set(v) == {'G_S','se','pct_E_stay','se_pct'} for v in result['twins'].values())
    assert 0 <= result['F_old_rate'] <= 1 and 0 <= result['F_new_rate'] <= 1
    assert all(0 <= result[k] <= 1 for k in nowcast_shares)
    assert result['spacing'] == max(P.TAU,3*train['T_int'])
    with pytest.raises(FileExistsError):
        P.main(argv)
    P.main(argv[:-4]+['--out',str(tmp_path/'timing'),'--timing-only'])
    timing = json.loads(next((tmp_path/'timing').glob('*.json')).read_text())
    assert timing['timing_only'] and 'twins' not in timing and 'E_stay' not in timing
    assert result['h'] == train['T_int']
    c['params']['kappa'] = 1.
    cases.write_text(json.dumps([c]))
    with pytest.raises(ValueError,match='mismatch'):
        P.main(argv[:-4]+['--out',str(tmp_path/'mismatch')])


def test_validation():
    for kwargs in [dict(lamA=10.),dict(id='../bad'),dict(h_mult=[2]),dict(n_inst=2),
                   dict(params=dict(kappa=-1)),dict(cls='unknown'),dict(seed=1000000),
                   dict(params=dict(kappa=.5,initial_mode=0)),
                   *[dict(params=dict(kappa=.5,rate_window=w)) for w in (0.,-1.,np.nan,np.inf)]]:
        with pytest.raises(ValueError):
            P.validate(case(**kwargs))
    P.validate(case(h_mult=[30]))


def test_ratefluid_mean_limit_and_gap():
    q = np.array([0.,.1,2.,20.,100.])
    for lam, u, h, tr in [(7.,1.,3.,.25),(9.,.5,30.,2.),(6.,0.,1.,.1)]:
        got = P.ratefluid_cost(q,lam,np.full(q.shape,lam),u,h,tr)
        np.testing.assert_allclose(got,P.fluid_cost(q,lam+u,h),atol=1e-9,rtol=0)
    qs = np.array([[0.,0.],[2.,4.],[6.,1.],[100.,100.]])
    for rho in (np.tile([7.,7.5],(4,1)),np.array([[0.,0.],[24.,0.],[0.,30.],[24.,30.]])):
        direct = P.ratefluid_cost(qs[:,0],7.,rho[:,0],0.,3.,.25)-P.ratefluid_cost(qs[:,0],7.,rho[:,0],1.,3.,.25)
        direct += P.ratefluid_cost(qs[:,1],7.5,rho[:,1],1.,3.,.25)-P.ratefluid_cost(qs[:,1],7.5,rho[:,1],0.,3.,.25)
        np.testing.assert_allclose(P.ratefluid_gap(qs,rho,case(),3.),direct,atol=1e-12,rtol=0)
        assert P.ratefluid_gap(qs,rho,case(),3.)[0] == 0.  # empty, no initial overload
        assert P.ratefluid_gap(qs,rho,case(),3.)[-1] == 0.  # saturated tie -> Stay
    np.testing.assert_array_equal(P.ratefluid_gap(qs,rho,case(u=0.),3.),np.zeros(4))
    assert P.rate_settings(case()) == (.25,.25)
    for cls in ('onoff_exp','onoff_pareto'):
        assert P.rate_settings(case(cls=cls,params=dict(T_c=2.,f=.25))) == (.375,.375)


def test_ratefluid_quadrature():
    # Includes rise-then-empty, drain, increasing negative drift, no emptying,
    # and an initially empty queue that first builds backlog then empties.
    q, rho = np.array([1.,2.,2.,100.,0.,0.]),np.array([18.,8.,0.,18.,18.,0.])
    h, tr, lam, u = 5.,.5,7.,1.
    t = np.linspace(0,h,200001)
    net = (lam+u-P.MU)*t+(rho[:,None]-lam)*tr*(-np.expm1(-t/tr))
    reference = np.trapezoid(np.maximum(0,q[:,None]+net),t,axis=1)
    got = P.ratefluid_cost(q,lam,rho,u,h,tr)
    np.testing.assert_allclose(got,reference,rtol=1e-6,atol=1e-12)
    print('\nratefluid max quadrature error:',np.max(abs(got-reference)))


def test_window_rate_stationary_mmpp2():
    bg = P.arrivals('mmpp2',7.,dict(kappa=.5),50000.,np.random.default_rng(6519))
    ts = np.arange(.25,50000.,.5)
    stats = P.batch_stats(P.window_rate(bg,ts,.25),100)
    print('\nwindow rate mean/se/target:',stats,7.)
    assert abs(stats['mean']-7.) <= 3*stats['se']
    np.testing.assert_array_equal(P.window_rate(np.array([0.,.5,1.,2.]),np.array([1.,2.]),1.),[3.,2.])
    with pytest.raises(ValueError,match='incomplete'):
        P.window_rate(bg,np.array([.1]),.25)


@pytest.mark.parametrize('h', [0., .1, 3., 30.])
def test_nowcast_identity_bitwise(h):
    q = np.array([[0,0],[2,4],[6,1],[100,100]])
    rho = np.array([[0.,0.],[24.,0.],[0.,30.],[24.,30.]])
    fit, shift = identity_nowcast(), -.125
    qhat, rhat = P.nowcast_inputs(q, rho, fit)
    assert qhat.tobytes() == q.astype(float).tobytes()
    assert rhat.tobytes() == rho.tobytes()
    gaps = P.nowcast_gaps(q, rho, case(), h, fit, shift)
    expected = [P.fluid_gap(q,case(),h), P.ratefluid_gap(q,rho,case(),h)]
    expected.append(expected[1]+h*shift)
    for got, want in zip(gaps.values(), expected):
        assert got.tobytes() == want.tobytes()
        assert (got<0).tobytes() == (want<0).tobytes()


@pytest.mark.parametrize('cls', ['mmpp2','onoff_exp','onoff_pareto'])
def test_nowcast_train_ols_and_shares(cls):
    params = dict(kappa=.5) if cls == 'mmpp2' else dict(K=4,f=.3,T_c=1.5,b=2.,alpha=1.5,cap=8.)
    c = case(cls=cls,params=params,train_T=4000.,sample_dt=.2,h_mult=[1,3])
    training = P.train(c)
    # Reconstruct only the training Stay run, with exactly the train seed.
    _, w = P.rate_settings(c)
    warm = max(c['warmup'],w)
    ts = np.arange(warm+P.TAU,warm+c['train_T'],c['sample_dt'])
    bg, both = P.long_run_crn(c,warm+c['train_T'],np.random.default_rng(c['seed']))  # Claude: train now uses CRN
    runs = both[0]
    fresh = np.column_stack([P.backlog(r,ts) for r in runs])
    stale = np.column_stack([P.backlog(r,ts-P.TAU) for r in runs])
    rn = np.column_stack([P.window_rate(a,ts,w) for a in bg])
    ro = np.column_stack([P.window_rate(a,ts-P.TAU,w) for a in bg])
    for j, path in enumerate(('A','B')):
        fit = training['nowcast'][path]
        for label, target, first, second, r2key in (
            ('beta',fresh[:,j],stale[:,j],ro[:,j],'r2_backlog'),
            ('gamma',rn[:,j],ro[:,j],stale[:,j],'r2_rate')):
            design = np.column_stack([np.ones(len(ts)), first, second])
            coef = np.asarray(fit[label])
            # Normal equations independently check OLS and feature/target order.
            np.testing.assert_allclose(design.T@(target-design@coef),0,atol=1e-7,rtol=0)
            expected_r2 = 1-np.sum((target-design@coef)**2)/np.sum((target-target.mean())**2)
            assert abs(fit[r2key] - expected_r2) <= 1e-12   # Claude: exact float equality was too brittle
            assert 0 < fit[r2key] < 1
        if cls == 'mmpp2':
            assert 0 < fit['beta'][1] <= 1
    qhat, rhat = P.nowcast_inputs(stale,ro,training['nowcast'])
    for mult in c['h_mult']:
        h = mult*training['T_int']
        fluid, rate = P.fluid_gap(qhat,c,h), P.ratefluid_gap(qhat,rhat,c,h)
        for name, gap in (('fluid_nowcast',fluid),('ratefluid_nowcast',rate),
                          ('ratefluid_nowcast_hybrid_train',rate+h*training['s_train'])):
            assert training['shares'][str(mult)][f'F_old_{name}'] == float((gap<0).mean())
    print('\nnowcast TRAIN fixture:',json.dumps(dict(cls=cls,seed=c['seed'],train_T=c['train_T'],
          sample_dt=c['sample_dt'],nowcast=training['nowcast'],CPU=training['CPU'])))
    assert json.loads(json.dumps(training,allow_nan=False))['nowcast'] == training['nowcast']


def test_nowcast_clipping_and_degenerate_ols():
    stale, rho = np.array([[0.,3.],[5.,1.]]), np.array([[4.,0.],[0.,2.]])
    fit = {p: dict(beta=[-1.,.5,.25],gamma=[-3.,.5,.25]) for p in ('A','B')}
    qhat, rhat = P.nowcast_inputs(stale,rho,fit)
    np.testing.assert_array_equal(qhat,[[0.,.5],[1.5,0.]])
    np.testing.assert_array_equal(rhat,[[-1.,-2.25],[-1.75,-1.75]])  # rate stays unclipped
    const = np.zeros((10,2))
    fitted = P.fit_nowcast(const,const,const,const)
    assert all(v['r2_backlog'] is None and v['r2_rate'] is None for v in fitted.values())
    json.dumps(fitted,allow_nan=False)


@pytest.mark.parametrize('identity', [True, False])
def test_nowcast_scoring_fresh_maps_and_no_test_refit(monkeypatch, identity):
    c, h = case(n_inst=80,batches=4,warmup=10.), 3.
    fit = identity_nowcast() if identity else {
        'A': dict(beta=[2.,.6,-.1],gamma=[4.,.2,.05]),
        'B': dict(beta=[1.,.7,.1],gamma=[5.,.1,-.05])}
    training = dict(s_train=-.125,T_int=1.,nowcast=fit)
    before = json.dumps(training,sort_keys=True)
    captured = {}
    original = P.long_run

    def record_run(*args):
        captured['bg'], captured['runs'] = original(*args)
        return captured['bg'], captured['runs']

    def fake_costs(q, *args):
        # Deterministic fixture costs; no scientific experiment.
        return np.column_stack([np.full(len(q),20.),20.+q[:,1]-q[:,0]])

    def no_fit(*args):
        pytest.fail('test must use frozen training coefficients')

    monkeypatch.setattr(P,'long_run',record_run)
    monkeypatch.setattr(P,'futures',fake_costs)
    monkeypatch.setattr(P,'fit_nowcast',no_fit)
    ev = P.simulate(c,h,training)
    assert json.dumps(training,sort_keys=True) == before
    assert ev['seed'] == c['seed']+1000000
    ts = c['warmup']+P.TAU+np.arange(c['n_inst'])*ev['spacing']
    fresh = np.column_stack([P.backlog(r,ts) for r in captured['runs']])
    stale = np.column_stack([P.backlog(r,ts-P.TAU) for r in captured['runs']])
    _, w = P.rate_settings(c)
    rn = np.column_stack([P.window_rate(a,ts,w) for a in captured['bg']])
    ro = np.column_stack([P.window_rate(a,ts-P.TAU,w) for a in captured['bg']])
    qhat, rhat = P.nowcast_inputs(stale,ro,fit)
    fg, rg = P.fluid_gap(fresh,c,h), P.ratefluid_gap(fresh,rn,c,h)
    ng, nr = P.fluid_gap(qhat,c,h), P.ratefluid_gap(qhat,rhat,c,h)
    d = fresh[:,1]-fresh[:,0]
    for name, base, old, new in (
        ('fluid_nowcast','fluid',ng,fg), ('ratefluid_nowcast','ratefluid',nr,rg),
        ('ratefluid_nowcast_hybrid_train','ratefluid_hybrid_train',nr+h*training['s_train'],rg+h*training['s_train'])):
        z = ((old<0).astype(int)-(new<0))*d
        expected = P.batch_stats(z,c['batches'])
        got = ev['twins'][name]
        assert got['G_S'] == expected['mean'] and got['se'] == expected['se']
        assert got['pct_E_stay'] == 100*(expected['mean']/20.)
        assert got['se_pct'] == pytest.approx(100*expected['se']/20.,rel=1e-14,abs=1e-14)
        assert ev[f'F_old_{name}'] == float((old<0).mean())
        if identity:
            assert json.dumps(got,sort_keys=True) == json.dumps(ev['twins'][base],sort_keys=True)
    with pytest.raises(ValueError,match='regenerate training'):
        P.simulate(c,h,dict(s_train=0.,T_int=1.))


def test_crn_s_estimate_close_to_exact():
    """Claude (review): the CRN estimate of s for mmpp2 is close to the exact ctmc value."""
    from fractions import Fraction as Fr
    from experiments.explore_ctmc import ctmc as Cm
    case = dict(id='crn', cls='mmpp2', lamA=7.0, lamB=6.5, u=1.0, params=dict(kappa=0.5), seed=7, train_T=60000.,
                sample_dt=0.5, h_mult=[1])
    t = P.train(case)
    a, b, u, k = Fr(7), Fr(13, 2), Fr(1), Fr(1, 2)
    NA, NB = Cm.choose_N(a + u, k), Cm.choose_N(b + u, k)
    s = (Cm.chain(a, k, NA).r + Cm.chain(b + u, k, NB).r) - (Cm.chain(a + u, k, NA).r + Cm.chain(b, k, NB).r)
    assert abs(t['s_train'] - s) <= 0.1 * abs(s) + 0.05
