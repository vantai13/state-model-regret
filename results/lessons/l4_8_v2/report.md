# L4.8 — declared use case/domain theo scope hiện có

Người phụ trách: **Doan Van Tai** · 31/10/2026 · AI theo ủy quyền tiếp tục;
không tác giả tự viết/tự đọc, human review hoặc Understanding PASS.

**SCOPING_COMPLETE_EMPIRICAL_DOMAIN_UNRESOLVED.** Đã chọn narrative, ghi
mathematical domain, kiểm nguồn và quy đổi metadata. **Chưa xác nhận được một
miền realistic bằng empirical evidence.** Lượt này không được cung cấp full
lesson4.8/checklist riêng; thực hiện roadmapPhase4v2 và chỉ đạo user, không
nhận đã hoàn tất một checklist chưa đọc hoặc tự đóng Gate4.

## Kết quả quyết định

Use case trình bày: **DC-inspired one-shot steering của managed aggregate giữa
hai equal-capacity egressqueues**, twin soStay/Switch trên fixedhorizon. Đây
là controlled model study trong contextDC đã duyệt; không deployment claim
vềSDN/TCP/flowlets. Giữ contextedge vàmọiartifactrealismv1, không đổi nó thànhOUT.

Domain là physicalvalidity **đã khóa ởcontractv1.3**: lambdaA/B>=6,
lambdaA+u<10,lambdaB<10,u>0,kappa/h>0,c_sw0. Currentnativeimplementation
thêm lambdaB+u<10; đó làcomputational subset. Finitepost-Switchoverload vẫn
physicalvalid theo contract, không đổi thành invalid để khớpengine. Horizon
phải đúng slotlattice, khôngceil. Không chọn samplingbox/heldout/threshold mới.

Empiricalbacklogage, holdh, offeredinput law, managedload, buffer/actuation
vẫnnull trong [domainJSON](../../../notes/realism/declared_domain_l4_8.json).
Không suy “không đủ nguồn” thành “phi thực tế” hoặc0feasible regimes. Nhãn
realismv1/216ID–210keys vàhai contexts được giữ nguyênbyte; đây không phải
một envelopev2 tự gán lạiIN/EDGE/OUT cho597points.

## Nguồn đã đọc và evidence boundary

Skill [paper-research](/home/vantai/.codex/skills/paper-research/SKILL.md);
đọcsearchprotocol/catalog26/log trước. **3exactDOIlookups,3existing sources,
3PDFpage-textcalls/15targetedpages**,0newpaper/0proposal/0PDFdownload.
BaPDFlocal khớpcatalogSHA, currentAImứcT, khôngfullread/author-self.

- **ZLK17**, §4.1–4.2/PDF3,§5.1–5.2/Table2/PDF4,§6.1/PDF5,§6.4/PDF7:
  measurement capability/traffic context, nhưng throughput/peakbuffer khác
  offeredinput/exactbacklog. Server-ToR10Gb/s khác alternativeuplinks40/100Gb/s;
  không ghép thành bằng chứngjointusecase10Gb/s. Hotduration không làT_mode.
- **BAM10**, §3.1/PDF3,§5.2/Table4/PDF6–7,§6.2–6.3/PDF9:
  traffic/window/ONOFFdefinitions vàfits khác symmetricexponentialtwo-rate
  law. SNMPwindow/hotspotthreshold không xác nhận tau/h/peakinput của plant.
- **NDT1**, §II/TableI/PDF2,§IV-B/Fig4/PDF5,§V/PDF6, acceptedarxivv2:
  hỗ trợ NDTwhat-if/routingmotivation; syntheticoptimizerstudy không calibrate
  backlog/mode/age hoặc triển khai của repo. Không gọi workflowNDT là novelty.

[Source review cóDOI/version/vị trí](../../../notes/realism/L4_8_source_review.md),
[access/reading record](literature/review.json). Xem trực tiếpZLKTable2,
BAMTable4,NDTFig4. T00chỉnote-levelreview; không nhận rereadprimaryPlanck/
Hedera/Kuźniar. Dừngbounded3nguồncũ, khôngsystematicsurvey/saturation. Không
đổiExcel/catalog26/authorreadingprogress/PC hoặc tải nguồn chưa duyệt.

## Quy đổi597tọa độ đã có — kết quả tính được

Inputchỉcasecoordinates từpreregSV497/A390 và10SUBpark; không loadcosts,
contrasts/labels mới hoặc mởCF/R09/R10. Supportsđã được chọn ởdiscovery;
bảngmin/max dưới đây không là một independentbox hoặcquyết địnhsampling mới.

**597/597** physicalvalid, currentnative-supported vàhorizonadmissible theo
schema; kết quả này **không** lànumericalreadiness hoặcempiricalrealismPASS.

| Đại lượng design | Range trên597keys |
|---|---:|
| lambdaA/mu,lambdaB/mu |.60–.85 |
| u/mu |.10–.175 |
| kappa=T_mode/tau |.05–3 |
| h/tau |1–16 |
| rhoA_pre |.70–.95 |
| rhoB_post |.70–.975 |
| BackgroundONrate/capacity |1.20–1.45 |

Reuse anchor **minh họa** capacity10Gb/s,tau10ms từcontext cũ; **tau không
được đo**. Với ratefactor r=C/10 vàtimefactor s=tau_phys/1s, backlog phải
nhânr*s, costnhânr*s². Normalizedcontrasts bất biến theo units, không qua đó
chứng minh applicability. Không giữ“1modelpacket=1physicalpacket” rồi đổi
capacity/time độc lập.

| Quy đổi minh họa, không measured range | Kết quả |
|---|---:|
| Managedaggregate |1–1.75Gb/s |
| Meanmode timeT |.5–30ms |
| Holdhorizonh |10–160ms |
| Mộtmodelbacklogunit |10,000,000bits=**1.25MBfluidwork** |

Không đổi egressmeasurement thành offeredpeak>capacity đểfit biên độ .6.
Ngay cả cùnglinkcapacity cũng chưa có jointlycompatibletau/h/input/buffer/
actuation. Các giá trị minh họa không thaynull empiricalparameters hoặc nhãn
v1. Không tạo thêm plot vì đây làbảngquyđổi đơn vị, không numericalexperiment.

## Verification

**12newtestsPASS(.04s);33combinedscope/legacyrealismtestsPASS(.53s);
942fulltestsPASS(96.98s).** Kiểm exacthomogeneity củaLindley/cost, units,
khôngceilH, primaryconstraints vàfinitepostoverload validnhưngoutsideengine.
Đối chiếu độc lập597keys/units/sourceSHA và3PDFSHA PASS. Oldrealismfreeze,
labels vàcatalog/Excelgiữnguyên; A1/A2/A3/baseline/screeningrules khớp.

Đã chạy:

```bash
.venv/bin/python -m pytest -q tests/test_p4_08_scope.py
.venv/bin/python -m pytest -q tests/test_p4_08_scope.py tests/test_realism_implied.py tests/test_realism_classify.py tests/test_realism_workflow.py
.venv/bin/python -m experiments.P4_08_scope.project_domain --out results/lessons/l4_8_v2/projection
.venv/bin/python -m pytest -q
```

Đây làmetadata/unitsanalysis,0newresearchsimulation/CF/sealedoutcomes,
khôngRNGseed/MC/CI mới. Toyrecurrence chỉ làexactunittest, khôngactualnetwork
measurement. Không chạy thêmSUB hoặc predictorclipping; D22native cònnull,
G1/Understanding/L8giữ. Provenance/codecommitad78946; hash/config trongsummary.

## Handoff cho L4.9

GiữP-clip làmtheorem/explanatoryanchor vàregressiontest. Điều kiện
π(Clip)=0⇒Gamma0 không làhypothesis mới vềmagnitudeGamma. S_clip/sigma1 là
identity trongprimary; khôngfreeze nhưpredictor. P_cliprank chưaheldout.

L4.9 có thể chuẩn bị **model-conditioned prediction** với metric/design/
baseline/exposure/heldoutcondition rõ; chưa được mang nhãn empiricalDCvalidation.
Nếu paper muốn claimdeployment/usecase realistic, cần một bộmeasurement cùng
schema cho backlogtimestamp/inputlaw/hold/action/buffer; chưa có từba nguồn
đã kiểm. Không tựsángtác source/range hoặc đổiplant để đóng điều kiện đó.
Tác giả tựviết/hiểu không được suy từAIwork. FullL4.8 nếu có hướng dẫn riêng
sau này phải được đối chiếu, không giả đã làmnhững yêu cầu chưa cung cấp.

## File đã lưu

- [Source](../../../experiments/P4_08_scope/project_domain.py),
  [tests](../../../tests/test_p4_08_scope.py),
  [declaredconfig](../../../notes/realism/declared_domain_l4_8.json).
- [CSV597rows](projection/illustrative_projection.csv),
  [JSONranges/provenance](projection/summary.json).
- [Source review](../../../notes/realism/L4_8_source_review.md),
  [literaturelog](../../../notes/literature/search_log.md),
  [3lookuprecords/access](literature/review.json).
- [Projectionlog](projection.log), [testlog](tests.log),
  [verificationJSON](verification.json)/[log](verification.log).

Không tạo paperPDF trongGit, simulationconfig/output, plots hoặcnewhypothesis.
