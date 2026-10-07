# Bằng chứng kiểm nguồn và cách tái chạy

Các script trong thư mục này chỉ audit nguồn đã có, không là code nghiên cứu RQ mới và không mở seed mới. JSON/manifest là metadata hoặc kết quả tính lại, không phải raw data cũ.

## Chạy độc lập

Python 3.10+ và SciPy. Từ repo notes đã clone:

```bash
python -m venv /tmp/l01-audit-env
/tmp/l01-audit-env/bin/python -m pip install scipy
/tmp/l01-audit-env/bin/python notes/verification/verify_archive.py --output-dir /tmp/l01-audit-results
```

Script mặc định clone public repo cũ vào temporary directory, đọc nội dung **từ tag**, kiểm remote hashes/ancestry, tính lại CI F7 từ JSON per-seed, đọc GO-check contrast, kiểm n02 seeds và phản ví dụ Γ. Output ghi vào --output-dir, không sửa snapshot. Có thể dùng --archive-repo với một clone nguồn có đầy đủ refs; đầu clone mới vẫn là cách tái kiểm ưu tiên.

## File và phạm vi

| File | Vai trò |
|---|---|
| verify_archive.py | Bản portable của script audit có thật ở Part 2, cùng công thức F7; thêm GO-check/N2/logic checks cho Part 3. |
| verification_results.json / verification_output.txt | Output thực sự của lần chạy clone mới, không tự viết số giả. |
| source_checks.json | 22 file được mở từ immutable tags, full SHA-256, URL tại commit; review digest riêng. |
| bundle_manifest.json | Public metadata rút từ manifest thật; không publish verbose private refs/local paths; chứa size/SHA/verify code và second-copy check. |
| raw_backup_manifest.json | Tar metadata/hash đã đo ở Part 2; không remeasure AoI hoặc xác nhận identity dataset 427 MiB. |
| final_review_reading_note.md | Tóm tắt từ full snapshot theo digest; không là bản gốc hoặc primary-paper verification. |

Raw, full bundles, full review và private feedback không được copy vào repo này. Manifest nguyên bản đầy đủ vẫn local-only; public summaries không có cùng hash với manifest nguyên bản và không giả chúng là bản nguyên vẹn. Second bundle copies ở filesystem khác cùng máy, chưa off-site. Full review chưa public và primary papers chưa đọc lại là giới hạn khoa học đã ghi trong inventory.
