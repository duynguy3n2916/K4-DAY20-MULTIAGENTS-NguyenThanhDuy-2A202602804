"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when a task needs investigation before editing: read the instructions, "
                "documentation, tests, and sample data, then report relevant rules and likely causes."
            ),
            "system_prompt": (
                "You investigate the workspace and report evidence, constraints, and likely root causes. "
                "Read relevant files and inspect edge cases. Do not modify files. "
                "Only use the task details supplied by the parent agent."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when the task requires changing code or creating requested output files "
                "after the requirements and target paths are known."
            ),
            "system_prompt": (
                "You implement the delegated task in the workspace. Follow every rule and path "
                "in the delegation, make the smallest complete change, run relevant checks, "
                "and report exactly which files changed and what the checks showed."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when completed work needs an independent check against the instructions, "
                "tests, data conventions, and edge cases before the parent agent finishes."
            ),
            "system_prompt": (
                "You independently verify the delegated work. Inspect outputs and run relevant "
                "checks without editing files. Report concrete failures and supporting evidence; "
                "do not claim success for checks you did not perform."
            ),
        },
    ]
