# L6.4 — bounded prior check

Người phụ trách: **Doan Van Tai** · 03/11/2026. Đọc theo skill paper-research
và search_protocol; sáu nguồn do lesson chỉ định, không sáu đề xuất mới.
Mức đọc dưới đây là **AI-only**; không thay cột tác giả đã đọc hoặc L-self.

## Câu hỏi và phạm vi

MainRQ/PC3/PC4/PC6: generic information harm và action/stake-based VOI đã
có prior nào? Chỉ lookup sáu identities; không kiểm novelty toàn lĩnh vực.
R02/M00/CEH23 đọc lại **note hiện có**, không primary reread lượt này.
Galanis/Making Information More Valuable được yêu cầu đọc trực tiếp nên
đã tải OA và đọc targeted, không cần xin duyệt lại. Excel/catalog giữ byte.

| Nguồn chính thức, phiên bản kiểm | Mức đọc lượt này | Nội dung được kiểm và giới hạn |
|---|---|---|
| Spyros Galanis, *The value of information under unawareness*, JET157:384–396,2015; [DOI10.1016/j.jet.2015.01.015](https://doi.org/10.1016/j.jet.2015.01.015), [accepted manuscript](https://openaccess.city.ac.uk/id/eprint/21336/) | AI-T: PDF4–9,§2 và§3.1–3.6; abstract/intro preview; không appendix proof | §2/PDF4–5 có single-agent information harm; §3.5 Assumption1/PDF8 yêu cầu hiểu đúng deterministic payoffs, còn beliefs sai do unawareness. Theorem1/PDF9 cho sufficient conditions của information value. Đây không phải mean-rollout response misspecification của repo; chỉ dùng để chặn claim generic harm là mới. Journal identity kiểm Crossref; bản đọc là accepted, không VoR. |
| Mark Whitmeyer, *Making Information More Valuable*, [arXiv2210.04418v6](https://arxiv.org/abs/2210.04418v6), revised16/04/2026; PDF đề17/04/2026 | AI-T: PDF6–9,14–16; §2 qua HTML, Eq1/Def2.1–2.2 và§3.2; PDF6 chỉ caption, không đọc hình | Eq1/PDF7 tối ưu expected utility; §3.2/PDF14–16 phân biệt responsiveness/extensive margin và payoff distinction/intensive margin. Là prior cho idea giá trị thông tin qua action và payoff, không xác nhận cùng covariance decomposition hoặc misspecified controller. Thm3.1 đọc statement/Lemma3.2 proof, chưa toàn proof/appendix. Bản dùng là preprint; publication/VoR chưa xác nhận từ lượt lookup này. |
| Michel de Lara, Olivier Gossner, *Payoffs-Beliefs Duality and the Value of Information*, [arXiv1908.01633v2](https://arxiv.org/abs/1908.01633v2),20/11/2019 | AI-A, official abstract | Abstract: convex analysis liên kết beliefs, payoffs và optimal actions. Không nhận đã kiểm theorem, assumptions hay covariance formula từ abstract; không đọc PDF. Journal/VoR chưa xác nhận. |
| Song Gao, *Value of Information for Optimal Adaptive Routing in Stochastic Time-Dependent Traffic Networks: Algorithms and Computational Tools*, [ROSA P dot34297](https://rosap.ntl.bts.gov/view/dot/34297),25/10/2010, technical report | AI-A, repository abstract/metadata | Abstract nói information không lỗi không làm tệ optimal adaptive routing trong flow-independent networks. Đây là **road traffic/traveler routing**, không computer-network routing. Giữ làm contrast khái niệm có nhãn ngoài ngành, không nearest networking prior hoặc nguồn theorem chuyển sang load-changing controller. Không tải PDF. |
| Simon Scherrer, Adrian Perrig, Stefan Schmid, *The Value of Information in Selfish Routing*, [arXiv2005.05191v1](https://arxiv.org/abs/2005.05191v1),11/05/2020 | AI-A, official abstract | Abstract mô tả selfish agents/path-aware Internet và PoA phụ thuộc topology/perspective/information; thông tin ít hơn có thể giảm PoA. Multi-agent equilibrium khác one-shot controller regret. arXiv comments ghi SIROCCO2020; chưa đối chiếu VoR. Không tải PDF. |
| Ran Eilat, Kfir Eliaz, *Rational Misspecification: Framework and Applications*, [CEPR DP20906](https://cepr.org/publications/dp20906),11/12/2025 | AI-A, publisher abstract | Prior-free constrained maximal regret đánh giá willingness to acquire a more accurate model theo abstract. Không đồng nhất với expected regret D18 hoặc khẳng định đã có factorial S×M của repo. Discussion paper, chưa xác nhận peer-reviewed publication; không tải PDF. |

## Kết quả đối với claim

Generic harm, optimal VOI và ý tưởng action/payoff channels không được nhận
là contribution mới. Galanis cũng cho thấy câu “single agent nên harm mới”
không đứng. R02/M00 đã có approximate-policy/stale-load mechanisms trong
thư viện; CEH23 có conditional bounds dưới assumptions khác reflected queues.
Trong lượt này chưa kiểm được một nguồn có cùng estimand/mechanism/regime
với toàn S×M design. Điều đó **không** chứng minh absence, novelty hoặc
prior clearance; không đổi PC/G1. Covariance identity của T10 là elementary
algebra, không nhận là theorem mới hay đồng nhất với hai VOI sources.

## PDF và reproducibility

Hai download qua paper-pilot/inspect_open_access_pdf từ City/arXiv, copy
nguyên byte sang thư viện dự án ngoài Git:

- `/home/vantai/papers/state-model-regret/current/Galanis2015_Unawareness_accepted.pdf`,
 13 PDF pages, SHA256 `463409bcd34b9490eba33e878adfa8ab5d844224ae85a2fdf47c7510b8dcfece`.
- `/home/vantai/papers/state-model-regret/current/Whitmeyer2026_MakingInformationMoreValuable_arxivv6.pdf`,
 48 PDF pages, SHA256 `60d27e7410fad84705b61b606ed0af869b648735cbe795a1632666e2edaca375`.

Paper-pilot get_pdf_page_text:3 calls,14 page views/13 unique pages (Galanis
PDF9 đọc lại do output trước bị cắt); không render/diễn giải figures. Không
ghi full-read hai bài. Không lỗi extraction ở các đoạn text được dùng;
font/math extraction cần đối chiếu khi định dùng proof chi tiết.

City URL ngắn timeout, canonical eprint/PDF được; EconPapers inaccessible,
CEPR official fallback được; dblp corr-page quá4MB, chưa VoR/selfish routing.
Local pypdf không có; dùng pdftotext có sẵn để định vị trang, không cài dependency.
Tra title xuất bản của Whitmeyer/de Lara chỉ trả arXiv và nhiễu, không suy
“chưa xuất bản”. [Query/count log](search_log.md) ghi đủ paths và limitations.
Dừng ở bounded scope sáu nguồn; không saturation/field coverage/new proposal.
