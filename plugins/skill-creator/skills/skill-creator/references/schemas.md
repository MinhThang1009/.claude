# JSON Schema

Tài liệu này định nghĩa các JSON schema được skill-creator sử dụng.

---

## evals.json

Định nghĩa các eval cho một skill. Nằm tại `evals/evals.json` trong thư mục skill.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Prompt ví dụ của người dùng",
      "expected_output": "Mô tả kết quả mong đợi",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "Output bao gồm X",
        "Skill đã dùng script Y"
      ]
    }
  ]
}
```

**Các field:**
- `skill_name`: Tên khớp với frontmatter của skill
- `evals[].id`: Định danh số nguyên unique
- `evals[].prompt`: Tác vụ cần thực thi
- `evals[].expected_output`: Mô tả thành công cho người đọc
- `evals[].files`: Danh sách đường dẫn file input tùy chọn (tương đối với skill root)
- `evals[].expectations`: Danh sách các phát biểu có thể kiểm tra

---

## history.json

Theo dõi tiến trình version trong Improve mode. Nằm tại workspace root.

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**Các field:**
- `started_at`: Timestamp ISO lúc bắt đầu cải thiện
- `skill_name`: Tên skill đang được cải thiện
- `current_best`: Định danh version của version hoạt động tốt nhất
- `iterations[].version`: Định danh version (v0, v1, ...)
- `iterations[].parent`: Version cha mà version này được derive từ đó
- `iterations[].expectation_pass_rate`: Tỉ lệ pass từ grading
- `iterations[].grading_result`: "baseline", "won", "lost", hoặc "tie"
- `iterations[].is_current_best`: Version này có phải là version tốt nhất hiện tại không

---

## grading.json

Output từ grader agent. Nằm tại `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {
      "text": "Output bao gồm tên 'John Smith'",
      "passed": true,
      "evidence": "Tìm thấy trong transcript Bước 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "Spreadsheet có công thức SUM trong ô B10",
      "passed": false,
      "evidence": "Không có spreadsheet nào được tạo. Output là file text."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "Form có 12 fillable field",
      "type": "factual",
      "verified": true,
      "evidence": "Đếm được 12 field trong field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Dùng dữ liệu 2023, có thể lỗi thời"],
    "needs_review": [],
    "workarounds": ["Fallback về text overlay cho field không thể điền"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "Output bao gồm tên 'John Smith'",
        "reason": "Tài liệu bịa đặt có đề cập tên này cũng sẽ pass"
      }
    ],
    "overall": "Assertion kiểm tra sự tồn tại nhưng không kiểm tra tính chính xác."
  }
}
```

**Các field:**
- `expectations[]`: Expectation đã được chấm điểm kèm bằng chứng
- `summary`: Tổng hợp số pass/fail
- `execution_metrics`: Lượng dùng tool và kích thước output (từ metrics.json của executor)
- `timing`: Thời gian thực (từ timing.json)
- `claims`: Các claim được trích xuất và kiểm tra từ output
- `user_notes_summary`: Vấn đề được executor gắn cờ
- `eval_feedback`: (tùy chọn) Gợi ý cải thiện cho eval, chỉ có khi grader xác định vấn đề đáng đề cập

---

## metrics.json

Output từ executor agent. Nằm tại `<run-dir>/outputs/metrics.json`.

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Bash": 8,
    "Edit": 1,
    "Glob": 2,
    "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**Các field:**
- `tool_calls`: Số lần gọi theo từng loại tool
- `total_tool_calls`: Tổng tất cả tool call
- `total_steps`: Số bước thực thi chính
- `files_created`: Danh sách file output được tạo
- `errors_encountered`: Số lỗi xảy ra trong quá trình thực thi
- `output_chars`: Tổng số ký tự của file output
- `transcript_chars`: Số ký tự của transcript

---

## timing.json

Thời gian thực cho một lần chạy. Nằm tại `<run-dir>/timing.json`.

**Cách capture:** Khi tác vụ subagent hoàn thành, thông báo tác vụ bao gồm `total_tokens` và `duration_ms`. Lưu ngay lập tức — chúng không được persist ở bất kỳ đâu và không thể khôi phục sau đó.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

Output từ Benchmark mode. Nằm tại `benchmarks/<timestamp>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "claude-sonnet-4-20250514",
    "analyzer_model": "most-capable-model",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },

  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "Dùng dữ liệu 2023, có thể lỗi thời",
        "Fallback về text overlay cho field không thể điền"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "Assertion 'Output là file PDF' pass 100% ở cả hai cấu hình - có thể không phân biệt được giá trị skill",
    "Eval 3 có variance cao (50% ± 40%) - có thể không ổn định hoặc phụ thuộc model",
    "Các lần chạy without-skill liên tục fail ở expectation trích xuất bảng",
    "Skill thêm trung bình 13s thời gian thực thi nhưng cải thiện pass rate lên 50%"
  ]
}
```

**Các field:**
- `metadata`: Thông tin về lần chạy benchmark
  - `skill_name`: Tên skill
  - `timestamp`: Thời điểm chạy benchmark
  - `evals_run`: Danh sách tên hoặc ID eval
  - `runs_per_configuration`: Số lần chạy mỗi cấu hình (ví dụ 3)
- `runs[]`: Kết quả chạy từng lần
  - `eval_id`: Định danh eval dạng số
  - `eval_name`: Tên eval cho người đọc (dùng làm tiêu đề section trong viewer)
  - `configuration`: Phải là `"with_skill"` hoặc `"without_skill"` (viewer dùng chính xác chuỗi này để nhóm và tô màu)
  - `run_number`: Số nguyên lần chạy (1, 2, 3...)
  - `result`: Object lồng nhau với `pass_rate`, `passed`, `total`, `time_seconds`, `tokens`, `errors`
- `run_summary`: Tổng hợp thống kê theo từng cấu hình
  - `with_skill` / `without_skill`: Mỗi cái chứa object `pass_rate`, `time_seconds`, `tokens` với field `mean` và `stddev`
  - `delta`: Chuỗi chênh lệch như `"+0.50"`, `"+13.0"`, `"+1700"`
- `notes`: Quan sát tự do từ analyzer

**Quan trọng:** Viewer đọc chính xác các tên field này. Dùng `config` thay vì `configuration`, hoặc đặt `pass_rate` ở cấp cao nhất của run thay vì lồng trong `result`, sẽ khiến viewer hiển thị giá trị trống/zero. Luôn tham chiếu schema này khi tạo benchmark.json thủ công.

---

## comparison.json

Output từ blind comparator. Nằm tại `<grading-dir>/comparison-N.json`.

```json
{
  "winner": "A",
  "reasoning": "Output A cung cấp giải pháp hoàn chỉnh với định dạng đúng và đủ tất cả field bắt buộc. Output B thiếu field ngày và có định dạng không nhất quán.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Giải pháp hoàn chỉnh", "Định dạng tốt", "Đủ tất cả field"],
      "weaknesses": ["Không nhất quán nhỏ về style ở header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Output dễ đọc", "Cấu trúc cơ bản đúng"],
      "weaknesses": ["Thiếu field ngày", "Định dạng không nhất quán", "Trích xuất dữ liệu không đầy đủ"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "Output bao gồm tên", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "Output bao gồm tên", "passed": true}
      ]
    }
  }
}
```

---

## analysis.json

Output từ post-hoc analyzer. Nằm tại `<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Tóm tắt ngắn lý do comparator chọn winner"
  },
  "winner_strengths": [
    "Hướng dẫn từng bước rõ ràng cho việc xử lý tài liệu nhiều trang",
    "Có script validation bắt được lỗi định dạng"
  ],
  "loser_weaknesses": [
    "Hướng dẫn mơ hồ 'xử lý tài liệu phù hợp' dẫn đến hành vi không nhất quán",
    "Không có script validation, agent phải tự ứng biến"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": ["Nhỏ: bỏ qua bước logging tùy chọn"]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Không dùng formatting template của skill",
        "Tự nghĩ ra cách tiếp cận thay vì làm theo bước 3"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Thay 'xử lý tài liệu phù hợp' bằng các bước tường minh",
      "expected_impact": "Sẽ loại bỏ sự mơ hồ gây ra hành vi không nhất quán"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Đọc skill -> Làm theo quy trình 5 bước -> Dùng script validation",
    "loser_execution_pattern": "Đọc skill -> Không rõ cách tiếp cận -> Thử 3 phương pháp khác nhau"
  }
}
```
