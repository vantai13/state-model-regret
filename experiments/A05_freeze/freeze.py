"""Doan Van Tai — receipt after committed predictions; never starts A05-T."""
from datetime import datetime,timezone

from experiments.A05_freeze.provenance import (ROOT,PREREG,CONFIG,CHOICES,CARRY,SOURCE_LOCK,THETA,FITDIR,
    PREDICTIONS,DISCRIMINATION,FEATURES,FREEZE_LOCK,CANONICAL,sha,read,write,verify_prediction_checkpoint)


def main():
    checkpoint=verify_prediction_checkpoint()
    if (ROOT/FREEZE_LOCK).exists() or (ROOT/CANONICAL).exists():
        raise FileExistsError('freeze receipt already exists; never overwrite')
    paths=[PREREG,CONFIG,CHOICES,CARRY,SOURCE_LOCK,THETA,PREDICTIONS,DISCRIMINATION,FEATURES,
           FITDIR+'/manifest.json',FITDIR+'/fit_input.json',FITDIR+'/loso.json',FITDIR+'/fit_status.json']
    lock=dict(responsible='Doan Van Tai',status='FROZEN_A05_F',created_utc=datetime.now(timezone.utc).isoformat(),
              checkpoint=checkpoint,artifact_sha256={p:sha(ROOT/p) for p in paths},
              A05_T_started=False,irreversible_A05_T_decision_recorded=False)
    write(ROOT/FREEZE_LOCK,lock)
    (ROOT/CANONICAL).write_text(f'''# A05-F — FROZEN trước A05-T

Người phụ trách: **Doan Van Tai**. Đây là con trỏ freeze của L3.6, không phải
bản lesson plan hoặc quyết định đã chạy A05-T.

- D25(ii), thiết kế A: author decision commit `{checkpoint['author_decision_commit']}`.
- Prereg commit: `{checkpoint['prereg_commit']}`.
- Theta commit: `{checkpoint['theta_commit']}`.
- Predictions/discrimination commit: `{checkpoint['prediction_commit']}`.
- predictions_heldout.json SHA256: `{checkpoint['predictions_sha256']}`.
- discrimination.json SHA256: `{checkpoint['discrimination_sha256']}`.

[Prereg](../../experiments/A05_freeze/prereg.md) ·
[Receipt](../../experiments/A05_freeze/freeze.lock.json) ·
[Predictions](../../experiments/A05_freeze/predictions_heldout.json) ·
[Discrimination](../../experiments/A05_freeze/discrimination.json).

K5 carry nguyên văn m=1; C1 khóa sau A04. PC4 metric chính: MAE trung bình
GS/GM/Gamma, margin 0,25 điểm phần trăm Cref. Verdict chính trên8ô nội suy,
R09/R10 vàR11/R12 báo riêng. Comparison D<m không mở theo luật đã khóa.
Các enclosures/hình học/tập fit không là kiểm ngoài mẫu hoặc bằng chứng cơ chế.

Features held-out chỉ bậc0–2; không dựng D/cost/gap/outcomes. L3.7 phải ghi
quyết định không đảo ngược trước khi chạy A05-T. L8/P0-V10/Phase4 không tự đóng.
''')
    print('A05-F receipt created. Commit receipt/canonical note; A05-T remains unrun.')


if __name__=='__main__':main()
