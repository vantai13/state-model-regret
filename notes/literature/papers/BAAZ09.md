# BAAZ09 — Benson et al.: đặc tính traffic datacenter (WREN 2009)

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Benson, Anand, Akella, Zhang. *Understanding Data Center Traffic Characteristics*. WREN 2009, tr. 65–72.
[DOI 10.1145/1592681.1592692](https://doi.org/10.1145/1592681.1592692); bản CCR 40(1):92–99 (2010) là
[10.1145/1672308.1672325](https://doi.org/10.1145/1672308.1672325).

**Phiên bản.** 8 trang, copyright ACM 2009 (bản WREN), tạo bằng Ghostscript. Lưu tại
`~/papers/state-model-regret/l73/BAAZ09/BAAZ09_Benson_WREN09.pdf`, sha256 `161502a46fab…`.
Đọc targeted: §3/PDF2, §4.1–4.2/PDF3–5 (render tr. 69 để đọc Fig. 6–8), §5/PDF5–6, §6.1/PDF7.

**Câu hỏi.** Câu 150 s có ở đây không? ON/OFF ở biên DC dài bao lâu?

**Quan sát (trích vị trí)**
- **Đo (§3/PDF2).**
  - SNMP poll mỗi 5 phút qua RRDTool, trong 10 ngày, nhiều DC (abstract bản CCR: 19 DC).
  - Packet trace từ SPAN port của 5 switch biên trong 15 ngày. WinDump ghi ở độ phân giải 10 ms.
  - Inter-arrival được bin theo clock 10 µs (§4.2/tr. 69).
- **Link rỗi (§4.1/PDF4).** Tập link rỗi trong mỗi khoảng 5 phút "constantly changing".
- **ON/OFF (§4.2/PDF4–5).**
  - Fig. 5: chuỗi packet gom theo bin 15 ms và 100 ms đều có dạng ON/OFF.
  - Fig. 6–8: inter-arrival, thời gian ON và thời gian OFF đều fit lognormal với sai số nhỏ nhất (so với Weibull,
    Pareto, exponential).
  - Đọc từ trục hình (tr. 69, một switch ở DC10, AI đọc): ON khoảng 20–100 ms (Fig. 8); OFF khoảng 2–10 × 10⁴ ms, tức
    20–100 s (Fig. 7).
- **Hàm ý TE (§6.1/PDF7).** Nếu traffic "not too bursty and hence, reasonably predictable", các kỹ thuật thích nghi chậm
  có thể đủ.

**Câu 150 s.** Grep toàn văn không có "150". **Không xác nhận** câu này ở nguồn thứ hai mà MicroTE trích.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- ON/OFF lognormal, không exponential, và rất bất đối xứng (ON chục ms, OFF chục giây) ở một switch. Điều này khác hai mode
  đối xứng exponential của ctmc-v1, cùng chiều với GZL22.
- Số ON/OFF đọc từ trục log của một hình; chỉ dùng như bậc độ lớn.

PC liên quan: realism / RQ3. Không đổi nhãn PC.
