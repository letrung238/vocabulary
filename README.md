# Dữ liệu VocabLite

Repo này là nguồn dữ liệu duy nhất cho Android, Windows, iOS và macOS. Có thể
biên tập và kiểm tra độc lập, không cần truy cập repo mã nguồn ứng dụng.

| Vị trí | Nội dung |
|---|---|
| `catalog.json` | Danh mục tải qua mạng; đường dẫn tương đối trong repo này |
| `seed_words.json` | Bộ từ khởi tạo |
| `decks/` | Các bộ từ gốc, cụm nằm trong `phrases` của từ gốc, nguồn và giấy phép |
| `learning/` | Ngữ cảnh, đồng nghĩa, dạng chia và dữ liệu nâng cấp nội dung cũ |
| `pronunciation/` | Từ điển IPA offline và giấy phép |
| `practice/` | Dữ liệu luyện tập |
| `tools/` | Nguồn biên tập đã duyệt, công cụ tạo và kiểm tra dữ liệu |

Không lưu thêm bản sao bộ từ theo nền tảng. Bộ “Cụm từ trong từ gốc” là một
góc nhìn được dựng từ các bộ gốc khi app cần nhập, không có file tổng hợp riêng.
Bảng trong `learning/` phục vụ tra cứu/nâng cấp app đã cài; nguồn biên tập và
thông tin xuất xứ trong `tools/` cần để kiểm tra và tạo lại dữ liệu.

Tạo lại và kiểm tra (Python 3.11+):

```sh
python -B tools/enrich-learning-content.py
python -B tools/check-data-layout.py
python -B tools/check-prepositions.py
python -B tools/check-word-forms.py
python -B tools/check-learning-content.py
python -B tools/check-reviewed-content.py
```

Ứng dụng đóng kèm dữ liệu từ checkout này lúc build, nên vẫn dùng được offline.
Người dùng cập nhật qua mạng chỉ nhận được thay đổi sau khi commit và push repo
này. Không đưa tiến độ học, ghi chú, bản sao lưu hoặc từ cá nhân vào repo.
