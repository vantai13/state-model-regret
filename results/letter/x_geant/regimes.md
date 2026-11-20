# X-GÉANT — lựa chọn chỉ từ train

Người phụ trách: Doan Van Tai.

Capacity 12544.525173885328 Mbit/s; 26 weekday, window 10:15–16:15.

| Regime | OD | mean OD (Mbit/s) | max-util path Stay | max-util path Switch | ratio |
|---|---|---:|---:|---:|---:|
| NEW1 | hu1.hu_se1.se | 1416.340868 | 0.900000000 | 0.610733502 | 0.678592780 |
| NEW2 | si1.si_se1.se | 966.639603 | 0.900000000 | 0.323403980 | 0.359337756 |
| NEW3 | ny1.ny_de1.de | 398.709543 | 0.900000000 | 0.170519868 | 0.189466520 |
| BOTH1 | de1.de_si1.si | 2890.912175 | 0.614852003 | 0.710310838 | 1.155254979 |
| BOTH2 | cz1.cz_si1.si | 30.755356 | 0.614852003 | 0.613185197 | 0.997289094 |
| BOTH3 | cz1.cz_at1.at | 0.026057 | 0.614852003 | 0.610735579 | 0.993305016 |

NEW1 Stay: hu1.hu → at1.at → de1.de → se1.se
NEW1 Switch: hu1.hu → at1.at → ny1.ny → uk1.uk → se1.se

NEW2 Stay: si1.si → at1.at → de1.de → se1.se
NEW2 Switch: si1.si → at1.at → ny1.ny → uk1.uk → se1.se

NEW3 Stay: ny1.ny → at1.at → de1.de
NEW3 Switch: ny1.ny → uk1.uk → fr1.fr → de1.de

BOTH1 Stay: de1.de → at1.at → si1.si
BOTH1 Switch: de1.de → at1.at → hu1.hu → hr1.hr → si1.si

BOTH2 Stay: cz1.cz → de1.de → at1.at → si1.si
BOTH2 Switch: cz1.cz → sk1.sk → hu1.hu → at1.at → si1.si

BOTH3 Stay: cz1.cz → de1.de → at1.at
BOTH3 Switch: cz1.cz → sk1.sk → hu1.hu → at1.at

Tiêu chí: {"X2": "exclude DAY1/2/3 ODs; Stay crosses global busiest link, Yen-2 Switch avoids it; descending train mean OD, then OD id", "X4": "exclude old and selected X2 ODs; Switch path max train mean utilization >= .75 * Stay path max; prefer distinct bottlenecks, then descending min(two path maxima), descending mean OD, OD id", "utilization": "total load with managed OD exactly once on the action-specific path; 26 train weekday/window average"}

Bảng từng link/action: train_utilizations.csv. Đây là offered-load trung bình train, không phải chứng nhận cả hai path thực sự có queue.
