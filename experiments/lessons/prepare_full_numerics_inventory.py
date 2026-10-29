"""Reserve every preregistered calibration coordinate before any CF draw."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from experiments.R3R_07_confirmation.common import digest,write_once,verified_card
from experiments.R3R_05_contract.schema import IDENTITY,canonical


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prereg',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();verified_card()
    old=Path('results/lessons/l3r_7/preparation/collision_inventory.json')
    result=json.loads(old.read_text());cfg=json.loads(a.prereg.read_text())
    result['status']='PARAMETER_ONLY_INVENTORY_V2_FULL_NUMERICS_RESERVED'
    result['parent_inventory']={'path':str(old),'sha256':digest(old)}
    result['sources'][str(a.prereg)]=digest(a.prereg)
    for job in cfg['cases']:
        la,lb,kappa,eta,h,c=map(F,job['parameters'])
        reg=dict(lambdaA=str(la),lambdaB=str(lb),u=str(2*eta),kappa=str(kappa),h=str(h),c_sw=str(c))
        key=canonical(reg)
        result['records'].append(dict(source=str(a.prereg),source_id=job['id'],
            namespace='v1.3_fixed_plant',reservation_type='registered_calibration_design_reserved',
            note='Reserve all designs, including cases not reached by the finite stop rule; not an attestation of execution.',
            coordinates={name:str(v) for name,v in zip(IDENTITY,key)},key='|'.join(map(str,key))))
    result['source_record_counts'][str(a.prereg)]=len(cfg['cases'])
    result['distinct_v13_keys']=len({r['key'] for r in result['records'] if r['namespace']=='v1.3_fixed_plant'})
    result['limitations'].append('Distances also include registered calibration designs whose outcomes may remain uncomputed.')
    write_once(a.out,result)
    print(json.dumps(dict(records=len(result['records']),distinct_v13_keys=result['distinct_v13_keys'],CF_draws=0)))


if __name__=='__main__':main()
