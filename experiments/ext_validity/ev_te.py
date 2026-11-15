"""Doan Van Tai — EV-TE Arm S, training and locked truth CLI.

Rates: Mb/s; time: fast-mode units; queues: Mb; costs: Mb*time.
No work on import. The small embedded C++ kernel is compiled locally without
network access. Its mean twin sums the specified discrete fluid steps in closed
form between drift sign changes; it does not replace them by a continuous twin.
"""
from concurrent.futures import ProcessPoolExecutor
import argparse
import csv
import ctypes as ct
from dataclasses import dataclass
import hashlib
import heapq
import json
import math
from multiprocessing import get_context
import os
from pathlib import Path
import re
import resource
import subprocess
import tempfile
import time

import numpy as np

from experiments.ext_validity.packet import batch_stats, tint

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_te'
TAUS = (.1, .3, 1., 3.)
HS = (1, 2, 4, 7, 15, 30)
PIPES = ('M0_new', 'M0_old', 'P_old', 'CE_old', 'M1_new', 'M1_old')
TRAIN_SEED, TEST_SEED, PILOT_SEED = 1, 1000001, 777
ZIP_URL = 'https://sndlib.put.poznan.pl/download/sndlib-networks-native.zip'
TM_URL = ('https://sndlib.put.poznan.pl/download/'
          'directed-abilene-zhang-5min-over-6months-ALL-native.tgz')


def data_root():
    return Path(os.environ.get('SMR_SNDLIB', '~/papers/data/sndlib')).expanduser()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def new(*paths):
    for path in paths:
        if Path(path).exists():
            raise FileExistsError(path)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def read_json(path):
    return json.loads(Path(path).read_text())


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', newline='') as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


def tm_files(root=None):
    return sorted((root or data_root()).joinpath('abilene_tm').rglob('demandMatrix*.txt'))


def data_fingerprint(root=None):
    root = root or data_root()
    paths = {'zip': root / 'networks_native.zip',
             'tgz': root / TM_URL.rsplit('/', 1)[1],
             'abilene': root / 'sndlib-networks-native/abilene.txt',
             'geant': root / 'sndlib-networks-native/geant.txt'}
    files = {k: dict(path=str(p.relative_to(root)), size=p.stat().st_size,
                     sha256=sha256(p)) for k, p in paths.items()}
    tms = tm_files(root)
    if not tms:
        raise FileNotFoundError('no Abilene TM files')
    # Canonical UTF-8 serialization, sorted by basename; final newline included.
    digest = hashlib.sha256()
    for p in tms:
        digest.update(f'{p.name}\t{sha256(p)}\n'.encode())
    return dict(urls=dict(networks=ZIP_URL, traffic=TM_URL), files=files,
                tm_file_count=len(tms), tm_pairs_sha256=digest.hexdigest(),
                tm_digest_format='sorted basename<TAB>sha256<LF>', data_root=str(root))


def fetch(out=OUT):
    new(out / 'data_manifest.json')
    result = data_fingerprint()
    write_json(out / 'data_manifest.json', result)
    print(json.dumps(dict(command='fetch', tm_file_count=result['tm_file_count'])), flush=True)


def sections(text):
    result, current = {}, None
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        match = re.fullmatch(r'(NODES|LINKS|DEMANDS)\s*\(', line)
        if match:
            current = match[1]
            result[current] = []
        elif current and line == ')':
            current = None
        elif current and line:
            result[current].append(line)
    if set(result) != {'NODES', 'LINKS', 'DEMANDS'}:
        raise ValueError('missing SNDlib section')
    return result


def parse_native(path, uniform_capacity=None):
    ss = sections(Path(path).read_text())
    nodes = sorted(line.split()[0] for line in ss['NODES'])
    if len(set(nodes)) != len(nodes):
        raise ValueError('duplicate node')
    links = []
    for line in ss['LINKS']:
        m = re.match(r'(\S+)\s*\(\s*(\S+)\s+(\S+)\s*\)\s+(\S+)', line)
        if not m:
            raise ValueError(f'malformed link: {line}')
        name, u, v, cap = m.groups()
        cap = float(cap) if uniform_capacity is None else float(uniform_capacity)
        if u not in nodes or v not in nodes or cap <= 0 or not math.isfinite(cap):
            raise ValueError(f'invalid link: {name}')
        for a, b in ((u, v), (v, u)):
            links.append(dict(id=f'{name}:{a}>{b}', source=a, target=b, capacity=cap))
    demands = []
    for line in ss['DEMANDS']:
        m = re.fullmatch(r'(\S+)\s*\(\s*(\S+)\s+(\S+)\s*\)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if not m:
            raise ValueError(f'malformed demand: {line}')
        name, u, v, unit, value, _ = m.groups()
        value = float(value)
        if u not in nodes or v not in nodes or u == v or float(unit) <= 0 or value < 0 or not math.isfinite(value):
            raise ValueError(f'invalid demand: {name}')
        demands.append(dict(id=name, source=u, target=v, value=value))
    links.sort(key=lambda e: (e['source'], e['target'], e['id']))
    demands.sort(key=lambda d: d['id'])
    if len({(e['source'], e['target']) for e in links}) != len(links):
        raise ValueError('parallel links require an explicit path tie rule')
    if len({d['id'] for d in demands}) != len(demands):
        raise ValueError('duplicate demand')
    return dict(nodes=nodes, links=links, demands=demands)


def shortest(graph, source, target, banned_nodes=(), banned_edges=()):
    """Dijkstra on (hop count, complete node-id sequence)."""
    queue, seen = [(0, (source,))], set()
    while queue:
        dist, path = heapq.heappop(queue)
        u = path[-1]
        if u in seen or u in banned_nodes:
            continue
        seen.add(u)
        if u == target:
            return path
        for v in sorted(graph[u]):
            if v not in seen and v not in banned_nodes and (u, v) not in banned_edges:
                heapq.heappush(queue, (dist + 1, path + (v,)))
    return None


def two_paths(graph, source, target):
    """Yen k=2: remove each first-path edge at its spur; ban root nodes."""
    first = shortest(graph, source, target)
    if first is None:
        raise ValueError('unreachable demand')
    candidates = []
    for i in range(len(first) - 1):
        spur = shortest(graph, first[i], target, first[:i], {(first[i], first[i+1])})
        if spur:
            path = first[:i] + spur
            candidates.append((len(path), path))
    return first, min(candidates)[1] if candidates else None


def prepare_network(network, rho, values=None):
    graph = {node: set() for node in network['nodes']}
    edge_index = {}
    for i, e in enumerate(network['links']):
        graph[e['source']].add(e['target'])
        edge_index[e['source'], e['target']] = i
    demands = []
    for d in network['demands']:
        stay, switch = two_paths(graph, d['source'], d['target'])
        demands.append(dict(d, value=d['value'] if values is None else float(values[d['id']]),
                            stay=list(stay), switch=list(switch) if switch else None))
    incidence = np.zeros((len(network['links']), len(demands)))
    for j, d in enumerate(demands):
        for u, v in zip(d['stay'][:-1], d['stay'][1:]):
            incidence[edge_index[u, v], j] = 1
    base = np.array([d['value'] for d in demands])
    caps = np.array([e['capacity'] for e in network['links']])
    utils = incidence @ base / caps
    if utils.max() <= 0:
        raise ValueError('zero network demand')
    # Links sorted source/target/id; the first lexicographic maximizer wins.
    b = int(np.argmax(utils))
    alpha = float(rho / utils[b])
    candidates = []
    for j, d in enumerate(demands):
        switched_edges = set(zip(d['switch'][:-1], d['switch'][1:])) if d['switch'] else set()
        if incidence[b, j] and d['switch'] and (network['links'][b]['source'], network['links'][b]['target']) not in switched_edges:
            candidates.append(d['id'])
    by_id = {d['id']: d for d in demands}
    candidates.sort(key=lambda name: (-by_id[name]['value'], name))
    if len(candidates) < 3:
        raise ValueError(f'only {len(candidates)} manageable ODs')
    return dict(nodes=network['nodes'], links=network['links'], demands=demands,
                rho=rho, alpha=alpha, bottleneck=network['links'][b]['id'],
                candidates=candidates, managed_sets=[[name] for name in candidates[:3]] + [candidates[:2]])


@dataclass
class Model:
    weights: np.ndarray  # action, link, OD; mean rates included
    capacity: np.ndarray
    kappa: np.ndarray
    beta: float
    od_ids: list
    link_ids: list


def make_model(spec, reduced=True):
    demands, links = spec['network']['demands'], spec['network']['links']
    managed = spec['managed']
    index = {(e['source'], e['target']): i for i, e in enumerate(links)}
    weights = np.zeros((2**len(managed), len(links), len(demands)))
    for a in range(len(weights)):
        for j, d in enumerate(demands):
            bit = managed.index(d['id']) if d['id'] in managed else None
            route = d['switch'] if bit is not None and (a >> bit) & 1 else d['stay']
            for u, v in zip(route[:-1], route[1:]):
                weights[a, index[u, v], j] = spec['network']['alpha'] * d['value']
    cap = np.array([e['capacity'] for e in links])
    active = ((1 + spec['beta']) * weights.sum(axis=2)).max(axis=0) > cap
    relevant = np.any(weights[:, active, :] != 0, axis=(0, 1))
    rank = sorted(range(len(demands)), key=lambda j: (-demands[j]['value'], demands[j]['id']))
    kappa = np.ones(len(demands))
    if spec['slow']:
        kappa[np.array(rank[1::2])] = .1
    if not reduced:
        active, relevant = np.ones(len(links), dtype=bool), np.ones(len(demands), dtype=bool)
    return Model(np.ascontiguousarray(weights[:, active][:, :, relevant]), cap[active], kappa[relevant],
                 spec['beta'], [d['id'] for j, d in enumerate(demands) if relevant[j]],
                 [e['id'] for j, e in enumerate(links) if active[j]])


def design(out=OUT):
    new(out / 'design.json', out / 'regimes.json')
    if not (out / 'data_manifest.json').exists():
        raise FileNotFoundError('run fetch first')
    networks, specs = {}, []
    for prefix, name in (('A', 'abilene'), ('G', 'geant')):
        net = parse_native(data_root() / 'sndlib-networks-native' / f'{name}.txt',
                           uniform_capacity=10000 if prefix == 'G' else None)
        networks[name] = {}
        for rho in (.8, .9):
            prepared = prepare_network(net, rho)
            networks[name][str(rho)] = prepared
            for set_i, managed in enumerate(prepared['managed_sets'], 1):
                for beta in (.3, .6):
                    for slow in (0, 1):
                        spec = dict(id=f'{prefix}{set_i}_r{round(rho*100)}_b{round(beta*10)}_s{slow}',
                                    topology=name, set=set_i, rho=rho, beta=beta, slow=slow,
                                    managed=managed, network=prepared)
                        model = make_model(spec)
                        spec['active_links'] = model.link_ids
                        spec['relevant_ods'] = model.od_ids
                        spec['max_action_mean_utilization'] = (model.weights.sum(axis=2) / model.capacity).max(axis=1).tolist() if len(model.capacity) else [0.] * len(model.weights)
                        specs.append(spec)
    write_json(out / 'design.json', dict(author='Doan Van Tai', networks=networks,
               active_links={s['id']: s['active_links'] for s in specs},
               limitations=['GEANT pre-installed capacities are zero; every directed link uses 10000 Mb/s.',
                            'Offered loads have no downstream shaping; c=0.',
                            'Active-link reduction assumes initially zero queues on inactive links.'],
               tie_rules=dict(path='hop count then lexicographic complete node-id sequence',
                              bottleneck='lexicographic (source,target,link id)', action='lowest action index'),
               n_regimes=len(specs)))
    write_json(out / 'regimes.json', specs)
    print(json.dumps(dict(command='design', n_regimes=len(specs),
                         active_links_range=[min(len(s['active_links']) for s in specs), max(len(s['active_links']) for s in specs)])), flush=True)


def fluid_step(q, load, capacity, dt):
    q, load, capacity = np.broadcast_arrays(np.asarray(q, dtype=float), load, capacity)
    drift = load - capacity
    end = np.maximum(0., q + drift * dt)
    clip = q + drift * dt < 0
    cost = (q + end) * dt / 2
    np.divide(q*q, -2*drift, out=cost, where=clip)
    return end, cost


def seed_for(seed, regime, stream=0):
    token = int.from_bytes(hashlib.sha256(regime.encode()).digest()[:4], 'little')
    return int(np.random.SeedSequence([seed, token, stream]).generate_state(1, dtype=np.uint64)[0])


_CPP = r'''
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <random>
#include <vector>
using std::vector;
struct RNG {
 std::mt19937_64 r;
 RNG(uint64_t s):r(s){}
 double uniform(){return (r()>>11)*0x1.0p-53;}
};
// Retain the original OD order. Removing additions of positive zero is
// bitwise lossless, including for queues, clipping costs and RNG streams.
struct Sparse {
 vector<int> ptr,idx;vector<double>value;
 Sparse(int A,int E,int D,const double*w):ptr(A*E+1,0){
  for(int ae=0;ae<A*E;ae++){
   for(int j=0;j<D;j++)if(w[ae*D+j]!=0){idx.push_back(j);value.push_back(w[ae*D+j]);}
   ptr[ae+1]=(int)idx.size();
  }
 }
 double load(int ae,const vector<double>&m,double beta)const{
  double sum=0;for(int z=ptr[ae];z<ptr[ae+1];z++)sum+=value[z]*(1+beta*m[idx[z]]);return sum;
 }
};
static double step(double &q,double drift,double dt){
 double end=q+drift*dt, cost;
 if(end<0) {cost=q*q/(-2*drift); q=0;}
 else {cost=(q+end)*dt/2; q=end;}
 return cost;
}
// Cumulative discrete mean drift and cost, using long double to reduce
// cancellation in finite geometric sums. No time-grid approximation here.
static long double geom(long double lr,int n){return -expm1l(lr*n)/(-expm1l(lr));}
struct Mean {
 long double d,bf,bs,lf,ls,dt;
 long double drift(int k){return d+bf*expl(lf*k)+bs*expl(ls*k);}
 long double delta(int st,int n){return dt*(d*n+bf*expl(lf*st)*geom(lf,n)+bs*expl(ls*st)*geom(ls,n));}
 void uncut(long double &q,long double &cost,int st,int n){
  if(!n)return;
  long double gf=geom(lf,n),gs=geom(ls,n);
  cost += q*n*dt+d*dt*dt*n*n/2
       + bf*expl(lf*st)*dt*dt*((n-gf)/(-expm1l(lf))+gf/2)
       + bs*expl(ls*st)*dt*dt*((n-gs)/(-expm1l(ls))+gs/2);
  q += delta(st,n);
 }
 void segment(long double &q,long double &cost,int st,int n){
  if(!n)return;
  if(drift(st)>=0 || q+delta(st,n)>=0){uncut(q,cost,st,n);return;}
  int lo=1,hi=n;
  while(lo<hi){int mid=(lo+hi)/2;if(q+delta(st,mid)<0)hi=mid;else lo=mid+1;}
  uncut(q,cost,st,lo-1);
  cost += q*q/(-2*drift(st+lo-1));q=0;
 }
 vector<int> signs(int n){
  vector<int> monotone{0,n};
  if(bf*bs<0){
   long double v=-bs*expm1l(ls)/(bf*expm1l(lf));
   if(v>0){long double root=logl(v)/(lf-ls);
    if(root>=0 && root<n-1)monotone.push_back((int)floorl(root)+1);
   }
  }
  std::sort(monotone.begin(),monotone.end());
  vector<int> cuts=monotone;
  for(size_t i=1;i<monotone.size();i++){
   int a=monotone[i-1],b=monotone[i];
   if(b<=a || (drift(a)>=0)==(drift(b-1)>=0))continue;
   bool start=drift(a)>=0;int lo=a+1,hi=b-1;
   while(lo<hi){int m=(lo+hi)/2;if((drift(m)>=0)==start)lo=m+1;else hi=m;}
   cuts.push_back(lo);
  }
  std::sort(cuts.begin(),cuts.end());cuts.erase(std::unique(cuts.begin(),cuts.end()),cuts.end());return cuts;
 }
};
extern "C" {
void twin(int N,int A,int E,int D,int H,const double*w,const double*cap,const double*kap,
 double beta,double dt,const int*hs,const double*modes,const double*queues,double*out){
 for(int i=0;i<N;i++)for(int a=0;a<A;a++)for(int e=0;e<E;e++){
  long double mu=0,bf=0,bs=0;
  for(int j=0;j<D;j++) {double z=w[(a*E+e)*D+j];mu+=z;
   if(kap[j]==1)bf+=z*beta*modes[i*D+j];else bs+=z*beta*modes[i*D+j];}
  Mean f{mu-cap[e],bf,bs,-2*dt,-.2*dt,dt};
  vector<int> cuts=f.signs(hs[H-1]);
  long double q=queues[i*E+e],cost=0;int st=0,seg=1;
  for(int k=0;k<H;k++){
   while(st<hs[k]){while(seg<(int)cuts.size() && cuts[seg]<=st)seg++;
    int end=std::min(hs[k],cuts[seg]);f.segment(q,cost,st,end-st);st=end;}
   out[(i*A+a)*H+k]+=(double)cost;
  }
 }
}
// Conditional futures, same mode path for EVERY action. A=1 is also the
// forward posterior kernel. Modes at t govern [t,t+dt); flip at the end.
void futures(int N,int A,int E,int D,int H,const double*w,const double*cap,const double*kap,
 double beta,double dt,const int*hs,const double*initial_m,const double*initial_q,
 uint64_t seed,double*out,double*final_m,double*final_q){
 RNG rng(seed);vector<double>p(D);for(int j=0;j<D;j++)p[j]=-expm1(-2*kap[j]*dt)/2;
 Sparse route(A,E,D,w);
 for(int i=0;i<N;i++){
  vector<double>m(initial_m+i*D,initial_m+(i+1)*D),q(A*E),cost(A,0);
  for(int a=0;a<A;a++)for(int e=0;e<E;e++)q[a*E+e]=initial_q[i*E+e];
  int ck=0;
  for(int t=0;t<hs[H-1];t++){
   for(int a=0;a<A;a++)for(int e=0;e<E;e++){
    double load=route.load(a*E+e,m,beta);
    cost[a]+=step(q[a*E+e],load-cap[e],dt);
   }
   for(int j=0;j<D;j++)if(rng.uniform()<p[j])m[j]=-m[j];
   if(t+1==hs[ck]){for(int a=0;a<A;a++)out[(i*A+a)*H+ck]=cost[a];ck++;}
  }
  if(final_m)std::copy(m.begin(),m.end(),final_m+i*D);
  if(final_q)std::copy(q.begin(),q.begin()+E,final_q+i*E);
 }
}
// Long CRN run with checkpointed states and step cost rates after burn-in.
void trajectory(int A,int E,int D,int burn,int steps,int C,const int*check,
 const double*w,const double*cap,const double*kap,double beta,double dt,uint64_t seed,
 double*costrate,double*backlog,double*saved_m,double*saved_q){
 RNG rng(seed);vector<double>m(D),p(D),q(A*E,0);
 Sparse route(A,E,D,w);
 for(int j=0;j<D;j++){m[j]=rng.uniform()<.5?-1:1;p[j]=-expm1(-2*kap[j]*dt)/2;}
 int ck=0;
 for(int t=0;t<=burn+steps;t++){
  if(ck<C && t==check[ck]){std::copy(m.begin(),m.end(),saved_m+ck*D);
   std::copy(q.begin(),q.begin()+E,saved_q+ck*E);ck++;}
  if(t==burn+steps)break;
  if(t>=burn){double z=0;for(int e=0;e<E;e++)z+=q[e];backlog[t-burn]=z;}
  for(int a=0;a<A;a++){
   double cost=0;for(int e=0;e<E;e++){
    double load=route.load(a*E+e,m,beta);
    cost+=step(q[a*E+e],load-cap[e],dt);
   }
   if(t>=burn)costrate[(t-burn)*A+a]=cost/dt;
  }
  for(int j=0;j<D;j++)if(rng.uniform()<p[j])m[j]=-m[j];
 }
}
}
'''

_LIB = None


def native():
    global _LIB
    if _LIB is None:
        digest = hashlib.sha256(_CPP.encode()).hexdigest()[:20]
        # Derived build products, never outside the authorized writable roots.
        build = Path(tempfile.gettempdir()) / f'smr_ev_te_{os.getuid()}_{digest}'
        build.mkdir(exist_ok=True)
        library = build / 'kernel.so'
        if not library.exists():
            src = build / f'kernel_{os.getpid()}.cpp'
            target = build / f'kernel_{os.getpid()}.so'
            with src.open('x') as f:
                f.write(_CPP)
            subprocess.run(['g++', '-std=c++17', '-O3', '-ffp-contract=off', '-shared', '-fPIC',
                            str(src), '-o', str(target)], check=True, capture_output=True)
            os.replace(target, library)
        lib = ct.CDLL(str(library))
        f64 = np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS')
        i32 = np.ctypeslib.ndpointer(dtype=np.int32, flags='C_CONTIGUOUS')
        lib.twin.argtypes = [ct.c_int]*5 + [f64]*3 + [ct.c_double]*2 + [i32] + [f64]*3
        lib.futures.argtypes = [ct.c_int]*5 + [f64]*3 + [ct.c_double]*2 + [i32] + [f64]*2 + [ct.c_uint64] + [f64]*3
        lib.trajectory.argtypes = [ct.c_int]*6 + [i32] + [f64]*3 + [ct.c_double]*2 + [ct.c_uint64] + [f64]*4
        for name in ('twin', 'futures', 'trajectory'):
            getattr(lib, name).restype = None
        _LIB = lib
    return _LIB


def _arrays(model):
    return [np.ascontiguousarray(x, dtype=np.float64) for x in (model.weights, model.capacity, model.kappa)]


def _hs(hs):
    hs = np.ascontiguousarray(hs, dtype=np.int32)
    if not len(hs) or hs[0] < 1 or np.any(np.diff(hs) <= 0):
        raise ValueError('checkpoints must be positive increasing steps')
    return hs


def twin_costs(model, modes, queues, dt, hs):
    modes, queues = [np.ascontiguousarray(x, dtype=np.float64) for x in (modes, queues)]
    a, e, d = model.weights.shape
    hs = _hs(hs)
    out = np.zeros((len(modes), a, len(hs)))
    native().twin(len(modes), a, e, d, len(hs), *_arrays(model), model.beta, dt, hs, modes, queues, out)
    return out


def futures(model, modes, queues, dt, hs, seed):
    modes, queues = [np.ascontiguousarray(x, dtype=np.float64) for x in (modes, queues)]
    a, e, d = model.weights.shape
    hs = _hs(hs)
    out = np.empty((len(modes), a, len(hs)))
    final_m, final_q = np.empty_like(modes), np.empty_like(queues)
    native().futures(len(modes), a, e, d, len(hs), *_arrays(model), model.beta, dt, hs,
                     modes, queues, seed, out, final_m, final_q)
    return out, final_m, final_q


def posterior(model, modes, queues, dt, tau_steps, k, seed):
    stay = Model(model.weights[:1], model.capacity, model.kappa, model.beta, model.od_ids, model.link_ids)
    _, m, q = futures(stay, np.repeat(modes, k, axis=0), np.repeat(queues, k, axis=0),
                      dt, [tau_steps], seed)
    return m, q


def trajectory(model, dt, burn_steps, steps, seed, checkpoints=()):
    a, e, d = model.weights.shape
    checkpoints = np.ascontiguousarray(checkpoints, dtype=np.int32)
    if len(checkpoints) and (checkpoints[0] < 0 or checkpoints[-1] > burn_steps + steps or np.any(np.diff(checkpoints) <= 0)):
        raise ValueError('invalid state checkpoints')
    rates, backlog = np.empty((steps, a)), np.empty(steps)
    m, q = np.empty((len(checkpoints), d)), np.empty((len(checkpoints), e))
    native().trajectory(a, e, d, burn_steps, steps, len(checkpoints), checkpoints, *_arrays(model),
                        model.beta, dt, seed, rates, backlog, m, q)
    return rates, backlog, m, q


def grid(ti, dt):
    return ([max(1, int(np.rint(t * ti / dt))) for t in TAUS],
            [max(1, int(np.rint(h * ti / dt))) for h in HS])


def instances(model, ti, dt, n, seed):
    taus, _ = grid(ti, dt)
    burn = math.ceil(50 * ti / dt)
    gap = max(1, int(np.rint(3 * ti / dt)))
    now = burn + max(taus) + np.arange(n) * gap
    checks = np.unique(np.r_[now, *(now - tau for tau in taus)])
    stay = Model(model.weights[:1], model.capacity, model.kappa, model.beta, model.od_ids, model.link_ids)
    _, _, m, q = trajectory(stay, dt, 0, int(now[-1]), seed, checks)
    ix = np.searchsorted(checks, now)
    stale = [(m[np.searchsorted(checks, now - tau)], q[np.searchsorted(checks, now - tau)]) for tau in taus]
    return (m[ix], q[ix]), stale


def choose_twins(model, fresh, stale, ti, dt, k, seed, truth=False, r_dec=128):
    taus, hs = grid(ti, dt)
    n = len(fresh[0])
    choices = np.empty((n, len(taus), len(PIPES) if truth else 4, len(hs)), dtype=np.int16)
    fresh_choice = twin_costs(model, *fresh, dt, hs).argmin(axis=1)
    choices[:, :, 0] = fresh_choice[:, None, :]
    if truth:
        cm, cq = [np.repeat(x, r_dec, axis=0) for x in fresh]
        vc, _, _ = futures(model, cm, cq, dt, hs, seed_for(seed, 'M1_new'))
        decision = vc.reshape(n, r_dec, len(model.weights), len(hs)).mean(axis=1).argmin(axis=1)
        choices[:, :, 4] = decision[:, None, :]
    for t, ((sm, sq), age) in enumerate(zip(stale, taus)):
        pm, pq = posterior(model, sm, sq, dt, age, k, seed_for(seed, 'posterior', t))
        old = twin_costs(model, pm, pq, dt, hs).reshape(n, k, len(model.weights), len(hs)).mean(axis=1)
        choices[:, t, 1] = old.argmin(axis=1)
        choices[:, t, 2] = twin_costs(model, sm, sq, dt, hs).argmin(axis=1)
        conditional_m = sm * np.exp(-2 * model.kappa * age * dt)
        ce_q = pq.reshape(n, k, -1).mean(axis=1)
        choices[:, t, 3] = twin_costs(model, conditional_m, ce_q, dt, hs).argmin(axis=1)
        if truth:
            one, _, _ = futures(model, pm, pq, dt, hs, seed_for(seed, 'M1_old', t))
            choices[:, t, 5] = one.reshape(n, k, len(model.weights), len(hs)).mean(axis=1).argmin(axis=1)
    return choices


def estimate_tint(backlog, dt):
    try:
        value, censored = tint(backlog, dt)
        return value, censored, None
    except ValueError as error:
        return None, True, str(error)


def train_one(task):
    spec, out, n_train, k = task
    start = time.process_time()
    model = make_model(spec)
    # Train-only calibration resolves dt/T_int circularity, explicitly recorded.
    pilot_dt = .05
    _, b, _, _ = trajectory(model, pilot_dt, 10000, 400000, seed_for(TRAIN_SEED, spec['id'], 0))
    ti, censored, error = estimate_tint(b, pilot_dt)
    pq = float((b > 0).mean())
    base = dict(id=spec['id'], seed=TRAIN_SEED, n_train=n_train, K=k,
                calibration=dict(dt=pilot_dt, T=20000., burn=500., T_int=ti,
                                 censored=censored, P_Q_positive=pq, error=error))
    reasons = []
    if censored:
        reasons.append('T_int censored' + (f': {error}' if error else ''))
    if pq < .01:
        reasons.append('P(total backlog > 0) < 0.01')
    if not reasons:
        dt = min(.05, ti / 40)
        duration = max(20000., 2000 * ti)
        burn = math.ceil(50 * ti / dt)
        steps = math.ceil(duration / dt)
        rates, b, _, _ = trajectory(model, dt, burn, steps, seed_for(TRAIN_SEED, spec['id'], 1))
        check_ti, check_censored, check_error = estimate_tint(b, dt)
        pq = float((b > 0).mean())
        base.update(T_int=ti, dt=dt, duration=steps * dt, burn=burn * dt,
                    T_int_check=check_ti, T_int_check_censored=check_censored,
                    T_int_check_error=check_error, P_Q_positive=pq,
                    dt_rule='T_int fixed from seed-A calibration dt=0.05; final-grid T_int recorded separately',
                    r_a=[batch_stats(rates[:, a]) for a in range(len(model.weights))],
                    s_type=(rates.mean(axis=0) - rates[:, 0].mean()).tolist(),
                    s_type_se=[batch_stats(rates[:, a]-rates[:, 0])['se'] for a in range(len(model.weights))],
                    nonstationary_actions=[a for a, u in enumerate(spec['max_action_mean_utilization']) if u >= 1],
                    r_a_interpretation='finite-duration training average; no finite stationary mean for mean utilization >= 1',
                    mean_utilization=spec['max_action_mean_utilization'])
        if check_censored:
            reasons.append('final-grid T_int censored' + (f': {check_error}' if check_error else ''))
        if pq < .01:
            reasons.append('final-grid P(total backlog > 0) < 0.01')
        if not reasons:
            fresh, stale = instances(model, ti, dt, n_train, seed_for(TRAIN_SEED, spec['id'], 2))
            counts = np.zeros((4, 4, len(HS), len(model.weights)), dtype=np.int64)
            for left in range(0, n_train, 32):
                sl = slice(left, min(left+32, n_train))
                choices = choose_twins(model, tuple(x[sl] for x in fresh),
                                      [tuple(x[sl] for x in s) for s in stale], ti, dt, k,
                                      seed_for(TRAIN_SEED, spec['id'], 100+left))
                for a in range(len(model.weights)):
                    counts[:, :, :, a] += (choices == a).sum(axis=0)
            base['F'] = (counts/n_train).tolist()  # tau, [new,M0old,Pold,CEold], h, action
            base['F_counts'] = counts.tolist()
            base['tau_steps'], base['h_steps'] = grid(ti, dt)
    base.update(excluded=bool(reasons), exclusion_reasons=reasons, CPU=time.process_time()-start)
    write_json(out / 'train' / f"{spec['id']}.json", base)
    return dict(id=spec['id'], excluded=bool(reasons), reasons=reasons, CPU=base['CPU'],
                T_int=base.get('T_int', ti))


def train(workers=8, out=OUT, n_train=2000, k=128):
    specs = read_json(out / 'regimes.json')
    new(out / 'design_excluded.json', *(out / 'train' / f"{s['id']}.json" for s in specs))
    native()  # Compile once, before spawning.
    tasks = [(s, out, n_train, k) for s in specs]
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
        results = []
        for result in pool.map(train_one, tasks):
            results.append(result)
            print(json.dumps(result), flush=True)
    write_json(out / 'design_excluded.json', dict(excluded=[r for r in results if r['excluded']],
                                               retained=[r['id'] for r in results if not r['excluded']]))


def predictor(rates, old, fresh, h):
    slope = np.sum(np.asarray(rates) * (np.asarray(old)-np.asarray(fresh)), axis=-1)
    return slope, np.asarray(h) * slope


def predict(out=OUT):
    new(out / 'predictions.csv')
    rows = []
    for spec in read_json(out / 'regimes.json'):
        tr = read_json(out / 'train' / f"{spec['id']}.json")
        if tr['excluded']:
            continue
        rates = [r['mean'] for r in tr['r_a']]
        f = np.array(tr['F'])
        hh = np.array(tr['h_steps']) * tr['dt']
        for t, tau in enumerate(TAUS):
            for twin, col in (('M0', 1), ('P', 2), ('CE', 3)):
                slope, level = predictor(rates, f[t, col], f[t, 0], hh)
                row = dict(regime=spec['id'], tau_mult=tau, tau=tr['tau_steps'][t]*tr['dt'], twin=twin,
                           T_int=tr['T_int'], dt=tr['dt'], r_a=json.dumps(rates),
                           s_type=json.dumps(tr['s_type']),
                           stationary_rate_valid=not bool(tr.get('nonstationary_actions')),
                           nonstationary_actions=json.dumps(tr.get('nonstationary_actions', [])),
                           Delta_pred=float(level[-1]-level[3]), level_pred=float(level[-1]))
                row.update({f'slope_h{h}': float(slope[j]) for j, h in enumerate(HS)})
                row.update({f'level_h{h}': float(level[j]) for j, h in enumerate(HS)})
                rows.append(row)
    write_csv(out / 'predictions.csv', rows)
    print(json.dumps(dict(command='predict', rows=len(rows))), flush=True)


def lock_inputs(out=OUT):
    """Complete mandatory manifest for Claude's later {sha256: {...}} lock."""
    # Claude 16/11 (pre-lock review): Arm R (ev_te_trace.py) is descriptive and not part of the confirmatory lock.
    paths = [ROOT / 'experiments/ext_validity/ev_te.py',
             out / 'regimes.json', out / 'predictions.csv', out / 'data_manifest.json',
             out / 'design_excluded.json']
    specs = read_json(out / 'regimes.json')
    if len(specs) != 64 or len({s['id'] for s in specs}) != 64:
        raise ValueError('lock needs the complete 64-regime design')
    required_train = {out / 'train' / f"{s['id']}.json" for s in specs}
    if set((out / 'train').glob('*.json')) != required_train:
        raise ValueError('incomplete or unexpected regime training inputs')
    paths += sorted(required_train)
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha256(p) for p in paths}


def verify_lock(out=OUT):
    lock = read_json(out / 'lock.json')  # Missing lock deliberately fails closed.
    expected = lock.get('sha256', {})
    actual = lock_inputs(out)
    if not actual.keys() <= expected.keys():
        raise ValueError('lock omits mandatory code, predictions, regimes or training files')
    for name, value in expected.items():
        p = Path(name) if Path(name).is_absolute() else ROOT / name
        if sha256(p) != value:
            raise ValueError(f'LOCK_FAIL SHA256 {name}')
    current = data_fingerprint()
    recorded = read_json(out / 'data_manifest.json')
    if any(current[key] != recorded[key] for key in ('files', 'tm_file_count', 'tm_pairs_sha256', 'urls')):
        raise ValueError('LOCK_FAIL data files or TM collection changed')
    print(f'LOCK_PASS {len(expected)} files and external data', flush=True)


def run_one(task):
    spec, tr, out, n, k, r_dec, r_eval, timing_only = task
    start, wall = time.process_time(), time.perf_counter()
    seed = PILOT_SEED if timing_only else TEST_SEED
    model = make_model(spec)
    native()
    compile_cpu = time.process_time()-start
    fresh, stale = instances(model, tr['T_int'], tr['dt'], n, seed_for(seed, spec['id'], 0))
    costs = np.empty((n, len(TAUS), len(PIPES), len(HS)))
    stay_costs = np.empty((n, len(HS)))
    # Work in small batches; per-instance seed streams are disjoint from training.
    for i in range(n):
        f = tuple(x[i:i+1] for x in fresh)
        s = [tuple(x[i:i+1] for x in x0) for x0 in stale]
        choices = choose_twins(model, f, s, tr['T_int'], tr['dt'], k,
                              seed_for(seed, spec['id'], 100+i), truth=True, r_dec=r_dec)
        cm, cq = [np.repeat(x, r_eval, axis=0) for x in f]
        vc, _, _ = futures(model, cm, cq, tr['dt'], tr['h_steps'], seed_for(seed, spec['id'], 100000+i))
        ev = vc.mean(axis=0)
        for t in range(len(TAUS)):
            costs[i, t] = ev[choices[0, t], np.arange(len(HS))]
        stay_costs[i] = ev[0]
    elapsed = time.process_time()-start
    meta = dict(regime=spec['id'], seed=seed, N=n, K=k, R_dec=r_dec, R_eval=r_eval,
                CPU=elapsed, CPU_per_instance=elapsed/n, workload_CPU_per_instance=(elapsed-compile_cpu)/n,
                wall=time.perf_counter()-wall,
                peak_memory_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                timing_only=timing_only, dt=tr['dt'], T_int=tr['T_int'],
                h_steps=tr['h_steps'], tau_steps=tr['tau_steps'], pipelines=list(PIPES))
    if not timing_only:
        path = out / 'raw' / f"{spec['id']}.npz"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            np.savez_compressed(f, pipeline_V=costs, V_stay=stay_costs,
                                h=np.array(tr['h_steps'])*tr['dt'], tau=np.array(tr['tau_steps'])*tr['dt'],
                                pipelines=np.array(PIPES))
        write_json(path.with_suffix('.json'), meta)
    return meta


def run(workers=1, regimes=None, timing_only=False, out=OUT, n=None, k=128, r_dec=128, r_eval=256):
    if min(workers, k, r_dec, r_eval) < 1 or (n is not None and n < 1):
        raise ValueError('positive workers/N/K/R required')
    if timing_only:
        # The brief explicitly orders this before Claude creates the truth lock.
        # The exception is ONLY seed 777 and the cost-free timing.json writer.
        new(out / 'timing.json')
        if (out / 'lock.json').exists():
            verify_lock(out)
    else:
        verify_lock(out)  # Before input loading, compilation or engine work.
    specs = read_json(out / 'regimes.json')
    wanted = set(regimes) if regimes else {s['id'] for s in specs}
    if not wanted <= {s['id'] for s in specs}:
        raise ValueError('unknown regime id')
    tasks = []
    for spec in specs:
        if spec['id'] not in wanted:
            continue
        tr = read_json(out / 'train' / f"{spec['id']}.json")
        if tr['excluded']:
            if regimes:
                raise ValueError(f"excluded regime {spec['id']}")
            continue
        if not timing_only:
            new(out / 'raw' / f"{spec['id']}.npz", out / 'raw' / f"{spec['id']}.json")
        tasks.append((spec, tr, out, n or (3 if timing_only else 500), k, r_dec, r_eval, timing_only))
    native()
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
        results = list(pool.map(run_one, tasks))
    if timing_only:
        write_json(out / 'timing.json', dict(seed=PILOT_SEED, timing_only=True,
                   lock_required=False, lock_exception='training-only timing pilot expressly authorized by brief',
                   regimes=results, no_costs_written=True))
    print(json.dumps(dict(command='timing' if timing_only else 'run', completed=len(results))), flush=True)


def paired_stats(values):
    values = np.asarray(values)
    return float(values.mean()), float(values.std(ddof=1)/np.sqrt(len(values)))


def hypothesis_counts(cells):
    rules = dict(H1=.90, H2=.90, H3=.80, H4=.90)
    result = {}
    for name, threshold in rules.items():
        eligible = [c for c in cells if c[f'{name}_eligible']]
        n, passed = len(eligible), sum(c[f'{name}_pass'] for c in eligible)
        result[name] = dict(eligible=n, passed=passed, threshold=threshold,
                            fraction=passed/n if n else None,
                            verdict=('PASS' if passed/n >= threshold else 'FAIL') if n else 'NOT_EVALUABLE')
    return result


def score(out=OUT):
    new(out / 'score.json', out / 'score_cells.csv')
    verify_lock(out)
    predictions = {(r['regime'], float(r['tau_mult']), r['twin']): r
                   for r in csv.DictReader((out / 'predictions.csv').open())}
    records, verdict_cells = [], []
    for spec in read_json(out / 'regimes.json'):
        tr = read_json(out / 'train' / f"{spec['id']}.json")
        if tr['excluded']:
            continue
        meta = read_json(out / 'raw' / f"{spec['id']}.json")
        if meta['seed'] != TEST_SEED or meta['timing_only']:
            raise ValueError('truth seed/provenance mismatch')
        with np.load(out / 'raw' / f"{spec['id']}.npz", allow_pickle=False) as raw:
            vv, stay = raw['pipeline_V'], raw['V_stay']
        for t, tau in enumerate(TAUS):
            v = vv[:, t]
            ref = v[:, 4].mean(axis=0)
            if np.any(ref <= 0):
                raise ValueError('nonpositive C_ref; score undefined')
            gaps = dict(GS_M0=v[:, 1]-v[:, 0], GS_P=v[:, 2]-v[:, 0], GS_CE=v[:, 3]-v[:, 0],
                        GM=v[:, 1]-v[:, 5], Gamma=v[:, 0]+v[:, 5]-v[:, 1]-v[:, 4])
            for j, h in enumerate(HS):
                row = dict(regime=spec['id'], tau_mult=tau, h_mult=h, N=len(v), C_ref=ref[j], E_stay=stay[:, j].mean())
                row.update({f'L_{pipe}': float(v[:, p, j].mean()) for p, pipe in enumerate(PIPES)})
                for name, difference in gaps.items():
                    mean, se = paired_stats(difference[:, j])
                    row.update({name: mean, f'{name}_se': se, f'z_{name}': 100*mean/ref[j], f'z_{name}_se': 100*se/ref[j]})
                for twin in ('M0', 'P', 'CE'):
                    pred = predictions[spec['id'], tau, twin]
                    row[f'pred_{twin}_pp'] = 100*float(pred[f'level_h{h}'])/ref[j]
                    delta, se = paired_stats(100*(gaps['GS_'+twin][:, -1]-gaps['GS_'+twin][:, 3])/ref[-1])
                    row[f'Delta_{twin}_meas_pp'], row[f'Delta_{twin}_se_pp'] = delta, se
                    row[f'Delta_{twin}_pred_pp'] = 100*float(pred['Delta_pred'])/ref[-1]
                records.append(row)
            last = records[-1]
            z, pred = last['z_GS_M0'], last['pred_M0_pp']
            dm, dp, se = (last[n] for n in ('Delta_M0_meas_pp', 'Delta_M0_pred_pp', 'Delta_M0_se_pp'))
            # Claude 16/11 (pre-lock, CARD D1): Prop 1 needs finite stationary rates for every action, so regimes
            # with an unstable action (mean utilization > 1; training flag) are descriptive only, not in H1-H4.
            valid = predictions[spec['id'], tau, 'M0']['stationary_rate_valid'] == 'True'
            eligible2 = valid and abs(dp) >= .25 and abs(dm) >= 2*se
            verdict_cells.append(dict(regime=spec['id'], tau_mult=tau, stationary_rate_valid=valid,
                H1_eligible=valid and abs(z) >= .25 and abs(pred) >= .25, H1_pass=bool(np.sign(z) == np.sign(pred)),
                H2_eligible=eligible2, H2_pass=bool(np.sign(dm) == np.sign(dp)),
                H3_eligible=eligible2, H3_pass=abs(dm-dp) <= max(.25, .25*abs(dp), 2*se),
                H4_eligible=valid, H4_pass=abs(last['Delta_P_meas_pp']) <= max(.25, 2*last['Delta_P_se_pp'])))
    write_csv(out / 'score_cells.csv', records)
    write_json(out / 'score.json', dict(hypotheses=hypothesis_counts(verdict_cells), cells=verdict_cells,
               n_cells=len(verdict_cells), descriptive_harm={name: sum(r[f'z_GS_{name}'] < -.1 for r in records)
                                                          for name in ('M0', 'P', 'CE')}))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('fetch', 'design', 'train', 'predict', 'run', 'verify-lock', 'score'))
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--regimes', nargs='+')
    p.add_argument('--timing-only', action='store_true')
    p.add_argument('--N', type=int, default=None)
    p.add_argument('--K', type=int, default=128)
    p.add_argument('--R-dec', type=int, default=128)
    p.add_argument('--R-eval', type=int, default=256)
    args = p.parse_args(argv)
    if args.workers < 1:
        p.error('workers must be positive')
    if args.command != 'run' and (args.timing_only or args.regimes or args.N is not None):
        p.error('timing/regimes/N options are run-only')
    if args.command == 'train':
        train(args.workers)
    elif args.command == 'run':
        run(args.workers, args.regimes, args.timing_only, n=args.N, k=args.K, r_dec=args.R_dec, r_eval=args.R_eval)
    else:
        {'fetch': fetch, 'design': design, 'predict': predict, 'verify-lock': verify_lock, 'score': score}[args.command]()


if __name__ == '__main__':
    main()
