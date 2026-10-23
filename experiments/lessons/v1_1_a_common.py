"""Doan Van Tai — shared parameter/serialization utilities, no candidate costs."""
import csv,json,math,hashlib
from fractions import Fraction as F
from pathlib import Path
from functools import lru_cache
from smr.stationary import r2_keep
from smr.stationary_spectral import SpectralLaw
ROOT=Path(__file__).resolve().parents[2]

def clean(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x

def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(clean(obj),ensure_ascii=False,indent=2)+'\n')

def csvwrite(path,rows):
    with Path(path).open('w') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(clean(rows))

def lattice(rates,u,dt):
    a=[(r+u-10)*dt for r in rates];den=math.lcm(*(v.denominator for v in a))
    unit=F(math.gcd(*(int(v*den) for v in a)),den)
    return unit,tuple(int(v/unit) for v in a)

@lru_cache(None)
def law_for(lam,u,kappa,refinement):
    dt=F(1,120*refinement);unit,inc=lattice((lam-6,lam+6),u,dt)
    return unit,SpectralLaw(inc,*r2_keep(dt,kappa))

def parameters():
    return [(a,k,F(1,2)) for a in (F(13,2),F(15,2),F(17,2)) for k in (F(3,10),F(1),F(3))]+[(F(15,2),F(1),F(9,10))]

def manifest(out):
    write(out/'manifest.json',[dict(file=str(p.relative_to(out)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'])
