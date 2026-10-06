# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thành Duy | 2A202602804 | Cài đặt harness, chạy thí nghiệm và phân tích kết quả |

- Mô hình: `openai:gpt-4o-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60`.
- Deep Agents: phiên bản ghim trong `pyproject.toml` là `0.7.21`. Môi trường chạy: Windows, `.venv`, không dùng Docker. Hướng dẫn dự án khuyến nghị WSL hoặc Docker; khác biệt môi trường này ảnh hưởng đến lệnh shell của tác tử.
- Số lần chạy tác vụ trước đóng băng: 9 (3 baseline, 3 subagents, 3 skills-auto trên tác vụ học). Curator gọi mô hình 1 lần.
- Commit của tag `freeze`: điền sau khi tạo tag.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): dự đoán không cải thiện điểm trung bình trên tác vụ đánh giá. Trên ba tác vụ học, subagents đạt 2/10, 1/8, 1/9 so với baseline 4/10, 1/8, 1/9; chỉ `data-learn` có 1 lần giao việc, và token tăng ở cả ba tác vụ.
- H2 (skills-auto so với baseline): dự đoán không cải thiện điểm trung bình tác vụ đánh giá. Ba skill sinh ra chỉ nhắm vào bảo toàn test, changelog và tiền theo cent; không bao quát log và các quy ước mới. Theo phần thảo luận SkillsBench/SkillEvolBench trong `GUIDE.md`, hiệu quả skill tự sinh và khả năng chuyển sang tác vụ mới không được bảo đảm.
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán điểm trung bình của `skills-auto` trên tác vụ đánh giá không cao hơn tác vụ học, vì tác vụ đánh giá có dữ liệu mới và thêm quy ước chưa xuất hiện trong phản hồi học. Đây là dự đoán trước khi xem điểm đánh giá.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ tệp gồm `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; `execute` chạy lệnh shell; `task` giao việc cho subagent. Danh sách được nêu trong `scripts/tour.py` và kiểm tra trong `tests/test_02_agent.py`.
2. `task` cung cấp subagent `general-purpose` cho các việc có thể giao độc lập. Subagent nhận yêu cầu giao việc, không tự nhận toàn bộ ngữ cảnh của tác tử chính; vì thế lời giao việc phải mang đủ quy tắc và đường dẫn.
3. Deep Agents mặc định không nhận system prompt riêng trong `scripts/tour.py`. Mô tả `task` hướng dẫn tác tử giao việc với yêu cầu cụ thể; mô tả `execute` hướng dẫn chạy lệnh shell trong backend. Hai mô tả công cụ cũng là nguồn chỉ dẫn hành vi.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | tests_not_modified | B | `the original files in tests/ must not be modified` |
| code-learn | parse_price_all_formats | D | `wrong for: ['(12.00)']` |
| code-learn | csv_quoting_follows_docstring | A | `to_csv_row returned 'Desk, large "oak",10.00,2'` |
| code-learn | rule_type_hints | E | `RULE: every public function ... has type annotations` |
| code-learn | rule_regression_tests | E | `RULE: add tests/test_regressions.py ... at least 3` |
| code-learn | rule_changelog | E | `RULE: record each fix in CHANGELOG.md ...` |
| data-learn | north_q1_revenue | D | `wrong value (got 0)`; vết cho thấy lỗi `ModuleNotFoundError: No module named 'pandas'` rồi ghi giá trị giữ chỗ. |
| data-learn | north_q1_orders | D | `wrong value (got 0)`; vết ghi giá trị giữ chỗ sau lỗi shell. |
| data-learn | missing_amount_orders | D | `wrong value (got 0)`; vết ghi giá trị giữ chỗ. |
| data-learn | duplicate_rows_removed | D | `wrong value (got 0)`; vết ghi giá trị giữ chỗ. |
| data-learn | rule_money_in_cents | E | `RULE: money values in answer.json are integer cents` |
| data-learn | rule_meta_block | E | `RULE: answer.json has an object meta` |
| data-learn | rule_clean_csv | E | `RULE: write workspace/clean.csv ...` |
| logs-learn | entry_count | D | `wrong number of entries (got 10)` |
| logs-learn | timestamps_utc | D | `4/25 timestamps match` |
| logs-learn | exception_fields | D | `21 wrong exception values` |
| logs-learn | repeat_counts | D | `21 wrong repeat_count values` |
| logs-learn | counts_by_service | D | `wrong values` |
| logs-learn | rule_service_names | E | `RULE: service names ... lower-case with '-' replaced by '_'` |
| logs-learn | rule_sorted_errors | E | `RULE: errors is sorted by service, then by timestamp_utc` |
| logs-learn | rule_schema_header | E | `RULE: ... schema_version: 2 and generated_by: log-triage` |

Trong 21 check thất bại, 10 thuộc D, 9 thuộc E, 1 thuộc A và 1 thuộc B. D chiếm 10/21, E chiếm 9/21. Skill quy trình có thể nhắc kiểm tra định dạng, dữ liệu bẩn và quy ước đầu ra, nhưng không thay thế việc tính lại từ dữ liệu. `code-learn` bị `GraphRecursionError`, nên `trace.md` rỗng và không thể kết luận chính xác tác tử đã làm những bước nào.

## 5. Điều kiện `subagents` (Phần 2.3)

- Ba subagent: `explorer` đọc và báo cáo ràng buộc, `implementer` thay đổi tệp theo yêu cầu, `reviewer` kiểm tra độc lập. Tách vai trò để tác tử chính có thể giao việc theo giai đoạn.
- `subagent_calls`: `code-learn=0`, `data-learn=1` (gọi `implementer`), `logs-learn=0`. Hai lần bằng 0 cho thấy tác tử chính tự làm dù prompt khuyến khích giao việc.
- Lời giao việc ở `data-learn` có tên tệp và năm trường kết quả, nhưng chỉ nói chung “clean the data according to Acme's reporting conventions”; không truyền đầy đủ từ điển dữ liệu và quy tắc chuẩn hóa. Tác tử chính nhận báo cáo đã tạo `answer.json` nhưng kết quả vẫn chỉ đạt 1/8.
- Token so với baseline: `code-learn` 81,297 so với 150,650 (giảm nhưng điểm cũng giảm 4/10 xuống 2/10); `data-learn` 107,422 so với 25,608; `logs-learn` 20,169 so với 19,584. Thời gian tương ứng 40.1/56.9, 51.3/15.0 và 13.7/11.8 giây.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator đã chạy 1 lần trên ba `baseline` của tác vụ học, sinh 3 skill hợp lệ về định dạng. Chưa xóa skill nào; cả ba được giữ để đo đúng đầu ra tự sinh, đồng thời ghi nhận hạn chế của từng skill.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `prevent-test-modification` | Có thể áp dụng cho tác vụ sửa code mới. | Giữ test gốc là đúng; chỉ dẫn “always create new test files” hơi rộng nếu không cần thêm test. | 5 bước; mô tả nêu tình huống giữ nguyên test. `skills_read=0` ở cả ba lần chạy học. |
| `validate-currency-format` | Áp dụng cho tác vụ dữ liệu tiền tệ; ví dụ số lấy từ phản hồi học làm skill kém tổng quát. | Quy đổi cent đúng; câu “no negative values” có ngoại lệ và phải theo đặc tả dữ liệu. | 5 bước; mô tả hợp tác vụ tiền. `skills_read=0` ở cả ba lần chạy học. |
| `generate-changelog-entries` | Áp dụng cho dự án có changelog cùng quy ước. | Mẫu bullet đúng với phản hồi học; yêu cầu “at least three entries” có thể sai khi tác vụ mới chỉ có ít lỗi. | 5 bước; mô tả về changelog khá hẹp. `skills_read=0` ở cả ba lần chạy học. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
