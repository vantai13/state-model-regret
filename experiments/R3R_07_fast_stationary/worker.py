"""Isolated candidate worker; source, environment and baseline worker stay intact."""
from experiments.R3R_07_numerics import worker as base


def main():
    original=base.stationary
    def candidate(job,out):
        # base.main has already enforced rlimit before this hook is called.
        from smr import cells
        from . import law
        old_coefficients=law.barycentric_coefficients
        def coefficients(*args,**kwargs):
            base.checkpoint(out,'barycentric_coefficients_started',roots=len(args[0]))
            result=old_coefficients(*args,**kwargs)
            base.checkpoint(out,'barycentric_coefficients_completed',roots=len(args[0]))
            return result
        law.barycentric_coefficients=coefficients
        class TracedLaw(law.BarycentricLaw):
            def certify(self):
                base.checkpoint(out,'unchanged_certificate_started',roots=len(self.terms))
                result=super().certify()
                base.checkpoint(out,'unchanged_certificate_completed',roots=len(self.terms))
                return result
        cells.SpectralLaw=TracedLaw
        cells.law_for.cache_clear()
        result=original(job,out)
        result['candidate']='barycentric coefficients; unchanged reference interval certificate'
        return result
    base.stationary=candidate
    return base.main()


if __name__=='__main__':raise SystemExit(main())
