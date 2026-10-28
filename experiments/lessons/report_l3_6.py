"""Doan Van Tai — read-only A05-F replay/report after the frozen checkpoint.

No fitting, grid/D/physical kernel, true held-out files or model changes here.
"""
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from experiments.A05_freeze.provenance import (ROOT,CONFIG,FITDIR,THETA,PREDICTIONS,DISCRIMINATION,FEATURES,
    read,write,sha,verify_frozen)
from experiments.A05_freeze.features import CANDIDATES,tensor,values
from experiments.A05_freeze.model import standardize,predict_model
from experiments.A05_freeze.ledger import contrasts,CONTRASTS
from experiments.A05_freeze.predict import discrimination

OUT=ROOT/'results/lessons/l3_6'


def csv_write(path,rows):
    with Path(path).open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def main():
    receipt=verify_frozen()
    cfg=read(ROOT/CONFIG);theta=read(ROOT/THETA);cv=read(ROOT/FITDIR/'loso.json')
    fit_input=read(ROOT/FITDIR/'fit_input.json')
    features=read(ROOT/FEATURES);pred=read(ROOT/PREDICTIONS)['predictions'];disc=read(ROOT/DISCRIMINATION)
    records=fit_input['design_main'];y=np.asarray(fit_input['summaries'])
    assert sha(ROOT/cfg['fit_outcome_inputs'])==fit_input['A04_input_sha256']
    rows=[];folds_checked=0;starts=0;failed_starts=0
    for model,candidates in cv.items():
        assert len(candidates)==cfg['candidates_per_model']
        for candidate in candidates:
            X=tensor(records,model,candidate['candidate'])
            assert len(candidate['folds'])==20
            for fold in candidate['folds']:
                test=np.asarray([r['slice']==fold['slice'] for r in records]);train=~test
                assert fold['test_ids']==[r['id'] for r,t in zip(records,test) if t]
                assert int(sum(train))==fold['train_cells']
                _,scale=standardize(X[train])
                solution=fold['optimizer_starts'][fold['chosen_start']]
                assert solution['success']
                p=predict_model(X[test],dict(beta=solution['beta'],scaling=scale),cfg)
                assert float(np.mean((p-y[test])**2))==fold['summary_MSE']
                folds_checked+=1;starts+=len(fold['optimizer_starts'])
                failed_starts+=sum(not x['success'] for x in fold['optimizer_starts'])
            assert float(np.mean([f['summary_MSE'] for f in candidate['folds']]))==candidate['mean_slice_MSE']
            rows.append(dict(model=model,candidate=candidate['candidate'],
                 selected=candidate['candidate']==theta['models'][model]['candidate'],
                 k=12,candidates_tried=2,LOSO_slices=20,LOSO_summary_MSE=candidate['mean_slice_MSE'],
                 LOSO_summary_RMSE_percentage_points=100*np.sqrt(candidate['mean_slice_MSE'])))
        selected=theta['models'][model]
        assert selected['k']==12 and np.asarray(selected['beta']).shape==(4,3)
        assert len(selected['starts'])==2
        starts+=2;failed_starts+=sum(not x['success'] for x in selected['starts'])
        all_predictions=predict_model(tensor(records,model,selected['candidate']),selected,cfg)
        assert float(np.mean((all_predictions-y)**2))==selected['training_summary_MSE']
    assert folds_checked==80 and starts==164
    assert [r['id'] for r in features['design_whitelist']]==[f'R{i:02}' for i in range(1,13)]
    for r in features['design_whitelist']:
        assert values(r)==features['feature_values'][r['id']]
    for model in ('H0','H1'):
        selected=theta['models'][model]
        summaries=predict_model(tensor(features['design_whitelist'],model,selected['candidate']),selected,cfg)
        gains=contrasts(summaries)
        for r,s,g in zip(features['design_whitelist'],summaries,gains):
            assert [str(float(v)) for v in s]==pred[r['id']][model]['summaries_normalized']
            assert {k:str(float(v)) for k,v in zip(CONTRASTS,g)}==pred[r['id']][model]['contrasts']
    assert discrimination(pred,cfg)==disc
    assert disc['outcome_open_ids']==['R01','R02','R03','R04','R05','R06','R07','R08','R11','R12']
    for record in ('features_heldout.json','predictions_heldout.json'):
        assert not read(ROOT/'experiments/A05_freeze'/record).get('heldout_D_computed',False)
    for audit_name in ('results/lessons/l3_5/artifact_audit.json','results/lessons/l3_6/artifact_audit.json'):
        audit=read(ROOT/audit_name)
        assert all(sha(ROOT/p)==h for p,h in audit['sha256'].items())
    # No new raw R outcomes or posterior files were created by any A05-F module.
    assert not (ROOT/'results/A05_T').exists()
    csv_write(OUT/'model_selection.csv',rows)
    drows=[dict(group=g,n_cells=r['n_cells'],D_percentage_points_Cref=r['D_percentage_points_Cref'],
                margin_percentage_points=.25,decision=r['decision'],ids='|'.join(r['ids'])) for g,r in disc['groups'].items()]
    csv_write(OUT/'discrimination_groups.csv',drows)
    fig,axes=plt.subplots(1,2,figsize=(13,4.6))
    h0,h1=(theta['models'][k] for k in ('H0','H1'))
    axes[0].bar(['H0: coordinates','H1: dynamics'],[100*np.sqrt(h0['LOSO_summary_MSE']),100*np.sqrt(h1['LOSO_summary_MSE'])],
                color=['#4477aa','#228833'])
    axes[0].set(ylabel='LOSO summary RMSE (percentage points Cref)',title='Internal model selection, 20 slices')
    axes[0].text(.03,.97,'4 normalized summaries; not the held-out PC4 metric',transform=axes[0].transAxes,
                 fontsize=8,va='top')
    colors=['#228833' if r['decision']=='OPEN_COMPARISON' else '#999999' for r in drows]
    axes[1].bar([r['group'].replace('_','\n') for r in drows],[r['D_percentage_points_Cref'] for r in drows],color=colors)
    axes[1].axhline(.25,ls='--',color='#cc6677',label='frozen margin = 0.25 pp')
    axes[1].set(ylabel='D (percentage points Cref)',title='Prediction separation before true outcomes')
    axes[1].legend(fontsize=8)
    fig.suptitle('A05-F: no held-out truth or posterior D used')
    fig.tight_layout()
    for suffix in ('.png','.pdf'):fig.savefig(OUT/('freeze_diagnostics'+suffix),dpi=180,bbox_inches='tight')
    plt.close(fig)
    r=dict(status='FROZEN_A05_F_PASS',responsible='Doan Van Tai',checked_utc=datetime.now(timezone.utc).isoformat(),
           **receipt,full_tests_passed=369,targeted_A05_tests_passed=21,full_suite_wall_s=60.31,
           fit_status=read(ROOT/FITDIR/'fit_status.json'),LOSO_folds_replayed=folds_checked,
           solver_starts=starts,unsuccessful_starts=failed_starts,registered_sources_verified=len(receipt['source_sha256']),
           target_predictions_replayed=24,discrimination_replayed=True,registered_A05_source_changed_after_prediction=False,
           A04_artifact_hashes_verified=147,preparation_artifact_hashes_verified=21,
           canonical_frozen=True,heldout_feature_maximum_tier=2,heldout_D_computed=False,
           heldout_cost_gap_or_contrast_computed=False,A05_T_run=False,
           registered_test_cells=12,planned_outcome_open_ids=disc['outcome_open_ids'],
           do_not_open_ids=['R09','R10'],primary_metric=cfg['primary_metric'],margin=cfg['margin'],
           PC4_test_verdict='NOT_RUN',K5_test_verdict='NOT_RUN',C1_test_verdict='NOT_RUN',
           human_reader_completed=False,phase4_status='HOLD until P0-V10')
    write(OUT/'freeze_verification.json',r)
    lines=['# L3.6 / A05-F — đã đóng băng trước held-out outcomes','',
        'Người phụ trách: **Doan Van Tai** · 28/10/2026. **Hoàn tất kỹ thuật L3.6**.',
        'H0/H1, θ, luật chấm, K5/C1 và dự báo đã khóa. **A05-T chưa chạy**; chưa có',
        'kết luận SUPPORT/WEAKEN/FALSIFY hoặc điểm K5/C1 trên held-out.','',
        '## 1. Đã làm và thứ tự commit','',
        f'- Author chọn D25(ii)/thiết kế A: `{receipt["author_decision_commit"]}`.',
        f'- Prereg, code, budget và luật chấm: `{receipt["prereg_commit"]}`.',
        f'- Fit A04/LOSO và θ: `{receipt["theta_commit"]}`.',
        f'- Features/predictions/discrimination: `{receipt["prediction_commit"]}`.',
        f'- Freeze receipt/canonical note: `{receipt["freeze_commit"]}`.','',
        'Đã thêm addendum headroom vào note A04/boundary theo kiểu append-only.',
        'P5-K đứng đã bị headroom baseline chặn; không nhận rằng nó chứng minh M0',
        'mô tả tốt động học. P3 trượt cũng nằm dưới trần headroom tại các ô của nó.',
        'Kỳ vọng gap M0 bằng0 không tự chứng minh từng state gap0 hoặc không có idle.','',
        '## 2. Kết quả chạy và baseline','',
        '**369 tests PASS**, gồm21 tests A05; suite60,31s. 80 fold LOSO được replay',
        'đúng từ θ từng fold và scaling tính trên train;2 fit toàn tập sau chọn.',
        f'Tổng164 solver starts, {failed_starts} start không thành công; fit hoàn tất trong',
        f'**{r["fit_status"]["wall_s"]:.6f} giây**. Không dùng held-out trong fit.','',
        '| Model | Candidate được chọn | k | LOSO summary MSE | LOSO RMSE (điểm %Cref) |',
        '|---|---|---:|---:|---:|']
    for name,m in theta['models'].items():
        lines.append(f'|{name}|{m["candidate"]}|12|{m["LOSO_summary_MSE"]:.12f}|{100*np.sqrt(m["LOSO_summary_MSE"]):.6f}|')
    reduction=100*(1-h1['LOSO_summary_MSE']/h0['LOSO_summary_MSE'])
    lines += ['',f'H1 có LOSO summary MSE thấp hơn H0 **{reduction:.4f}%**. Đây là so sánh nội bộ',
        'trên discovery để chọn mô hình, không xác nhận RQ2. Loss này dùng4 summaries;',
        'metric PC4 thật đã khóa là MAE đều GS/GM/Gamma, sẽ chấm bằng true intervals',
        'ở A05-T. Không đổi metric để chọn chỉ số thuận lợi.','',
        'Cùng Gaussian,12 hệ số,2 candidates/bên,2 starts,optimizer/ridge/scaling/tie',
        'và feasibility. Rho cố định0 cho cả hai; null vẫn sinh Γ>0/GS<0 trên toy.',
        'Scaling mỗi fold chỉ dùng training partition;20 lát, không LOOCV từng ô.',
        'H0 có bias phụ thuộc tọa độ; H1 dùng variance telegraph/fluid-boundary/drain',
        'proxies. Kappa là memory time, rate correlation=2/kappa. Không có queue D',
        'hoặc cost/gap thật trong feature module.','',
        '## 3. Khả năng phân biệt trước outcomes','',
        'Margin m=0,25 điểm phần trăm Cref. D=mean|predictionH0−predictionH1| trên',
        'metric đã khóa; **D không dùng y thật**, khác với d=MAE0−MAE1 sau test.','',
        '| Nhóm | n | D (điểm %Cref) | Kế hoạch comparison |',
        '|---|---:|---:|---|']
    for row in drows:
        lines.append(f'|{row["group"]}|{row["n_cells"]}|{row["D_percentage_points_Cref"]:.8f}|{row["decision"]}|')
    lines += ['',
        '**R09/R10 giữ chưa mở**: D=0,212297<0,25, không outcome nào có thể làm',
        'chênh lệch MAE đạt margin trong comparison này. Không hạ m, đổi candidate',
        'hoặc gộp nhóm sau khi thấy dự báo. Universe vẫn đăng ký đủ12 ô; theo luật',
        'union đã viết trước, A05-T chỉ cần **10 ô R01–R08,R11,R12**. K5/C1 nằm trong',
        '8 ô primary. Nhóm ngoại suy báo riêng, không dùng để cứu verdict primary.',
        'D≥m là điều kiện cần, không guarantee power hoặc causal identification.','',
        '## 4. Ba nhánh đã khóa','',
        '- **PC4:** H0/H1, MAE đều3 contrasts; SUPPORT nếu lower(d)≥m; FALSIFY',
        '  nếu upper(d)≤0; WEAKEN nếu khoảng nằm trọn(0,m); còn lại INCONCLUSIVE.',
        '  Enclosure paired dùng endpoint của |p0−y|−|p1−y|, không mất correlation.',
        '- **K5:** copy nguyên văn card, m_rule_count=1, test R03/R04; Q-witness',
        '  chỉM01–M04. Giữ luật3 trạng thái của A03 và nguồn “khóa trước A04”.',
        '- **C1:** khóa sau A04, GM/Cref≤0,5% tại mọiR05–R08; không claim GM=0',
        '  chính xác. Base rate cùng sự kiện36/38; heuristic4ô0,80551868. Con số',
        '  0,64088673=(34/38)^4 chỉ cho nominalzero; cả hai không là xác suất thật.',
        '- Với ô equivalence đứng và upper(R00/Cref)<0,5%, báo headroom-limited.',
        '  Chưa biết nhãn ấy của R vì chưa tính headroom thật. Không gộp3 nhánh',
        '  thành một “tỉ lệ thành công”.','',
        'Truth quality giữ cặp1/120→1/240 theo A03, bổ sung radius≤m/10 cho PC4.',
        'Primary cho tối đa2/8 ô unavailable, báo n/N;secondary2ô cần đủ2. D phải',
        'còn≥m trên eligible subset. K5/C1 không bỏ ô HOLD khỏi ALL. Chi tiết đầy đủ',
        'trong prereg; không thay các gates đó sau khi thấy true outcomes.','',
        '## 5. Hash và kiểm chứng','',
        f'- predictions_heldout.json SHA256: `{receipt["predictions_sha256"]}`.',
        f'- discrimination.json SHA256: `{receipt["discrimination_sha256"]}`.',
        '-17 registered source hashes,147 A04 hashes và21 preparation hashes khớp.',
        '- Replay24 model-cell predictions và3 nhómD khớp chính xác với files.',
        '- Scorer verify frozen hashes trước đọc inputtruth; tests có dirty/committed',
        '  tamper cases và kiểm không đọc input khi hash guard thất bại.',
        '- Gaussian đã kiểm quadrature và2×2triệu toy samples; 100.000toyD có',
        '  roundoff dương1288trường hợp,max6,66e−16,0vượt allowance; giữ raw số đo.','',
        '## 6. Exposure và giới hạn','',
        'λA là input cho cả hai theo lựa chọn trực tiếp DL-057. Cùng quyền input',
        'không tự loại endogeneity do anchoring; chỉ claim paired predictive value',
        'trong thiết kế này. Không claim absolute forecast accuracy hay cơ chế queue.',
        'Features của12R đã exposed, bậc0–2, cóλA và stale observations. Không p_sw',
        'thật, không posterior D, cost/gap/Cref/contrast/headroom thật của R. Không',
        'fit/test bằng outcomes held-out; không gọi metadata là chưa từng chạm.',
        'Các giả định Gaussian/rho0/fluid proxies,20lát và ngoại suyh12 vẫn là',
        'limitations. T-H1: định giá cửa sổ[t0,t0+h], không long-run loss.',
        'Không tra paper mới, không đổi thư viện/author reading/human gates.','',
        '## 7. Lệnh đã chạy và vị trí file','',
        '```bash',
        '.venv/bin/python -m pytest tests/test_a05_math.py tests/test_a05_freeze.py -q',
        '.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_6/preflight/full_freeze_suite.xml',
        '.venv/bin/python -m experiments.A05_freeze.fit',
        '# commit theta6aa696a trước:',
        '.venv/bin/python -m experiments.A05_freeze.predict',
        '# commit prediction3c75aec trước:',
        '.venv/bin/python -m experiments.A05_freeze.freeze',
        '.venv/bin/python -m experiments.lessons.report_l3_6',
        '```','',
        'Source/config/prereg/locks/rules/predictions: `experiments/A05_freeze/`.',
        'Theta/CV/fit inputs/manifest/status: `results/A05_F/20261028_01/`.',
        'Logs: `results/lessons/l3_6/fit.log`,predictions.log,freeze.log,final_freeze_audit.log.',
        'Numbers: model_selection.csv,discrimination_groups.csv,freeze_verification.json.',
        'Figure: freeze_diagnostics.png/.pdf. Preflight: full_freeze_suite.log/.xml.',
        'Canonical note: `notes/lessons/A05_F_preregistration.md`; DL-057/DL-058.',
        'report.md và verification.json là snapshot **chuẩn bị cũ f5699aa**, giữ để',
        'không làm hỏng historical hashes; bản tổng kết hiện tại là freeze_report.md.','',
        '## 8. Kết luận và bước tiếp','',
        '**A05-F/L3.6 đã hoàn tất kỹ thuật.** Bước tiếp L3.7/A05-T sẽ thực hiện đúng',
        'frozen protocol sau quyết định không đảo ngược được ghi trước run. Không',
        'còn thay H0/H1/θ/feature/metric/margin/split theo outcome. L8/P0-V10 và',
        'T05 author-writing/Understanding chưa tự đóng; Phase4 vẫn HOLD.',
        'Chưa có bảng true cost baseline/repair trên R để báo; đó là việc của A05-T.']
    (OUT/'freeze_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(r,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
