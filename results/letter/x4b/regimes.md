# X4b — lựa chọn chỉ từ train

Người phụ trách: Doan Van Tai.

26 weekday; 10:15–16:15; base capacity 12544.525173885328 Mbit/s.

| Regime | OD | e* | capacity e* Mbit/s | utilization trước → sau (Switch) |
|---|---|---|---:|---|
| NEWB1 | ch1.ch_de1.de | de1.de_fr1.fr:fr1.fr>de1.de | 2107.079186150 | 0.142772826 → 0.850000000 |

NEWB1 Stay: ch1.ch → at1.at → de1.de
NEWB1 Switch: ch1.ch → fr1.fr → de1.de
| NEWB2 | ch1.ch_se1.se | de1.de_se1.se:de1.de>se1.se | 9126.508697966 | 0.618399843 → 0.850000000 |

NEWB2 Stay: ch1.ch → at1.at → de1.de → se1.se
NEWB2 Switch: ch1.ch → fr1.fr → de1.de → se1.se
| NEWB3 | at1.at_de1.de | de1.de_fr1.fr:fr1.fr>de1.de | 1953.880206073 | 0.132392271 → 0.850000000 |

NEWB3 Stay: at1.at → de1.de
NEWB3 Switch: at1.at → ch1.ch → fr1.fr → de1.de

Mỗi regime chỉ thay một directed link. Offered-load utilization không chứng nhận queue hay congestion của mọi sample.
