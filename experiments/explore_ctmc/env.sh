# Doan Van Tai — numeric environment for ctmc-v1 runs on every machine [AI (Claude) theo ủy quyền].
# The GCP Xeon has AVX-512, the local Ryzen does not: numpy's SIMD kernels and OpenBLAS kernels then differ in
# the last ulp (found by control V7, 03/11/2026). Disable AVX-512 dispatch in numpy and pin OpenBLAS to Haswell
# kernels so both machines run the same instruction paths. Source this before any scan or control.
export NPY_DISABLE_CPU_FEATURES="AVX512F AVX512CD AVX512VL AVX512BW AVX512DQ AVX512VNNI AVX512_SKX AVX512_CLX AVX512_CNL AVX512_ICL AVX512_SPR"
export OPENBLAS_CORETYPE=Haswell
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
