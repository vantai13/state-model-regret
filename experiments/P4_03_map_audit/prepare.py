"""Materialize exact discovery coordinates/aliases before physical calls."""
import csv
from fractions import Fraction as F
import json
from pathlib import Path
import re

from .common import ROOT,HERE,OUT,CF,METRICS,canonical,cf_keys,forbid_cf,git,require,write_once
from experiments.P4_02_reading.read_map import load_table
from experiments.P4_01_recount import recount_map as R


def zones(row):
    a,b,k,e,h,amp=R.scaled_key(row)
    result=[]
    if amp==6 and F(1,5)<=k<=1 and 1<=h<=4 and e>=F(1,2):result.append('A')
    if (amp==6 and 6<=a<=F(27,4) and F(13,2)<=b<=F(15,2)
            and F(1,20)<=k<=F(3,20) and 4<=h<=8 and F(5,8)<=e<=F(7,8)):
        result.append('AB')
    return result


def native_cases(rows,forbidden):
    by,aliases={},[]
    for row in rows:
        memberships=zones(row)
        if not memberships:continue
        a,b,k,e,h,_=R.scaled_key(row)
        parameters=list(map(str,(a,b,k,e,h,F(0))))
        forbid_cf(parameters,forbidden)
        key=canonical(parameters)
        by.setdefault(key,dict(parameters=parameters,key=list(key),aliases=[]))['aliases'].append(row['id'])
        aliases.append(dict(id=row['id'],zones=memberships,key=list(key),pilot_class=row['class'],
                            original_age=str(row['_key'][5]),
                            pilot_pctC={m:str(row[m+'_pctC']) for m in METRICS}))
    ordered=sorted(by,key=lambda k:tuple(map(F,k)))
    cases=[dict(id=f'P43_{i:04d}',**by[k]) for i,k in enumerate(ordered)]
    mapping={tuple(c['key']):c['id'] for c in cases}
    for alias in aliases:alias['native_id']=mapping[tuple(alias['key'])]
    return cases,aliases


def raw_rows(batch):
    return list(csv.DictReader(git('show',f'{R.COMMIT}:results/explore_v13/{batch}/regimes.csv').decode().splitlines()))


def bit_specs():
    resume=re.findall(r'^\[map2\] (XM2\w+) ',git('show',f'{R.COMMIT}:results/explore_v13/logs/map2_resume.log').decode(),re.M)
    selections=[('map2',resume[0],'resume_first'),('map2',resume[len(resume)//2],'resume_middle'),
                ('map2',resume[-1],'resume_last'),('plantrobust','XPR0K','after_restart_11of12'),
                ('plantrobust','XPR0D','after_restart_12of12'),('map3age','XA000','age_extension_first'),
                ('map3age','XA108','age_extension_middle'),('map3age','XA215','age_extension_last')]
    seen=set()
    for row in sorted(raw_rows('map1'),key=lambda r:r['id']):
        label=R.cls({m:float(row[m]) for m in R.NUM})
        if label not in seen:
            seen.add(label);selections.append(('map1',row['id'],'independent_supplement_'+label))
    out=[]
    for batch,rid,why in selections:
        row=next(r for r in raw_rows(batch) if r['id']==rid)
        spec=[rid,*[str(F(row[c])) for c in ('lambdaA','lambdaB','kappa','eta','h')],int(row['ref']),int(row['K']),
              str(F(row.get('c_sw','0'))),str(F(row.get('age','1'))),str(F(row.get('amp','6')))]
        fields=['Cbar','Sbar','P_flip',*METRICS]
        out.append(dict(batch=batch,id=rid,reason=why,spec=spec,expected={k:row[k] for k in fields}))
    return out


if __name__=='__main__':
    cases,aliases=native_cases(load_table(),cf_keys())
    require(len(cases)==666 and len(aliases)==684,'scope counts differ from author-approved proposal')
    target=ROOT/HERE/'cases.json'; doc=dict(cases=cases,aliases=aliases)
    if target.exists():require(json.loads(target.read_text())==doc,'existing scope differs; never overwrite')
    else:write_once(target,doc)
    specs=bit_specs()
    write_once(ROOT/HERE/'bit_specs.json',dict(rows=specs,original_K2='UNAVAILABLE_IDS; six new supplemental rows are not the historical K2'))
    ids={a['id']:a['native_id'] for a in aliases}
    print(json.dumps(dict(cases=len(cases),aliases=len(aliases),bit_specs=len(specs),
                          benchmark=[ids[x] for x in ('XM2S189','XM2S110','XM2X000','XM2X077')]),indent=2))
