# Lưu trữ resource_v2

Raw PartA retry, native rows, comparison, logs và summary được giữ trong Git.
`native_cache/` vẫn tồn tại ở filesystem local; chứa stationary/profile checkpoints
được tạo từ source frozen, không phải kết quả so sánh cuối. Thư mục này không đưa
vào Git để tránh thêm khoảng30MiB cache có thể tái tạo. Không xóa cache.

SHA256 của các cache files không rỗng nằm ở `../cache_manifest.json`. Code gốc
còn kiểm source fingerprint và checksum khi reuse cache. Reproduce từ cache rỗng
được bằng source/cases đã khóa; thời gian cold/warm có thể khác.
