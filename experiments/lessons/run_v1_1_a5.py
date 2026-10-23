"""Doan Van Tai — apply the declared B4 rule; never force a failed grid to pass."""
from experiments.lessons.v1_1_a_common import *


def run():
    out=ROOT/'results/lessons/v1_1_a5';out.mkdir(parents=True,exist_ok=True)
    if (out/'selection.json').exists():raise SystemExit('preserve B4 evidence')
    initial=json.loads((ROOT/'results/lessons/v1_1_a4/assessment.json').read_text())
    final=json.loads((ROOT/'results/lessons/v1_1_a4_redesign/assessment.json').read_text())
    candidate=json.loads((ROOT/'notes/design/grid_v1_1_redesign_candidate.json').read_text())
    labels=list(csv.DictReader((ROOT/'results/lessons/v1_1_a2_redesign/labels.csv').open()))
    outcomes=list(csv.DictReader((ROOT/'results/lessons/v1_1_a4_redesign/screen.csv').open()))
    assert initial['in_count']==8 and final['in_count']==11 and len(candidate['cells'])==34
    assert len(outcomes)==44 and {r['cell'] for r in outcomes}=={f'M{i:02}' for i in range(1,23)}
    assert not final['accepted'] and final['redesigns_used']==1
    cells=[]
    for c in candidate['cells']:
        c=dict(c);c['dominance']={r['refinement']:r['label'] for r in labels if r['cell']==c['id']}
        c['screen_class']=final['classes'].get(c['id'],'NOT_SCREENED')
        c['screen']=[r for r in outcomes if r['cell']==c['id']]
        if c['role']=='negative':
            assert all(v in ('SD-cell','conservation-cell') for v in c['dominance'].values())
            c['expected_six_contrasts']='exactly zero by all-support certificate; not simulated'
        cells.append(c)
    selection=dict(author='Doan Van Tai',status='REJECTED_NARROW_REQUIRED',accepted=False,
        initial_in_count=8,final_in_count=11,required_in_count=15,main_count=22,redesigns_used=1,
        calibration_cells=[],calibration_status='NOT_SELECTED_BECAUSE_GRID_REJECTED',
        negative_controls=['N01','N02','N03','N04'],cells=cells,
        deleted_cells=[],thresholds=dict(p_low=.1,p_high=.9,required_fraction='2/3',epsilon_R=.01,epsilon_E=.005,refinement_budget=.0025),
        tag_allowed=False,A01_allowed=False,source_commits=dict(initial_candidate='571d4cf',initial_screen='6b87256',
            redesign_preregistration='19d03cc',redesign_candidate='3fe81d2',redesign_screen='ae876ab'))
    write(out/'selection.json',selection);write(ROOT/'notes/design/grid_v1_1.json',selection)
    csvwrite(out/'cell_decisions.csv',[dict(cell=c['id'],role=c['role'],dominance=c['dominance']['1'],classification=c['screen_class'],kept=True) for c in cells])
    (ROOT/'notes/design/grid_v1_1.md').write_text('# Lưới v1.1 — REJECTED / NARROW REQUIRED\n\nDoan Van Tai,23/10/2026. Đây là decision record, không phải lưới được phép chạy Phase3.\n\nInitial8/22, sau đúng một redesign11/22, yêu cầu15/22. Giữ toàn bộ28 ô và6 reserve trong JSON. Không calibration được chốt, không tag contract-v1.1. B4 đã kết thúc bằng nhánh NARROW/REFORMULATE theo protocol; không thử λ lần hai. Negative controlsN01/N02 SD-cell,N03/N04 conservation-cell, kỳ vọng sáu contrasts0 theo chứng chỉ, chưa chạy contrasts.\n')
    manifest(out)
if __name__=='__main__':run()
