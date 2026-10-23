# T01 — một observation/cell, bổ đề E0

Người phụ trách: **Doan Van Tai**,23/10/2026. Đây là proof/reference được tạo trong phiên triển khai và kiểm bằng code, **không** là bài kín sách hoặc understanding artifact của tác giả.

Giả sử y cố định, S0 dùng b=D, action binary, cùng true cost J và model M0, strict negative gap mới Switch. Đặt g=E_DΔ,h=E_DΔhat_M0,P=E_DΔ+,N=E_DΔ−.

1. y và b cố định khiến mọi predicted cost trung bình của S0 cố định. Do đó a00=1[h<0],a01=1[g<0] không phụ thuộc realized state trong cell. Đây là conditional experiment, không controller phản ứng với nhiều observations trong cùng cell.
2. M1 đúng law nên predicted difference của S0M1 là E_D[JSw−JSt]=g. Tie rule cho trực tiếp a01=1[g<0].
3. Viết L00=EJSt+a00g,L01=EJSt+a01g. GM=(a00−a01)g. Nếu action giống nhau thì0; nếu khác, a01 là minimizer của hai expected true costs nên kết quả abs(g). g0 cho GM0 ngay cả khi action khác nhau.
4. Khi action khác và g≠0, h ở nửa trục khiến M0 chọn action khác g (kể cả h0). Bởi vậy abs(h−g)≥abs(g)=GM. Khi action giống hoặc g0, GM0 nên bound vẫn đúng.
5. min(JSt,JSw)=JSt−Δ−, nên L11=EJSt−N. L01=EJSt+min(0,g), g=P−N. Trừ hai vế được GSgivenM1=N+min(0,P−N)=min(P,N). Nó dương iff cả Δ>0 và Δ<0 có probability dương; chỉ trộn Switch thắng với ties không đủ.

Canonical: L00=59/8,L01=57/8; g=−1/4,h=1/4,bias=1/2; GM1/4; P7/8,N9/8,GSgivenM1=7/8. Mean-cost biases không suy ra policy gain nếu cùng action. Hàm GM theo parameters là piecewise0/abs(g), có thể nhảy tại model-decision boundary; không là step function có độ cao hằng trên mọi miền.

Mixture nhiều observations cần conditional law D_y và weights của đầy đủ y-support: Lsm=Σ_y p(y)Lsm(y), đồng thời policy của S0 thay theo y. Hai mức q50/q90 không phủ population và không đủ dựng mixture. Đây là suy luận từ thiết kế, không novelty claim.

Tests: canonical Fraction,1.875 ca hai-state rational gồm ties và counterexample GM0/action khác. Không dùng outcomes của candidate grid v1.1 để kiểm bổ đề.
