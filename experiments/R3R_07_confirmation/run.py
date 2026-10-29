"""Locked Phase4 entry point. Audited numerical/D22 backend is still DEFERRED.

No engine import, no CLI parameter to substitute levels/models/subsets or bypass
gates. Refused invocations have durable logs. Future adapter integration requires
numerics v1.3.1 and full dry-run B before this entry point can execute a batch.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import uuid

from .common import write_once
from .gates import verify_execution_receipt


def preflight(*,confirmation_run,receipt):
    if not confirmation_run:
        raise ValueError('explicit --confirmation-run required')
    if receipt is None:
        raise ValueError('committed execution receipt required')
    return verify_execution_receipt(receipt)


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--confirmation-run',action='store_true')
    p.add_argument('--receipt',type=Path)
    p.add_argument('--attempt-log-dir',type=Path,default=Path('results/CF_attempts'))
    args=p.parse_args(argv)
    record=dict(owner='Doan Van Tai',utc=datetime.now(timezone.utc).isoformat(),engine_runs=0,
                receipt=str(args.receipt),confirmation_run=args.confirmation_run)
    try:
        preflight(confirmation_run=args.confirmation_run,receipt=args.receipt)
        raise ValueError('AUDITED_NUMERICS_D22_BACKEND_DEFERRED: execution adapter not implemented')
    except (ValueError,OSError,KeyError,TypeError) as exc:
        record.update(status='REFUSED',reason=str(exc))
    except Exception as exc:
        record.update(status='REFUSED',reason=f'{type(exc).__name__}: {exc}')
    path=args.attempt_log_dir/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex+'.json')
    write_once(path,record)
    print(json.dumps(dict(status='REFUSED',engine_runs=0,log=str(path),reason=record['reason'])))
    return 2


if __name__=='__main__':
    raise SystemExit(main())
