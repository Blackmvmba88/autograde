from __future__ import annotations

from typing import Any

TARGET_TO_FORMAT = {
    "omr": "omr",
    "web": "quiz",
    "pdf": "open",
    "simulation": "simulation",
}


def render_exam(exam: dict[str, Any], target: str) -> dict[str, Any]:
    if target not in {"omr", "web", "pdf", "simulation"}:
        raise ValueError(f"unsupported render target: {target}")

    return {
        "target": target,
        "exam_id": exam["id"],
        "title": exam["title"],
        "subject": exam["subject"],
        "level": exam.get("level"),
        "difficulty": exam.get("difficulty"),
        "competency": exam.get("competency"),
        "format": TARGET_TO_FORMAT[target],
        "items": [
            _render_item(question, target)
            for question in exam.get("questions", [])
        ],
    }


def _render_item(question: dict[str, Any], target: str) -> dict[str, Any]:
    base = {
        "id": question["id"],
        "type": question["type"],
        "prompt": question["prompt"],
        "points": question.get("points", 1),
        "tags": question.get("tags", []),
    }
    if question["type"] == "multiple_choice":
        base["choices"] = question.get("choices", [])
        if target == "omr":
            base["layout"] = "bubble_sheet"
        elif target == "web":
            base["layout"] = "radio_group"
        elif target == "pdf":
            base["layout"] = "fillable_pdf"
        elif target == "simulation":
            base["layout"] = "interactive_choice"
    else:
        base["answer_key"] = question.get("answer_key")
    return base
