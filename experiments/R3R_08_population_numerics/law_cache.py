"""Content-checked stationary checkpoints shared across K/h, with exact inputs."""
import fcntl
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import os
import resource
import time
import mpmath as mp
import numpy as np
from smr.cells import lattice
from smr.stationary import r2_keep
from .native_law import NativeLaw
from .fast_law import FastLaw

SOURCES=['src/smr/stationary.py','src/smr/stationary_spectral.py',
 'experiments/R3R_07_fast_stationary/law.py',
 'experiments/R3R_07_fast_stationary/root_proposal.py',
 'experiments/R3R_08_population_numerics/native_law.py',
 'experiments/R3R_08_population_numerics/native_certificate.py',
 'experiments/R3R_08_population_numerics/dyadic.py',
 'experiments/R3R_08_population_numerics/native/dyadic_products.cpp',__file__]
MEMORY={}


def cpu():
    children=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+children.ru_utime+children.ru_stime


def fingerprint():
    return hashlib.sha256(''.join(hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES).encode()).hexdigest()


def dump(law,parameters,source):
    z=lambda x:[mp.nstr(x.real,80),mp.nstr(x.imag,80)]
    return dict(parameters=parameters,source_fingerprint=source,mpmath=mp.__version__,
                increments=list(law.increments),keep=str(law.keep),keep_error=str(law.keep_error),
                plan=law.plan,certificate=law.certificate,terms=[[z(x) for x in row] for row in law.terms],zero=[z(x) for x in law.zero])


def restore(data,parameters,source):
    if data['parameters']!=parameters or data['source_fingerprint']!=source or data['mpmath']!=mp.__version__:
        raise ValueError('stationary checkpoint provenance mismatch')
    mp.mp.dps=80;mp.iv.dps=80;law=object.__new__(NativeLaw)
    law.increments=tuple(data['increments']);law.keep=F(data['keep']);law.keep_error=F(data['keep_error'])
    law.plan=data['plan'];law.certificate=data['certificate'];law.error=mp.mpf(law.certificate['infinite_law_error_upper'])
    law.terms=[tuple(mp.mpc(*z) for z in row) for row in data['terms']];law.zero=tuple(mp.mpc(*z) for z in data['zero'])
    if len(law.terms)!=law.increments[1] or law.error>mp.mpf('1e-10'):raise ArithmeticError('invalid cached certificate')
    return law


def get(lam,u,kappa,ref,cache,progress=lambda *a,**k:None):
    parameters=[str(F(lam)),str(F(u)),str(F(kappa)),int(ref)];source=fingerprint()
    key=hashlib.sha256(json.dumps([parameters,source]).encode()).hexdigest()
    folder=Path(cache);folder.mkdir(parents=True,exist_ok=True);path=folder/(key+'.json')
    memory_key=(str(folder.resolve()),key)
    if memory_key in MEMORY:
        unit,fast,key=MEMORY[memory_key];fast.last_creation_cpu_seconds=0.
        return unit,fast,key
    constructed=0.
    with (folder/(key+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        unit,inc=lattice((F(lam)-6,F(lam)+6),F(u),F(1,120*ref))
        if path.exists():
            payload=path.read_bytes()
            if hashlib.sha256(payload).hexdigest()!=(folder/(key+'.sha256')).read_text().strip():
                raise ValueError('stationary checkpoint bytes changed')
            law=restore(json.loads(payload),parameters,source);progress('stationary_cache_hit',key=key)
        else:
            started=cpu()
            keep,ke=r2_keep(F(1,120*ref),F(kappa));d,b=-inc[0],inc[1]
            progress('stationary_started',parameters=parameters,degree=d+b)
            law=NativeLaw(inc,keep,ke,progress)
            data=dump(law,parameters,source);constructed=cpu()-started;data['cold_cpu_seconds']=constructed
            payload=(json.dumps(data,sort_keys=True)+'\n').encode()
            temporary=folder/(key+'.tmp.'+str(os.getpid()));temporary.write_bytes(payload);temporary.rename(path)
            (folder/(key+'.sha256')).write_text(hashlib.sha256(payload).hexdigest()+'\n')
            progress('stationary_completed',key=key,error=str(law.error))
        if constructed==0.:data=json.loads(path.read_text())
        fast=FastLaw(law);fast.cold_cpu_seconds=data['cold_cpu_seconds'];fast.last_creation_cpu_seconds=constructed
        MEMORY[memory_key]=(unit,fast,key)
        return unit,fast,key
