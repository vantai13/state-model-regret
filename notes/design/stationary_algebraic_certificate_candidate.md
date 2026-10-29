# Candidate certificate — biến đổi đại số và bound cùng mô hình infinite queue

Người phụ trách: **Doan Van Tai** · 29/10/2026 · **CANDIDATE_NOT_ADOPTED**.
Đây là implementation/certificate evaluation mới,không được gọi “certificate code cũ không đổi”.
Giữ80digits,tailplan/returntimebound cũ vàacceptance1e-10; cầnfullaudit trướcadoption.

## Target và approximation được tách

Gọi d=-increment_OFF,b=increment_ON, s=keep thật trong interval R2. Chọn b root
proposals r_j,|r_j|<1,distinct. Rootproposal đượcrefine80digits như cũ; chưa phải
chứngnhận chỉ vì Newton converged. Đặt:

    F_j=s r_j^(d+b)-(2s-1)r_j^d-r_j^b+s
    v_j=(1-s r_j^d)r_j^b/(1-s)
    c*_j ∝ r_j^(b-1)/(v_j P'(r_j)), P(t)=product(t-r_j)

Normalize c* bằng đúng hàng tổngmass cũ. Define target μ*(q,0)=sum c*_j r_j^q,
μ*(q,1)=sum c*_j v_j r_j^q,q≥1;zero_ON=sum c*v vàzero_OFF=s/(1-s)zero_ON.
c* làexactfunction của cácrootdecimal đãkhai vàs thật,không phải roundedcoeffstored.
Interval arithmetic eval derivatives/normalizer; reject nếu không certify nonzero.

## Residual không cần cộng từng backlog

NullvectorVandermonde cho sum c*v*r^(q-b)=0 khi1≤q<b. Suyra **OFFresidual=0**
cho mọi q≥1 (q=b dùngzero_ON). Từ sparse polynomial:

    v_j-(1-s)r_j^d = [s(1-s r_j^d)-F_j]/(1-s).

Do đó **ONresidual(q)=-sum c*_j F_j r_j^q/(1-s)** cho mọi q≥1, kể cảq=b vàq>b.
Bound toàn bộpositive-stateL1residual bằng:

    R_pos ≤ sum |c*_j F_j| ρ_j / [(1-s)(1-ρ_j)], ρ_j=|r_j|.

Zero-stateincoming được tính bằng geometricseries:

    incoming=zero_OFF + sum c*_j r_j(1-r_j^d)/(1-r_j).

Bound R_0 bằng hai balance equations gốc dùng incoming này. Không bỏ residual
của rootproposals; nếu roots sai thìF_j làm certificate fail.

## Normalization và stored-coefficient error

Target μ* có tổngmass1 đúng theo normalization identity,không giảđịnh rounded
storedcoeffs normalized exact. Bound E=||μ_stored-Re μ*||_1 bằng zero-mass
intervaldifference cộng geometricseries các sai khác coefficientstored vàc*/c*v.
Tất cảroots trongstored vàtarget là cùng exactdecimal datum;intervalenclosure
bao gồm datum đó. Coherentfunctionc*(r,s) tồn tại trong mọi coefficientinterval;
không giảđịnh cácintervalvalues độc lập đều thỏa identity.

Với tailtargetA,truetailB vàreturntimeboundT từimplementation gốc:

    law_error ≤ (1+2T)(A+B) + T(R_0+R_pos) + E.

Target có thểsigned/complex; cáccomplexabs bound realpartL1. Tail dùngabscoefficient,
không khẳngđịnh positivity của từngspectralterm. Stored approximation vàarray
conversion vẫn phải kiểmriêng khi fullphysicalaudit; đây chỉlawcertificate.

## Kiểm độc lập và giới hạn

- ExactFraction Gaussian elimination từ hệgốc,rồienumeratebalance ởq0..d+b+4,
  kiểmON/OFF/geometricincoming/normalization identities exact trên rationalroots.
- Closedform(-2,1):tínhTVerror vàtailupper độc lập,phải nằmtrongcertificate.
- Proposal vẫn đượccertificategốc chấpnhận ởsmall/moderatecases;quantile khớp.
- Corruptroot hoặccoefficient phải bịreject. Rootproposal sparseNewton so dense
  companionroots trênsyntheticcases; count/refinement/certificate vẫnmandatory.

Đây không phải bằngchứnghypothesis,novelty,globalaccuracy hoặcpermissionPhase4.
Một profiledegree12000 phải prereg/commit trước computation,giữmọi failure.
