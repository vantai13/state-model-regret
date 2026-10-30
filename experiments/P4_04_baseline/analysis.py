"""Pure descriptive outputs and the approved selection/reading rules.

No engine calls, CF file reads or card verdict changes. Reusable by L4.8.
"""
from fractions import Fraction as F
from statistics import median

from .common import RHOS, require


def baseline(row,rho):
    return next(b for b in row['baseline'] if F(b['rho'])==F(rho))


def objective(row,rho,target):
    return (F(baseline(row,rho)['L'+target])-F(row['losses']['11']))/F(row['Cref'])


def select_rho(rows,target):
    require(rows and target in ('00','10'),'nonempty target controller data required')
    scores={rho:sum(objective(row,rho,target) for row in rows)/len(rows) for rho in RHOS}
    best=min(RHOS,key=lambda rho:(scores[rho],F(rho)))
    return best,scores


def describe(row,rho,target):
    """One row of outputs required by the future Phase5 descriptive runner."""
    b=baseline(row,rho);c=F(row['Cref']);stay=F(row['Stay'])
    l00,l10,l11=(F(row['losses'][k]) for k in ('00','10','11'))
    gm=F(row['G_M']);gs=F(b['GS_theta']);delta=F(b['deltaL10'])
    recovery=(l00-F(b['L00']))/gm if gm>0 else None
    best=min(RHOS,key=lambda r:(objective(row,r,target),F(r)))
    return dict(id=row['id'],rho_star=rho,rho_best=best,
                R_M=None if recovery is None else float(recovery),
                R_M_exact=None if recovery is None else str(recovery),
                R_M_denominator_certified=b['R_M_denominator_certified'],
                GS_theta_pctC=float(100*gs/c),deltaL10=float(delta),deltaL10_pctC=float(100*delta/c),
                GS_theta_pctC_exact=str(100*gs/c),deltaL10_exact=str(delta),
                GS_original_pctC=float(100*F(row['G_S'])/c),
                Stay_headroom_pctC=float(100*(stay-l11)/c),
                Stay_minus_L00_pctC=float(100*(stay-l00)/c),
                L10_minus_Stay_pctC=float(100*(l10-stay)/c),
                recovery_best=None if gm<=0 else float((l00-F(baseline(row,best)['L00']))/gm),
                target_improvement_pctC=float(100*(F(row['losses'][target])-F(b['L'+target]))/c))


def reading(region,descriptions):
    require(descriptions,'no descriptive rows')
    if region=='MV+A':
        values=[F(r.get('R_M_exact',str(r['R_M']))) for r in descriptions if r['R_M'] is not None]
        certified=all(r['R_M_denominator_certified'] for r in descriptions)
        narrow=bool(values) and median(values)>=.5
        return dict(region=region,median_recovery=None if not values else float(median(values)),
                    undefined=len(descriptions)-len(values),all_denominators_certified=certified,
                    descriptive_narrow=narrow,claim_readiness='DEFINED' if certified else 'DENOMINATOR_UNRESOLVED',
                    statement='So với controller mean-field không margin; margin lấy lại phần lớn lợi ích' if narrow else
                              'Lưới margin đã thử chưa lấy lại ít nhất một nửa theo luật mô tả này')
    absolute=[abs(F(r.get('GS_theta_pctC_exact',str(r['GS_theta_pctC'])))) for r in descriptions]
    delta=[F(r.get('deltaL10_exact',str(r['deltaL10']))) for r in descriptions]
    narrow=median(absolute)<F(1,2) and median(delta)<0
    return dict(region=region,median_abs_GS_theta_pctC=float(median(absolute)),median_deltaL10=float(median(delta)),
                descriptive_narrow=narrow,controller_improved=median(delta)<0,
                statement='Tác hại với controller không margin' if narrow else
                          'Không thu hẹp vì baseline theo luật đã duyệt; báo cả hiệu ứng và chất lượng controller')
