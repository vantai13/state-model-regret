"""Isolated sparse-root/algebraic-certificate candidate; baseline stays untouched."""
from fractions import Fraction as F
from experiments.R3R_07_numerics import worker as base


def main():
    original=base.stationary
    def candidate(job,out):
        from smr import cells
        from smr.stationary import r2_keep
        from . import law,algebraic_certificate as AC
        from .root_proposal import stable_root_proposals
        lam,u,kappa=map(F,(job['lambda'],job['managed'],job['kappa']))
        ref=job['ref'];_,inc=cells.lattice((lam-6,lam+6),u,F(1,120*ref))
        d,b=-inc[0],inc[1];s,_=r2_keep(F(1,120*ref),kappa)
        def proposals(poly):
            if len(poly)!=d+b+1:raise ValueError('unexpected root polynomial')
            base.checkpoint(out,'sparse_newton_proposals_started',degree=d+b,expected=b)
            result=stable_root_proposals(d,b,float(s))
            base.checkpoint(out,'sparse_newton_proposals_completed',proposals=len(result))
            return result
        law.np.roots=proposals
        old_coefficients=law.barycentric_coefficients
        def coefficients(*args,**kwargs):
            base.checkpoint(out,'barycentric_coefficients_started',roots=len(args[0]))
            result=old_coefficients(*args,**kwargs)
            base.checkpoint(out,'barycentric_coefficients_completed',roots=len(args[0]))
            return result
        law.barycentric_coefficients=coefficients
        class TracedLaw(AC.AlgebraicCertificateLaw):
            def certify(self):
                base.checkpoint(out,'algebraic_certificate_started',roots=len(self.terms))
                result=AC.algebraic_certificate(self,progress=lambda phase,**values:base.checkpoint(out,phase,**values))
                base.checkpoint(out,'algebraic_certificate_completed',roots=len(self.terms))
                return result
        cells.SpectralLaw=TracedLaw;cells.law_for.cache_clear()
        result=original(job,out)
        result['candidate']='sparse proposals, original 80-digit refinement, barycentric coefficients, algebraic interval certificate'
        return result
    base.stationary=candidate
    return base.main()


if __name__=='__main__':raise SystemExit(main())
