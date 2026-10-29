"""Exact dyadic product enclosures, evaluated on fixed decimal root proposals."""
import ctypes as C
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import mpmath as mp


@lru_cache(None)
def library():
    source=Path(__file__).with_name('native')/'dyadic_products.cpp'
    target=Path(tempfile.gettempdir())/('smr-dyadic-'+hashlib.sha256(source.read_bytes()).hexdigest()[:24]+'.so')
    if not target.exists():subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC',str(source),'-o',str(target)],check=True)
    lib=C.CDLL(str(target));lib.dyadic_derivatives.argtypes=[C.c_size_t,C.POINTER(C.c_char_p),C.POINTER(C.c_char_p)]
    lib.dyadic_derivatives.restype=C.c_char_p;return lib


def products(roots):
    encoded=[(mp.nstr(r.real,80),mp.nstr(r.imag,80)) for r in roots]
    real=(C.c_char_p*len(roots))(*(r.encode() for r,i in encoded));imag=(C.c_char_p*len(roots))(*(i.encode() for r,i in encoded))
    data=json.loads(library().dyadic_derivatives(len(roots),real,imag))
    if 'error' in data:raise ArithmeticError(data['error'])
    if data['bits']!=384 or len(data['products'])!=len(roots):raise ArithmeticError('dyadic result schema mismatch')
    intervals=[]
    for re,im,rad,exp in data['products']:
        re,im,rad=map(int,(re,im,rad));scale=mp.iv.mpf(2)**exp
        # The native ball encloses the exact products of the declared decimal
        # roots. The interval conversion is outward again at80digits.
        intervals.append(mp.iv.mpc(mp.iv.mpf([re-rad,re+rad])*scale,mp.iv.mpf([im-rad,im+rad])*scale))
    return intervals
