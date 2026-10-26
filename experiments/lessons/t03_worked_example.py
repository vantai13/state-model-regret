"""Ví dụ tính tay cho hai identity T03 (G_{S|M1}=EVPPI, G_{M|S1}=E[VSS]) — chỉ để hỗ trợ học.

Người phụ trách: Doan Van Tai. Queue B một bước: Stay tốn K cố định (ở A); Switch đẩy thêm u
gói sang B, cost = max(0, qB + w + u − c). State ẩn qB ∈ {0, b}, posterior 1/2–1/2 sau y; tương
lai w ∈ {0, w2} xác suất 1/2. M1 = kỳ vọng đúng theo w; M0 = rollout với w trung bình (D10/G5).
Tie → Stay (D16). Tính chính xác bằng Fraction; không phải output lưới.
"""
from fractions import Fraction as F
import itertools, json, sys
from pathlib import Path

H = F(1, 2)


def run(K, b, w2, u, c, p=H, r=H):
    xs, ws = [0, b], [0, w2]
    px = {0: p, b: 1 - p}
    pw = {0: 1 - r, w2: r}
    wbar = w2 * r
    sw = lambda q, w: max(F(0), F(q + w + u - c))
    J = {(a, q): (F(K) if a == "Stay" else sum(pw[w] * sw(q, w) for w in ws)) for a in ("Stay", "Switch") for q in xs}
    J0 = {(a, q): (F(K) if a == "Stay" else sw(q, wbar)) for a in ("Stay", "Switch") for q in xs}
    ties = []
    def pick(f):
        ties.append(f("Stay") == f("Switch"))
        return "Stay" if f("Stay") <= f("Switch") else "Switch"
    a11 = {q: pick(lambda a: J[a, q]) for q in xs}
    a10 = {q: pick(lambda a: J0[a, q]) for q in xs}
    a01 = pick(lambda a: sum(px[q] * J[a, q] for q in xs))
    a00 = pick(lambda a: sum(px[q] * J0[a, q] for q in xs))
    L11 = sum(px[q] * J[a11[q], q] for q in xs)
    L10 = sum(px[q] * J[a10[q], q] for q in xs)
    L01 = sum(px[q] * J[a01, q] for q in xs)
    L00 = sum(px[q] * J[a00, q] for q in xs)
    evppi = min(sum(px[q] * J[a, q] for q in xs) for a in ("Stay", "Switch")) - sum(px[q] * min(J[a, q] for a in ("Stay", "Switch")) for q in xs)
    vss = {q: J[a10[q], q] - min(J[a, q] for a in ("Stay", "Switch")) for q in xs}
    return dict(any_tie=any(ties), J=J, J0=J0, a11=a11, a10=a10, a01=a01, a00=a00, L00=L00, L01=L01, L10=L10, L11=L11,
                evppi=evppi, Evss=sum(px[q] * v for q, v in vss.items()), vss=vss)


def main():
    best = None
    probs = (F(1, 4), F(1, 3), H, F(2, 3), F(3, 4))
    n = 0
    for K, b, w2, u, c, p, rr in itertools.product(range(1, 6), range(1, 7), range(2, 9, 2), (1, 2), range(2, 7), probs, probs):
        r = run(K, b, w2, u, c, p, rr)
        n += 1
        assert r["L01"] - r["L11"] == r["evppi"] >= 0 and r["L10"] - r["L11"] == r["Evss"] >= 0
        if r["evppi"] > 0 and r["Evss"] > 0 and not r["any_tie"]:
            key = (K + b + w2 + u + c + (p.denominator + rr.denominator), K, b, w2, u, c, p, rr)
            if best is None or key < best[0]:
                best = (key, (K, b, w2, u, c, p, rr), r)
    _, params, r = best
    K, b, w2, u, c, p, rr = params
    s = lambda v: str(v)
    out = {"params": dict(K=K, b=b, w2=w2, u=u, c=c, P_qB0=str(p), P_w2=str(rr)),
           "J_true": {f"{a}|qB={q}": s(v) for (a, q), v in r["J"].items()},
           "J_meanrollout_M0": {f"{a}|qB={q}": s(v) for (a, q), v in r["J0"].items()},
           "actions": {"a11": r["a11"], "a10": r["a10"], "a01": r["a01"], "a00": r["a00"]},
           "L": {k: s(r[k]) for k in ("L00", "L01", "L10", "L11")},
           "GS_given_M1": s(r["L01"] - r["L11"]), "EVPPI": s(r["evppi"]),
           "GM_given_S1": s(r["L10"] - r["L11"]), "E_VSS": s(r["Evss"]), "VSS": {str(q): s(v) for q, v in r["vss"].items()},
           "GS": s(r["L00"] - r["L10"]), "GM": s(r["L00"] - r["L01"]),
           "Gamma": s(r["L10"] + r["L01"] - r["L00"] - r["L11"]), "exact_ties": r["any_tie"],
           "identity_checks_cases": n}
    out_path = Path(__file__).resolve().parents[2] / "results/lessons/l2_9/t03_example/example.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
