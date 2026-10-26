"""Thêm 4 nguồn được tác giả duyệt (26/10/2026) vào đầu catalog; không đổi 19 record cũ.

Người phụ trách: Doan Van Tai. Snapshot trước sửa: results/lessons/l2_8/approved_batch/.
Mức "author_reading" = "Chưa có xác nhận"; mức đọc thay tác giả ghi ở cột AI riêng.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT / "papers/data/catalog.json"
LOCAL = Path.home() / "papers/state-model-regret/current"

NEW = [
    dict(id="IA26", title="A Theory of Information Architecture for Networked Decisions: Freshness, Locality, and Coordination",
         authors="Scott Moeller; Bhaskar Krishnamachari", year=2026, venue="arXiv2609.06351v1", type="Preprint",
         kind="Theory / networked decisions", url="https://arxiv.org/abs/2609.06351v1", peer="Chưa xác nhận",
         area="Networking/control: freshness × scope", priority="P1",
         claims="• PC2/PC6: giá trị thông tin hiện tại theo decision-relevant predictability; môi trường ngoại sinh.",
         ai="Mục liên quan", local="IA26.pdf",
         role="Đợt duyệt 26/10: AI-T §1–2.3, §3.4; chưa L-self.",
         problem="Thông tin mới-cục bộ hay đầy đủ-trễ cho quyết định đội?",
         method="Cost bậc hai, x*=Q⁻¹b(θ_t); regret so thông tin hiện tại đầy đủ (§2.3 Eq19–21).",
         result="Định lý 3 §3.4 tr13–14: fresh-local thắng ⇔ τ/T > ½log(1/(1−η_S(0))); Eq22–23: thêm thông tin cùng độ tươi không hại.",
         limit="Môi trường không bị action điều khiển; loại trừ controlled queueing (§1 tr3).",
         diff="Không trục model, không Γ; repo là quyết định làm đổi tải có mode ẩn.", emr="P/N/N",
         next="Tác giả đọc §2.3, §3.4 nếu dùng cho PC6."),
    dict(id="DTS25", title="Adaptive Digital Twin Synchronization: A Mechanism for Where, When, and What to Measure",
         authors="Zhiheng Yang; Francisco Vogt; Adam Belloum; Christian Rothenberg; Paola Grosso; Chrysa Papagianni",
         year=2025, venue="CoNEXT'25 Student Workshop", type="Workshop (2 trang)", kind="Vision / NDT sync",
         url="https://doi.org/10.1145/3769700.3771695", peer="Workshop sinh viên", area="NDT/networking",
         priority="P2", claims="• PC2/PC6 framing: chọn telemetry theo giá trị quyết định; chưa có thí nghiệm.",
         ai="Full bài", local="DTS25.pdf", role="Đợt duyệt 26/10: AI-F 2 trang; chưa L-self.",
         problem="Đo gì, ở đâu, khi nào để đồng bộ NDT dưới ngân sách?",
         method="Neural Measurement Field λθ(e,t,f,p|z_c) học online (§2).",
         result="Chỉ ý tưởng; validation là kế hoạch (§3 tr2).", limit="Không số đo, không oracle/regret.",
         diff="Không tách state/model; không định giá có kiểm soát.", emr="N/N/P", next="Chỉ bối cảnh đoạn 1 related work."),
    dict(id="CEN26", title="CENTILE: A Telemetry Foundation Model Evaluated by the Decisions It Drives",
         authors="Zifan Zhang; Zhichao Hou; Tingxiang Ji; Yuchen Liu", year=2026, venue="arXiv2608.01725v1",
         type="Preprint", kind="Telemetry model / decision replay", url="https://arxiv.org/abs/2608.01725v1",
         peer="Chưa xác nhận", area="Networking/systems telemetry", priority="P2",
         claims="• PC5: đánh giá model bằng quyết định replay; không 2×2.", ai="Mục liên quan", local="CEN26.pdf",
         role="Đợt duyệt 26/10: AI-T §I, §III-D, §IV-A, §IV-D; chưa L-self.",
         problem="Telemetry model có cải thiện quyết định scheduling/provisioning không?",
         method="Replay backfilling (5 walltime source, true runtime làm reference) và provisioning (§IV-A, §IV-D).",
         result="CESNET vi phạm 20,5%→9,0% (§IV-D tr8); câu 'error saturates near last-value' trích từ [6] (§I).",
         limit="Comparator hindsight; không oracle D15.", diff="Không can thiệp state × model.", emr="P/N/N",
         next="Bối cảnh K-M1/K-M2."),
    dict(id="CEH23", title="Certainty Equivalence Control-Based Heuristics in Multi-Stage Convex Stochastic Optimization Problems",
         authors="Chen Yan; Alexandre Reiffers-Masson", year=2023, venue="arXiv2308.13166v1; submitted to Operations Research",
         type="Preprint", kind="Stochastic optimization / CE bounds", url="https://arxiv.org/abs/2308.13166v1",
         peer="Chưa xác nhận", area="OR / certainty equivalence", priority="P1",
         claims="• PC5/PC3: cận khoảng cách CE–tối ưu ∝√var hoặc var; cần động học affine trong kỳ vọng.",
         ai="Mục liên quan", local="CEH23.pdf", role="Đợt duyệt 26/10: AI-T §2, §5.1, §6.1–6.3, §8; chưa L-self.",
         problem="Heuristic CE (thay bất định bằng giá trị danh nghĩa) cách tối ưu bao xa?",
         method="CEC relaxation, update/projection/hybrid policy (§5); state hiện tại đầy đủ, W(t) quan sát trước quyết định (§2).",
         result="Định lý 1–2 §6.1 tr21–22: C₁=O(√var), C₂=O(var); §8: re-solving không luôn có lợi (trích R02/R04).",
         limit="Assumption 5 động học affine; reward C³ lõm; queue phản xạ vi phạm.",
         diff="Gần G_M|S1 nhưng không cho vị trí ranh giới trong plant phi tuyến.", emr="P/P/N",
         next="Tác giả đọc §2 Assumption 5, §6.1 nếu dùng cho PC5; H1-Q04."),
]


def main() -> None:
    data = json.loads(CAT.read_text(encoding="utf-8"))
    old_ids = [p["id"] for p in data["papers"]]
    assert not set(old_ids) & {n["id"] for n in NEW}
    rows = []
    for n in NEW:
        pdf = LOCAL / n["local"]
        rec = dict(n)
        rec.update(local_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                   local_source="Tác giả tải 26/10/2026 (Downloads)", access="Có (local)",
                   author_reading="Chưa có xác nhận", code="Chưa kiểm", citations="",
                   bibkey=n["id"].lower())
        rec["note_row"] = [n["id"], n["title"], n["problem"], n["method"], n["result"], n["limit"], n["diff"],
                           n["emr"], n["ai"], "Chưa kiểm", "", n["id"].lower(), n["next"], "AI (chưa kiểm)", "2026-10-26"]
        rows.append(rec)
    data["papers"] = rows + data["papers"]
    data["as_of"] = "2026-10-26"
    data["scope"] = data.get("scope", "") + " | 26/10 đợt duyệt: +IA26, DTS25, CEN26, CEH23 (AI-T/AI-F, chưa L-self)."
    CAT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": [r["id"] for r in rows], "total": len(data["papers"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
