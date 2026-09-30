# Nguồn và giấy phép của `b2-1000.json`

Deck B2 gồm 1.000 mục mới, được biên tập và đối chiếu để không trùng headword với
bộ chính, 17 bộ IELTS hoặc bộ IT chuyên sâu. Nội dung đã được chỉnh sửa: chọn
nghĩa chính, lọc nghĩa phụ trùng/không chắc chắn, sửa ví dụ và dịch câu ví dụ.
91 mục chưa xác nhận được nghĩa phụ tách biệt được ghi trong
`tools/sense-exceptions.txt`; không thêm từ đồng nghĩa chỉ để đủ số lượng.

Nguồn dữ liệu từ điển:

- [Từ điển Anh–Việt thichhoc.com (thichhoc-dict)](https://github.com/thichhoc-org/thichhoc-dict),
  dữ liệu theo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  Nguồn gốc của dữ liệu này gồm WordNet 3.1 (Princeton), CMUdict (CMU) và
  Wiktionary. **Dữ liệu đã được chỉnh sửa.**
- [Skypedia English–Vietnamese Dictionary](https://github.com/skypediacode/english-vietnamese-dictionary),
  dẫn xuất từ từ điển MinhQND, theo
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  Dùng để đối chiếu IPA, nghĩa và gợi ý câu ví dụ; câu sai được sửa hoặc thay.

Nguồn tham khảo để xác định mức B2: [LexiCore-5000](https://github.com/X-Trivle/LexiCore)
([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)),
[Words CEFR Dataset](https://github.com/Maximax67/Words-CEFR-Dataset), và danh sách
[Oxford 3000](https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf)/[Oxford 5000](https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf)
chỉ để đối chiếu cấp độ. Deck không sao chép định nghĩa hoặc câu ví dụ Oxford.
Bản dịch ví dụ được tạo cục bộ với
[Hy-MT2-1.8B](https://huggingface.co/tencent/Hy-MT2-1.8B-GGUF)
([Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)) rồi rà soát/sửa
các lỗi phát hiện được. Không phân phối trọng số mô hình trong dự án.

**Giấy phép cho riêng dữ liệu deck `b2-1000.json`:**
[Creative Commons Attribution–ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).
Khi phân phối bản sửa đổi của deck, giữ ghi nguồn và phát hành dữ liệu phái sinh
theo cùng giấy phép. Giấy phép này không đổi giấy phép mã nguồn ứng dụng.
