"""Doan Van Tai — summarize saved L3R.3 evidence; never run an engine or rescore CF."""
import csv
from datetime import datetime
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/l3r_3'


def read(path): return json.loads(path.read_text())


def suite(path):
    rows = ET.parse(path).getroot().findall('testsuite')
    return dict(tests=sum(int(r.attrib['tests']) for r in rows),
                failures=sum(int(r.attrib['failures']) for r in rows),
                errors=sum(int(r.attrib['errors']) for r in rows))


def main():
    now = datetime.now(ZoneInfo('Asia/Saigon')).isoformat()
    ids = read(ROOT / 'experiments/R3R_02_audit/prereg.json')['audit_regimes']
    engines = {rid: read(OUT / f'engine_run01/{rid}/audit.json') for rid in ids}
    prepares = {rid: read(OUT / f'mc_run01/{rid}/prepare.json') for rid in ids}
    finals = {rid: read(OUT / f'mc_run01/{rid}/final.json') for rid in ids}
    precision = read(OUT / 'mc_run01/X2065/precision_extension.json')
    resolution = read(OUT / 'mc_run01/X1008/C2_arithmetic_resolution.json')
    repro = read(OUT / 'repro_run01/comparison_final.json')
    assert repro['status'] == 'PASS' and len(repro['jobs']) == 19
    tests, original = suite(OUT / 'full_suite.xml'), suite(OUT / 'pilot_original_tests.xml')
    assert tests == dict(tests=467, failures=0, errors=0)
    assert original == dict(tests=19, failures=0, errors=0)
    mutants = read(OUT / 'mutants.json')['mutants']
    assert len(mutants) == 12 and all(r['status'] == 'KILLED' for r in mutants)
    c1 = [check for r in prepares.values() for row in r['C1'] for check in row['history'][-1]['checks']]
    c2 = [row['history'][-1]['comparison'] for r in prepares.values() for row in r['C2']]
    assert len(c1) == len(c2) == 80 and all(c['status'] == 'PASS' for c in c1)
    assert sum(c['status'] == 'PASS' for c in c2) == 77 and resolution['status'] == 'PASS'
    assert len(resolution['checks']) == 3 and all(c['comparison']['status'] == 'PASS' for c in resolution['checks'])
    c3nodes = [v for r in finals.values() for v in r['C3']['nodes'][-1]['checks'].values()]
    assert all(v['status'] == 'PASS' for v in c3nodes)
    assert precision['status'] == 'PASS'
    records = []
    for rid in ids:
        audit, mc = engines[rid], finals[rid]
        base = audit['levels'][0]
        main = next(v for v in audit['levels'] if v['ref'] == 2 and v['K'] == 40)
        checkK = next(v for v in audit['levels'] if v['ref'] == 2 and v['K'] == 20)
        keymap = {'GS': 'G_S', 'GM': 'G_M', 'GSM': 'G_SM', 'Gamma': 'Gamma', 'GS_M1': 'G_S_M1', 'GM_S1': 'G_M_S1'}
        deltaC = max(100 * abs(main[k] - other[k]) / main['Cbar'] for k in keymap.values() for other in (base, checkK))
        deltaS = max(100 * abs(main[k] - other[k]) / main['Sbar'] for k in keymap.values() for other in (base, checkK))
        sign_flips = [k for k in keymap.values() for other in (base, checkK)
                      if main[k] * other[k] < 0 and max(abs(main[k]), abs(other[k])) > .005 * main['Cbar']]
        c3stat = mc['C3']['stationary'][-1]
        se = precision['contrast_SE_max_ppC'] if rid == 'X2065' else c3stat['contrast_SE_max_ppC']
        record = dict(id=rid, Cbar=base['Cbar'], L00=base['Cbar'] + base['G_SM'], L01=base['Cbar'] + base['G_S_M1'],
                      L10=base['Cbar'] + base['G_M_S1'], L11=base['Cbar'],
                      GS_pctC=base['G_S_pctC'], GM_pctC=base['G_M_pctC'], Gamma_pctC=base['Gamma_pctC'],
                      T2b_original=audit['T2b_status'], S1_error_K160_ppC=max(audit['S1_quadrature_errors'][-1][k] for k in ('error_L10_ppC', 'error_L11_ppC')),
                      delta_max_ppC=deltaC, delta_max_ppStakes=deltaS, sign_flip_outside_equivalence=bool(sign_flips),
                      nominal_contrast_refinement='PASS' if deltaC <= .25 and not sign_flips else 'UNRESOLVED',
                      nodes_N=mc['C3']['nodes'][-1]['N'], nodes_max_z=max(v['z'] for v in mc['C3']['nodes'][-1]['checks'].values()),
                      stationary_original_status=mc['status'], stationary_final_SE_ppC=se,
                      T6_relative_error=audit['snapshot_v12']['max_relative'])
        extra = OUT / f'K320_extension/{rid}.json'
        if extra.exists():
            level = read(extra); direct = audit['direct_stationary_S1']
            record['S1_error_K320_ppC'] = max(100 * abs(level['Cbar'] - direct['L11']) / direct['L11'],
                                             100 * abs(level['Cbar'] + level['G_M_S1'] - direct['L10']) / direct['L11'])
        escalation = OUT / f'numerical_escalation/{rid}_ref2_K80.json'
        if escalation.exists():
            fine = read(escalation)
            delta = max(100 * abs(fine[k] - main[k]) / fine['Cbar'] for k in keymap.values())
            flips = any(fine[k] * main[k] < 0 and max(abs(fine[k]), abs(main[k])) > .005 * fine['Cbar'] for k in keymap.values())
            record['escalation_delta_ppC'] = delta
            record['escalation_status'] = 'PASS' if delta <= .25 and not flips else 'UNRESOLVED'
        records.append(record)
    fields = list(dict.fromkeys(k for row in records for k in row))
    with (OUT / 'summary.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(records)
    timing = []
    for ref, k in [(1, 40), (1, 80), (1, 160), (2, 40), (2, 20)]:
        values = [v['wall_s'] for r in engines.values() for v in r['levels'] if v['ref'] == ref and v['K'] == k]
        timing.append(dict(ref=ref, K=k, dt_s=1 / (120 * ref), median_s=statistics.median(values), min_s=min(values), max_s=max(values), jobs=len(values), concurrent_load=True))
    maxTV = max(v['TV_retained_prior_after_age'] for r in engines.values() for v in r['posterior_prior'].values())
    atom_coarse = sum(x['status'] == 'PASS' for r in engines.values() for x in r['atoms'])
    atom_fine = sum(x['slotted'][1]['abs_error'] <= .01 and x['slotted'][1]['abs_error'] <= x['slotted'][0]['abs_error'] for r in engines.values() for x in r['atoms'])
    summary = dict(responsible='Doan Van Tai', completed_at=now, audit_verdict='HOLD',
                   technical_evidence='PASS_WITH_LIMITATIONS', source_scope='8 seen discovery regimes; no CF/R09/R10',
                   tests=tests, original_pilot_tests=original, mutants_killed=12,
                   mutant_math_guard_rejections=sum(r.get('mechanism') == 'MATH_INVARIANT_REJECTION' for r in mutants),
                   C1_pass=80, C2_original_pass=77, C2_conservation_resolved=3,
                   C3_node_regimes_pass=8, C3_node_max_z=max(v['z'] for v in c3nodes),
                   C3_original_regimes_pass=sum(r['status'] == 'PASS' for r in finals.values()),
                   C3_precision_extension=precision['status'], C3_final_max_SE_ppC=max(r['stationary_final_SE_ppC'] for r in records),
                   posterior_prior_max_TV=maxTV, T6_regimes_pass=8, T6_max_relative=max(r['T6_relative_error'] for r in records),
                   original_T2b_pass=sum(r['T2b_status'] == 'PASS' for r in engines.values()),
                   atom_coarse_pass=atom_coarse, atom_ref2_pass=atom_fine, atom_cases=16,
                   clean_reproduction_runs=19, clean_reproduction_pairs=sum(r['pairs'] for r in repro['jobs']), clean_reproduction_distinct_coordinates=9,
                   engine_decision='KEEP_CORE_AND_PILOT_SNAPSHOT_WITH_TEST_API_LAYER',
                   engine_bug_requiring_pilot_v2='NOT_CONFIRMED_IN_AUDITED_SCOPE',
                   pilot_v2_rerun=False, numerical_policy='PROPOSAL_NOT_FROZEN',
                   read_back='OPEN', P0_V10='OPEN', L8='OPEN', phase4_execution='HOLD', G_level='G1',
                   records=records, timings=timing)
    summary['original_nominal_refinement_pass'] = sum(r['nominal_contrast_refinement'] == 'PASS' for r in records)
    summary['post_escalation_nominal_refinement_pass'] = sum(r.get('escalation_status', r['nominal_contrast_refinement']) == 'PASS' for r in records)
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    table = '\n'.join(f"| {r['id']} | {r['L00']:.6f} | {r['L01']:.6f} | {r['L10']:.6f} | {r['L11']:.6f} | {r['GS_pctC']:+.6f} | {r['GM_pctC']:.6f} |" for r in records)
    times = '\n'.join(f"| {r['ref']} | {r['K']} | {r['median_s']:.3f} | {r['min_s']:.3f}–{r['max_s']:.3f} |" for r in timing)
    text = f'''# L3R.3 — Audit engine population

Người phụ trách: **Doan Van Tai** · thực hiện 28–29/10/2026 · DL-066–068.
**Kết luận audit: HOLD.** Bộ kiểm kỹ thuật đã thực hiện, evidence **PASS có giới hạn**;
chưa đủ để tự khóa numerics v1.3: read-back tác giả còn OPEN, một số mức số khai gốc
UNRESOLVED, cost allowance đầy đủ chưa interval-certified. Không nâng G1/Phase4.

## Đã làm và quyết định engine

Đọc đủ4phần lesson; trả lời(a)–(n) kèm file:dòng tại [code map](../../../notes/verification/l3r_3/code_map.md).
Commit prereg **6499d7f** trước engine outcomes mới; T07 gốc315d203 đã có trước kết luận.
S1/S2/S4/S6 MC được làm rõ từ tài liệu R2/slot cũ trước pilot, không thay plant.
MC do phiên độc lập chỉ đọc đặc tả/T07/contract; code/provenance giữ riêng, không human review.

Chọn **KEEP lõi và snapshot pilot, thêm lớp test/API trong experiments/R3R_02_audit**.
Không gọi đây là REBUILD toàn bộ hoặc đã có production enginev1.3. Snapshot và19tests gốc
giữ nguyên byte từtag a7435e9. API thêm giúp hỏi policy tại y/x tùy ý và test explicit tables.
Trong8regimes audit chưa xác nhận bug làm thay đổi số pilot; hai lỗi phát hiện nằm ở
adapter toy và arithmetic của MC checker, đã có regression/proof trước sửa.
Vì vậy **chưa kích hoạt chạy lại216ID/pilotv2**. Nếu sau này tìm ra bug thật ở engine,
vẫn phải giữv1, viết regression/prediction rồi rerun toàn216ID, không chọn phần thuận lợi.

## Kết quả kiểm thực tế

| Phép kiểm | Kết quả |
|---|---|
| T1/T4/T5/T7 + MC unit trong full suite | **467/467 PASS**, 99.39s; gồm28test audit mới |
|19test toy gốc pilot, import alias không sửa byte | **19/19 PASS**,0.04s; chạy riêng ngoài full testpaths |
| Mutation | **12/12 bị bắt**:11 bởi assertions,1 bị mathematical guard Jensen từ chối; không đếm arbitrary runtime crash là KILLED |
| T2 xác suất,16side cases | **16/16 PASS**, maxTV={maxTV:.6g}, mỗi tolerance=removed mass+1e−12 |
| T2 cost so direct stationary, khai gốc đếnK160 | **6/8 PASS**, X1008/X1009 giữUNRESOLVED ở mức gốc |
| T3 atom so fluid,ref1 | **{atom_coarse}/16 PASS**,5case coarse ngoài.01; không gọi đó là bug slotted law |
| T3 atom ởref2 | **{atom_fine}/16** trong.01 và lệch giảm; κ dependence ở finite dt không tự là lỗi |
| T6 so actual snapshot với evaluate_sidesv1.2 | **8/8 PASS**, maxrelative={summary['T6_max_relative']:.6g}; chỉ kiểm phần khác code, không độc lập belief |
| MC C1,5state×2action×8regimes | **80/80 PASS** theo3SE/luật retry |
| MC C2,2side×5y×8regimes | **77/80 PASS ban đầu**;3alarm còn lại được giải thích bằng exact conservation và kiểm lạiPASS |
| MC C3 trên cùng discrete-node law | **8/8 PASS** sau retry đã khóa, max abs(z)={summary['C3_node_max_z']:.6f}; conditional law vẫn có numerical solve error đã công bố |
| MC C3 full stationary |8/8khớp mean theo3SE+allowance refinement; ban đầu1SE-targetUNRESOLVED, precision extension sau đóPASS |
| Clone/venv mới | **19/19 PASS**, {summary['clean_reproduction_pairs']} snapshot-pair records khớp exact numeric values |

T1 integer-count adapter đưa cùng toy rational qua actual pair_values mà không làm mất tie.
500jointlaws seed20261028 ở T07 được dùng lại, không gọi replay là500laws mới độc lập.
T4u0 và T5far-state conservation kiểm **0 chính xác**, không epsilon/clamp.
T5là kiểm theo state, không giả định cả population không bao giờ chạm0.

Mutation matrix thực chạy nằm ở[mutants.json](mutants.json). Ma trận trong lesson là
dự đoán, không phải bằng chứng mọi test phải bắt mọi mutant. Thêm analytic R2 conditional
mode test đã bắt no-age; vì thế câu “chỉ MC bắt được” không còn đúng cho bộ kiểm mới.
Đính chính nguồn lesson: report L1.5 dòng63–81 và các replay XML **có evidence** checker
chung helper bỏ sót P4 ở test any-belief; bản kiểm độc lập bắt được. Code map trỏ đúng
artifact; không nhận đã rerun các mutant lịch sử trong lượt này.
MC dùng policy hộp đen không tự chứng minh information restrictions/optimality của policy;
S0leak/M0semantics vẫn cần code map/toy, không gán coverage tưởng tượng cho MC.
D22mode-leak mutant áp vào prototype finite-toy, chưa là D22 outcome trên pilot.

## Những số pilot đã được kiểm lại

Regimes đã exposed; age1s,μ10packet/s,λ±6,R2,pre-Stay; bảng dưới **ref1,K40,dt1/120s**.
L là expected cost **packet·s**; GS/GM chiaC̄=L11, đơn vị**%C̄**. Không phải CF/held-out mới.

| ID | L00(S0/M0) | L01(S0/M1) | L10(S1/M0) | L11 oracle | GS %C̄ | GM %C̄ |
|---|---:|---:|---:|---:|---:|---:|
{table}

Ví dụX2065: sửa model giảm cost37.983758→33.503211packet·s, gain13.406930%C̄.
X2029: state-only làm cost tăng, GS=−21.570165%C̄. Đây vẫn là discovery của plant;
audit xác nhận phạm vi tính toán, không biến chúng thành hypothesis confirmation hoặc mạng thật.

## Numerics: cái gì đạt, cái gì chưa được khóa

S1cost ởκ3 co khiK tăng nhưng K40 không đủ: X1008 maxerror khoảng.942ppC,
X1009 khoảng.939ppC. K160 còn.3265/.3162ppC > .25.
K320 được khai **sau quan sát** tạiDL-067, trước run bổ sung; maxerror còn
**{next(r['S1_error_K320_ppC'] for r in records if r['id']=='X1008'):.6f}ppC** và
**{next(r['S1_error_K320_ppC'] for r in records if r['id']=='X1009'):.6f}ppC**.
Không đổi nhãn của hàng prereg gốc hoặc nóiK320đã khai từ đầu.
Đây là sai số estimator S1 qua quadrature, không bác identity estimand.

Candidate từlesson **K40,ref2(dt1/240)** đã được đo cùng checkK20/ref2 vàK40/ref1;
bảng[summary.csv](summary.csv) giữ cả maxdelta theo%C̄/theo%stakes và sign-flip.
Không tự adopt candidate thành mức toàn miền: absoluteS1/Cbar error ởκ3 yêu cầu
quadrature tốt hơn hoặc thiết kế direct-state integration được audit riêng.
Ngoài ra X2065 có coarse pairK20→K40/ref2 lệch.440885ppC, nên đã chạy **K80/ref2**
theo đúng một bậc escalation khai gốc; status/delta mới ở summary, giữ coarse pairFAIL
precision ban đầu. Không lấy 9robustness points cũ làm chứng nhận cặpK20mới.
Ref2 được hỗ trợ bởi atom nhưng chưa là certificate cho mọi contrast/regime mới.
Giữ tolerance .25ppC,sign rule ngoàiεE.5%C,thang stakes riêng; không suy tolerance
theoC đủ cho mọi hypothesis theo stakes. Primary/εR/K*/stop rule cuối thuộcL3R.5.
UNRESOLVED không tính PASS/FALSIFY; tỷ lệngưỡng10% vẫn là proposal choL3R.7.

Pilot ghi tail probability; tail cost và independent-law finite-cap bounds có trongMC
diagnostics. Chúng được tính float64, sparse residual không tự là certified invariant
error. Refinement difference là **estimate**, không phải rigorous bound. Full population
MC dùng allowance đó nên kết luận phải có giới hạn; không gọi all z≤3 cho target này.
Bin-policy integral không bằng point quadrature; strict-node comparison tránh trộn hai law.
3SE là quy tắc audit, không global family-wise confidence guarantee; công thức
1−(1−p)^m chỉ đúng khi các alarm độc lập, còn các metricCRN ở đây tương quan.

## MC sample sizes, SE và các lần có vấn đề

Dảiseed318300000–318399999 chỉverification. C1/C2/C3 trên8regimes audit dùng **ref1**;
ref2 được probe/reproduce, chưa được MC production độc lập trên toàn8regimes này.
C1/C2N65536, alarm→4N/seed mới một lần.
C3pilotN2048/target; Nproduction được khóa ởcommit4c4908f **trước final runs**,
Nban đầu32768–524288, X2029nodes retry lên2097152 theo luật có sẵn.
Mean/SD/SE và từng seed ở[mc_run01](mc_run01/); moments giữ per-episode contrasts,
mean,sd,cross_sum để kiểm lại SE. Không cần giả episode liên tiếp làIID: mỗi initial
state được rútIID từ invariant law độc lập, future streams độc lập episode vàCRN theoaction.

X2065stationary ban đầuSEmax=.103446939ppC vượt.1: [final gốc](mc_run01/X2065/final.json)
giữUNRESOLVED. Sau khi khai[precision extension](../../../experiments/R3R_02_audit/precision_extension.json),
N=1048576,seed318351301 choSEmax=**{precision['contrast_SE_max_ppC']:.9f}ppC**, đạt.1.
Đây là kiểm thêm sau outcome, không sửa N hoặc status của final gốc.

Các sai sót đã giữ dấu vết:

1. InitialT1đỏ1/25: adapter đổiFraction→LD trước sign làm mất exact tie,cost lệch.15.
   Sửa bằnginteger-count homogeneity, không sửa engine hoặc tăngtol; fixture/log/XML giữ.
2. Một MC diagnostic index vượt bảng khiq đã ở miền provablybusy; sửa guard có ý nghĩa
   zero-idle, resume phần chưa xong, giữprepare_before_resume và traceback.
3. Ba C2z tới~212 do raw cost subtraction nhiễu~1e−15 trong bài có variance thật0.
   Phiên MC độc lập thêm no-idle certificate; raw_gap/rawcost không sửa. Check mới3/3PASS,
   không thêm epsilon,z vẫn3; [receipt](mc_run01/X1008/C2_arithmetic_resolution.json).
4. Một mutant bịJensen guard từ chối; lần đầu ghiEXECUTION_ERROR rồi phân loại cụ thể
   mathematical invariant rejection, không coi mọi exception làKILLED.
5. Phiên bị tác giả ngắt: giữ incompletefull-test log/partialrepro/K320logs. /tmpclone cũ
   không còn sau resume nên dựng clone/venv mới;12job trước+7job sau đều cùngsource/deps.
6. CSVStage2cũ chưa cộtc_sw; chỉmetadata mới0 được kiểm vớispec gốc. Mọi cột đã có và
   pair-values khớp; không nới numeric tolerance hoặc rerunengine để sửa schema-checker.

## Thời gian đo trên máy này

8declaredregimes, một số job chạy đồng thời; gồm chi phí setup/cache/CPU contention.
Đây là performance measurement, **không** benchmark isolated hoặc lời hứa thời gianPhase4.

| ref | K | Median s/regime | Min–max s |
|---|---:|---:|---:|
{times}

19 lần tái lập thuộc **9 tọa độ vật lý**:9 mứcK80,9mức ref2 và baselineX2065;
không gọi đó là19regimes vật lý độc lập.

Nền tảngx86_64,Python3.14.5,NumPy2.5.3,SciPy1.18.1; longdouble cómantissa63bit,
eps1.0842e−19 theo np.finfo, không chỉ dựa vào tênfloat128. Repro dùng freshnativecache
và deps pin. Chỉ đã kiểm cùng nền tảng, không claim tái lập Mac/Windows.

## Lệnh, source và output

```bash
.venv/bin/python experiments/R3R_02_audit/run_engine_audit.py X2065 --out <new-dir>
.venv/bin/python experiments/R3R_02_audit/run_mutants.py
.venv/bin/python experiments/R3R_02_audit/run_mc.py prepare X2065 --out <new-dir>
.venv/bin/python experiments/R3R_02_audit/run_mc.py final X2065 --out <same-dir>
.venv/bin/python experiments/R3R_02_audit/run_extensions.py precision
.venv/bin/python experiments/R3R_02_audit/run_extensions.py K320 --id X1008
.venv/bin/python experiments/R3R_02_audit/run_extensions.py K320 --id X1009
.venv/bin/python experiments/R3R_02_audit/run_pilot_original_tests.py
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_3/full_suite.xml
.venv/bin/python experiments/lessons/report_l3r_3.py
.venv/bin/python experiments/lessons/audit_l3r_3.py
```

Các lần đã chạy ghi command thực với outputpath trongcontroller receipts; script từ chối
ghi đè completed output. `<new-dir>` chỉ minh họa rerun, không nhận nó là path đã thực thi.
Clone/venv setup và resume có source/receipts, original19jobs đã soát không rerun thêm.

- [Spec/phạm vi/seed](../../../experiments/R3R_02_audit/prereg.json),[Nselection](../../../experiments/R3R_02_audit/MC_N_selection.json),[extension](../../../experiments/R3R_02_audit/prereg_extension.json).
- [Pilot snapshot](../../../experiments/R3R_02_audit/pilot_population.py),[API/adapter](../../../experiments/R3R_02_audit/bridge.py),[MC độc lập](../../../experiments/R3R_02_audit/independent_mc.py),[MC provenance](../../../experiments/R3R_02_audit/independent_mc_provenance.json).
- [SummaryJSON](summary.json),[CSV](summary.csv),[engine probes](engine_run01/),[MC/SE/moments](mc_run01/),[K320](K320_extension/).
- [Full log](full_tests.log),[XML](full_suite.xml),[originaltests](pilot_original_tests.log),[mutants](mutants.json),[repro](repro_run01/comparison_final.json).
- [Completion](../../../notes/phases/L3R_3_completion.json),[integrity verification](verification.json).

Không tạoplot hoặcCFoutcome; không promote code lênsrc,khôngmergetagpilot,
không đổi contractv1.2/card/A05freeze/R09/R10. Các số đã nhìn vẫn làdiscovery.

## Còn gì trước khi đóng gate?

Tác giả tự read-back/giải thích code cònOPEN; không ghiAIsoạn là tự viết. Chưa khóa
numericsv1.3 toàn miền, chưa có interval-certified tail/cost/policy bound ở lớppopulation,
D22 outcome/indicatorN3 chưa cài. N7 đã tái lập mới8cặp, không xác nhận code lịch sử củaclaim.
L3R.4 được học/thực hiện trong phạm vi củalesson; **L3R.5 không tự khóa numerics**
từ các dấuPASS riêng. P0-V10/L8/T05author-writing/G1/Phase4HOLD giữ nguyên.
'''
    (OUT / 'report.md').write_text(text)
    completion = dict(responsible='Doan Van Tai', completed_at=now,
                      status='L3R_3_AUDIT_EXECUTED_GATE_HOLD', audit_verdict='HOLD',
                      technical_status='PASS_WITH_LIMITATIONS', Understanding='OPEN',
                      phase4_execution='HOLD', contract_v1_3='DRAFT', numerical_policy='NOT_FROZEN',
                      engine_decision=summary['engine_decision'], pilot_v2_rerun=False,
                      full_tests=467, original_tests=19, mutants_killed=12, C1=80, C2=80,
                      C3_nodes=8, clean_reproduction=19, P0_V10='OPEN', L8='OPEN', T05_author_writing='OPEN',
                      V9='WAIVED_BY_AUTHOR', G_level='G1', next_lesson='L3R.4; numerics freeze remains HOLD',
                      report='results/lessons/l3r_3/report.md', summary='results/lessons/l3r_3/summary.json')
    (ROOT / 'notes/phases/L3R_3_completion.json').write_text(json.dumps(completion, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ('audit_verdict', 'technical_evidence', 'tests', 'C3_node_max_z', 'C3_final_max_SE_ppC', 'clean_reproduction_runs')}, indent=2))


if __name__ == '__main__':
    main()
