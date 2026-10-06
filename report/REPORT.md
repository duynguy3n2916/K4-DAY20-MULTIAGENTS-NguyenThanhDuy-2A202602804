# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Thành Duy | 2A202602804 | Cài đặt harness, chạy thí nghiệm và phân tích kết quả |

- Mô hình: `openai:gpt-4o-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60`.
- Deep Agents: phiên bản ghim trong `pyproject.toml` là `0.7.21`. Môi trường chạy: Windows 11, `.venv` (Python 3.12.10).
- Số lần chạy tác vụ đã dùng: 21 lần chạy tác vụ (gồm 6 baseline, 6 subagents, 3 skills-auto ở Phần 3.4 lưu tại `results/skills-auto-dev`, 6 skills-auto chính thức sau đóng băng) + 1 lần gọi curator.
- Commit của tag `freeze`: `89a15289fddd6fd2dde3d2ea7d31e5d6397192bd`.

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

Trong 21 check thất bại, 10 thuộc D, 9 thuộc E, 1 thuộc A và 1 thuộc B. D chiếm 10/21, E chiếm 9/21. Skill quy trình có thể nhắc kiểm tra định dạng, dữ liệu bẩn và quy ước đầu ra, nhưng không thay thế việc tính toán từ dữ liệu thô. `code-learn` bị `GraphRecursionError` sau 60 bước, làm gián đoạn một phần thao tác ghi nhận vết. Số check kỹ thuật đạt ở baseline học là 6/18 (chiếm 33.3%), trong khi quy ước tổ chức đạt 0/9 (0%), cho thấy tác tử giải quyết được một phần logic bài toán nhưng hoàn toàn bỏ qua các quy ước ngầm nếu không được hướng dẫn tường minh.

## 5. Điều kiện `subagents` (Phần 2.3)

- Ba subagent: `explorer` đọc và báo cáo ràng buộc, `implementer` thay đổi tệp theo yêu cầu, `reviewer` kiểm tra độc lập. Tách vai trò để tác tử chính có thể giao việc theo giai đoạn.
- `subagent_calls` ở từng tác vụ:
  - Tác vụ học: `code-learn=0`, `data-learn=1` (gọi `implementer`), `logs-learn=0`.
  - Tác vụ đánh giá: `code-eval=0`, `data-eval=0`, `logs-eval=0`.
  - Tổng cộng 5/6 lần chạy có `subagent_calls = 0`. Tác tử chính chủ động tự thực hiện hầu hết các tác vụ dù prompt (`SUBAGENTS_NOTE`) khuyến khích phân rã công việc.
- Lời giao việc ở `data-learn` có tên tệp và năm trường kết quả, nhưng chỉ nói chung “clean the data according to Acme's reporting conventions”; không truyền đầy đủ từ điển dữ liệu và quy tắc chuẩn hóa. Tác tử chính nhận báo cáo đã tạo `answer.json` nhưng kết quả vẫn chỉ đạt 1/8.
- Token và thời gian so với baseline:
  - Tác vụ học: `code-learn` 81,297 tokens (40.1s) so với 150,650 tokens (56.9s); `data-learn` 107,422 tokens (51.3s) so với 25,608 tokens (15.0s); `logs-learn` 20,169 tokens (13.7s) so với 19,584 tokens (11.8s).
  - Tác vụ đánh giá: `code-eval` 33,305 tokens (21.3s) so với 266,696 tokens (144.5s); `data-eval` 401,228 tokens (137.7s) so với 383,630 tokens (133.8s, cùng dính `GraphRecursionError`); `logs-eval` 18,609 tokens (12.0s) so với 17,755 tokens (12.0s).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator đã chạy 1 lần trên ba `baseline` của tác vụ học, sinh 3 skill hợp lệ về định dạng và không chứa bất kỳ từ khóa đánh giá nào. Cả ba được giữ nguyên không sửa tay để phản ánh chính xác năng lực tự tiến hóa.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `prevent-test-modification` | Có thể áp dụng cho tác vụ sửa code mới. | Giữ test gốc là đúng; chỉ dẫn “always create new test files” hơi rộng nếu không cần thêm test. | 5 bước; mô tả nêu tình huống giữ nguyên test. `skills_read=0` ở cả ba lần chạy học. |
| `validate-currency-format` | Áp dụng cho tác vụ dữ liệu tiền tệ; ví dụ số lấy từ phản hồi học (`1606.67`) làm skill kém tổng quát. | Quy đổi cent đúng; câu “no negative values” có ngoại lệ và phải theo đặc tả dữ liệu. | 5 bước; mô tả hợp tác vụ tiền. `skills_read=0` ở cả ba lần chạy học. |
| `generate-changelog-entries` | Áp dụng cho dự án có changelog cùng quy ước. | Mẫu bullet đúng với phản hồi học; yêu cầu “at least three entries” phản ánh sát yêu cầu học nhưng có thể gượng ép ở tác vụ mới. | 5 bước; mô tả về changelog khá hẹp. `skills_read=0` ở cả ba lần chạy học. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

### Bảng so sánh tổng hợp (`report/table.md`)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 2/10 | 0/10 |
| data-learn | 1/8 | 1/8 | 0/8 |
| logs-learn | 1/9 | 1/9 | 1/9 |
| code-eval | 1/11 | 1/11 | 2/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.21 | 0.15 | 0.04 |
| **Mean score - evaluation tasks** | 0.06 | 0.06 | 0.09 |
| **Mean tokens per run** | 143,987 | 110,338 | 89,240 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

### Phân rã check kỹ thuật và quy ước (`python scripts/check_breakdown.py`)

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      2/18         0/12         222,693      0/3     
baseline      learn     6/18         0/9           65,280      0/3     
subagents     eval      2/18         0/12         151,047      0/3     
subagents     learn     4/18         0/9           69,629      0/3     
skills-auto   eval      3/18         0/12          27,437      0/3     
skills-auto   learn     1/18         0/9          151,042      0/3     
```

### Xử lý lỗi và tính toàn vẹn:
- Các lần chạy chạm giới hạn đệ quy (`recursion_limit=60` dẫn đến `GraphRecursionError`):
  - `baseline`: `code-eval` (144.5s), `code-learn` (56.9s), `data-eval` (133.8s)
  - `subagents`: `data-eval` (137.7s)
  - `skills-auto`: `data-learn` (158.4s)
  - `skills-auto-dev`: `code-learn` (41.0s), `data-learn` (134.2s)
  Hàm `run_task` đã xử lý bắt lỗi ngoại lệ, ghi nhận vào trường `error` của `run.json`, giữ lại các tệp trong workspace và hoàn thành việc chấm điểm tự động mà không làm sập luồng điều khiển.
- Kiểm tra toàn vẹn skill: Toàn bộ các lần chạy của `skills-auto` đều ghi nhận `skills_modified = false`. Lệnh `python scripts/verify_freeze.py` đạt kết quả `OK` tuyệt đối (6/6 runs hợp lệ sau thời điểm tag `freeze`).

## 8. Phân tích

1. **So sánh điểm số giữa các điều kiện:**
   - Trên tác vụ **học**: Không có điều kiện nào cải thiện so với `baseline` (0.21). `subagents` đạt 0.15 và `skills-auto` đạt 0.04 (hoặc 0.10 ở Phần 3.4). Cả hai điều kiện can thiệp đều có điểm học thấp hơn baseline.
   - Trên tác vụ **đánh giá**: `baseline` đạt 0.06, `subagents` đạt 0.06 (tương đương baseline), `skills-auto` đạt 0.09 (nhờ đạt 2/11 ở `code-eval` so với 1/11 của baseline).
   - Không có điều kiện nào cải thiện tác vụ học nhưng suy giảm trên đánh giá. Hiện tượng `skills-auto` có điểm học thấp hơn nhưng điểm đánh giá cao hơn nhẹ (0.04 so với 0.09) không phản ánh quy luật học/tổng quát hóa thực sự, vì trường `skills_read = 0` cho thấy tác tử không đọc bất kỳ skill nào; sự biến thiên này thuần túy là nhiễu ngẫu nhiên của mô hình.

2. **Phân rã check kỹ thuật và check quy ước (`rule_`):**
   - Trên toàn bộ 18 lần chạy (3 điều kiện x 6 tác vụ), tất cả các check quy ước tổ chức (`house rules`) đều đạt **0%** (0/9 ở tập học và 0/12 ở tập đánh giá).
   - Toàn bộ điểm số đạt được đều đến từ nhóm check kỹ thuật (ví dụ `add_slot_no_shared_state`, `billable_blocks_round_up`, `valid_structure`, `top_region`).
   - Các skill do curator sinh ra (dù nhắm đúng vào các quy ước như format tiền theo cent, tạo changelog, giữ test) hoàn toàn không giúp đạt thêm check quy ước nào vì tác tử không đọc skill vào ngữ cảnh thực thi.
   - Check quy ước mới của tác vụ đánh giá (như `rule_version_bump`, `rule_negative_margin`, `rule_session_id`) không xuất hiện trong `skills/auto/` do curator bị chặn nghiêm ngặt không được tiếp cận dữ liệu đánh giá; đồng thời do tác tử không đọc skill nên cũng không có khả năng suy luận mở rộng.

3. **Cơ chế tác động qua vết thực thi (`trace.md`) và `skills_read`:**
   - Trường `skills_read = 0` trên tất cả các tác vụ.
   - *Check dường như được cải thiện:* Trong `skills-auto/code-eval`, check `negative_minutes_rejected` đạt `true` (2/11 điểm). Tuy nhiên, vết `trace.md` cho thấy tác tử gọi trực tiếp `read_file` trên `workspace/bookings/billing.py`, đọc docstring "`minutes` must be >= 0; a negative value raises ValueError", rồi tự bổ sung nhánh kiểm tra `if minutes < 0: raise ValueError(...)`. Tác tử hoàn toàn không gọi đọc skill nào trong `skills/auto/`. Check này đạt là nhờ năng lực đọc hiểu docstring nội tại của LLM tại lượt sinh đó.
   - *Check mà skill không giúp:* Check `rule_changelog` và `rule_regression_tests` trong `code-learn` và `code-eval`. Mặc dù curator đã tạo skill `generate-changelog-entries` rất chi tiết, tác tử không hề mở file `skills/auto/generate-changelog-entries/SKILL.md` mà lao thẳng vào sửa code trong `workspace/`. Vì skill không được nạp vào context, tác tử không hề biết về quy ước tạo `CHANGELOG.md`.

4. **Phân tích chi phí token và hiệu quả đa tác tử:**
   - Token trung bình mỗi lần chạy: `baseline` là 143,987 tokens; `subagents` là 110,338 tokens; `skills-auto` là 89,240 tokens.
   - Hiệu quả điểm trên token: Trên tác vụ đánh giá, `skills-auto` có chi phí token thấp nhất (27,437 tokens/run ở eval) và đạt điểm cao nhất (0.09), cho tỷ suất điểm/token cao nhất. Tuy nhiên, `subagents` tiêu tốn trung bình 151,047 tokens trên tác vụ đánh giá nhưng chỉ đạt 0.06 (ngang bằng baseline).
   - *Đa tác tử không đáng chi phí:* Trong thí nghiệm này, `subagents` chỉ được kích hoạt duy nhất 1 lần ở `data-learn` (gọi `implementer`), tiêu tốn 107,422 tokens (gấp 4.2 lần so với 25,608 tokens của baseline) nhưng vẫn chỉ đạt 1/8 điểm. Ở 5 tác vụ còn lại, subagent không được gọi lần nào nhưng sự hiện diện của tool `task` và prompt hướng dẫn vẫn gây lãng phí context overhead.

5. **Rò rỉ dữ liệu (Data leakage) và quá khớp (Overfitting):**
   - *Rò rỉ dữ liệu:* Hoàn toàn không xảy ra. Hàm `curate_skills` chỉ chọn các bản ghi có `role == "learn"`, loại trừ toàn bộ dữ liệu eval. Bộ lọc `validate_skill` với danh sách `eval_markers()` tự động xác nhận không có bất kỳ định danh hoặc từ khóa đánh giá nào lọt vào `skills/auto/`.
   - *Quá khớp:* Có dấu hiệu quá khớp nội dung trong văn bản skill sinh ra. Ví dụ skill `validate-currency-format` chứa nguyên số liệu `1606.67 USD becomes 160667` từ lỗi của `data-learn`; skill `generate-changelog-entries` yêu cầu "at least three entries" theo đúng số lượng test của `code-learn`. Nhóm đã phòng tránh bằng cách đưa chỉ dẫn nghiêm ngặt trong prompt của curator ("never copy task identifiers, specific answers, or numbers from an example"), giúp cấu trúc hành động vẫn duy trì được tính khái quát dạng checklist.

6. **Đo lường nhiễu (Noise estimation):**
   - Đối chiếu điểm tác vụ học của `skills-auto` giữa Phần 3.4 (`skills-auto-dev`) và sau đóng băng (`skills-auto`):
     - `code-learn`: giảm từ 2/10 (0.20) xuống 0/10 (0.00), chênh lệch -0.20.
     - `data-learn`: 0/8 (0.00) giữ nguyên 0/8 (0.00).
     - `logs-learn`: 1/9 (0.11) giữ nguyên 1/9 (0.11).
     - Điểm trung bình tác vụ học giảm từ 0.10 xuống 0.04 (chênh lệch 0.06).
   - Sự dao động 0.06 (tương đương 6% điểm toàn bài) trên cùng một bộ mã, cùng bộ skill đóng băng và cùng mô hình ở `temperature=0` cho thấy biên độ nhiễu thống kê rất đáng kể. Do đó, mức khác biệt 0.03 giữa baseline (0.06) và skills-auto (0.09) trên tác vụ đánh giá nằm hoàn toàn trong phạm vi phương sai ngẫu nhiên, không đủ bằng chứng bác bỏ giả thuyết H2.

## 9. Hạn chế và tính hợp lệ

1. **Cỡ mẫu tác vụ nhỏ (Small sample size):** Thí nghiệm chỉ gồm 3 tác vụ học và 3 tác vụ đánh giá (tổng cộng 6 tác vụ). Với mỗi tác vụ chỉ có từ 8 đến 11 check, việc một check đổi trạng thái đạt/không đạt sẽ làm thay đổi điểm số trung bình tới 9-12%, khiến các chỉ số trung bình rất nhạy cảm với biến động cục bộ.
2. **Đánh giá một lần chạy (Single-run evaluation) và phương sai mô hình:** Do giới hạn về chi phí API, mỗi cấu hình chỉ chạy một lần duy nhất. Độ lệch quan sát được giữa Phần 3.4 và sau đóng băng (lên tới 0.20 trên `code-learn`) chứng minh tính ngẫu nhiên của LLM trong chuỗi gọi công cụ nhiều lượt là rất lớn, không đủ cơ sở để thực hiện kiểm định ý nghĩa thống kê (t-test, p-value).
3. **Nút thắt tra cứu kỹ năng (Skill retrieval bottleneck):** Thiết kế progressive disclosure dựa vào việc mô hình tự đọc thư mục `skills/` thông qua mô tả ngắn. Với mô hình `gpt-4o-mini`, mô hình bị thiên kiến chú ý mạnh mẽ vào yêu cầu công việc cụ thể ("hãy sửa workspace/..."), dẫn đến `skills_read = 0` trên 100% các lần chạy. Thí nghiệm thực tế đo lường khả năng "tự phát hiện và kích hoạt đọc skill" hơn là giá trị của bản thân tri thức trong skill.
4. **Giới hạn đệ quy (`recursion_limit=60`):** Một số lần chạy (`baseline/code-eval`, `subagents/data-eval`, `skills-auto/data-learn`) bị ngắt bởi `GraphRecursionError`, làm điểm số phản ánh trạng thái dở dang thay vì kết quả hoàn chỉnh của tác tử.

## 10. Kết luận

1. Bộ khung thí nghiệm Deep Agents hoàn chỉnh đã được cài đặt và kiểm thử thành công, đáp ứng 32/32 unit tests ngoại tuyến và vượt qua 100% giao thức đóng băng của `verify_freeze.py`.
2. Trên tác vụ đánh giá, điểm trung bình của `baseline` (0.06) và `subagents` (0.06) là ngang bằng nhau, trong khi `skills-auto` đạt 0.09 nhưng mức tăng này nằm trọn trong biên độ nhiễu thống kê quan sát được (0.06).
3. Kiến trúc đa tác tử chưa phát huy hiệu quả do tác tử chính hiếm khi phân rã công việc và gặp khó khăn trong việc truyền tải đầy đủ ngữ cảnh qua lời giao việc.
4. Cơ chế progressive disclosure không kích hoạt được mô hình tự đọc skill khi đối mặt với tác vụ kỹ thuật cụ thể, dẫn đến toàn bộ các check quy ước tổ chức đều thất bại.
5. Hướng cải tiến tiếp theo là thay thế việc đọc file thủ công bằng cơ chế tiêm ngữ cảnh tự động (Dynamic In-Context Injection hoặc RAG) kết hợp với đánh giá lặp lại nhiều lần (multi-trial) để triệt tiêu nhiễu.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py` (15/15 passed)
  2. `python scripts/tour.py`
  3. Cài đặt `src/lab/subagents.py`, `src/lab/agent.py`, `src/lab/runner.py` và chạy `pytest tests/test_02_agent.py`, `pytest tests/test_03_runner.py`
  4. Chạy tác vụ học đường cơ sở: `python -m lab.runner --condition baseline --tasks data-learn code-learn logs-learn`
  5. Chạy tác vụ học đa tác tử: `python -m lab.runner --condition subagents --tasks learn`
  6. Cài đặt `src/lab/curator.py`, kiểm thử: `pytest tests/test_04_curator.py`
  7. Chạy curator sinh skill: `python -m lab.curator`
  8. Chạy kiểm tra skill trên tác vụ học (Phần 3.4): `python -m lab.runner --condition skills-auto --tasks learn`
  9. Sao lưu kết quả Phần 3.4: `mv results/skills-auto results/skills-auto-dev`
  10. Điền giả thuyết H1-H3 và commit: `git add -A && git commit -m "hypotheses"`
  11. Đóng băng bộ skill: `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze`
  12. Chạy đánh giá chính thức sau đóng băng:
      - `python -m lab.runner --condition baseline --tasks eval`
      - `python -m lab.runner --condition subagents --tasks eval`
      - `python -m lab.runner --condition skills-auto --tasks all`
  13. Xác minh giao thức đóng băng: `python scripts/verify_freeze.py` (kết quả `OK`)
  14. Xuất bảng so sánh và phân tích: `python -m lab.compare > report/table.md` và `python scripts/check_breakdown.py`
  15. Hoàn thiện báo cáo toàn diện tại `report/REPORT.md`.
- Ghi chú khác: Toàn bộ quá trình thực nghiệm được thực hiện nghiêm túc, tuân thủ nguyên tắc không can thiệp thủ công vào kết quả và thư mục kỹ năng sau đóng băng.
