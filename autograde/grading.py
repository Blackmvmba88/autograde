from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any


def grade_exam(exam: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    questions = exam.get("questions", [])
    response_map = responses.get("answers", {})
    max_points = 0.0
    earned_points = 0.0
    results: list[dict[str, Any]] = []

    for question in questions:
        points = float(question.get("points", 1))
        max_points += points
        qid = question["id"]
        given = response_map.get(qid)
        expected = _expected_answer(question)
        correct = _is_correct(question, given, expected)
        if correct:
            earned_points += points
        results.append(
            {
                "question_id": qid,
                "correct": correct,
                "expected": expected,
                "given": given,
                "points": points if correct else 0,
            }
        )

    percentage = (earned_points / max_points * 100.0) if max_points else 0.0
    report = {
        "score": round(earned_points, 2),
        "max_score": round(max_points, 2),
        "percentage": round(percentage, 2),
        "results": results,
    }
    competency = exam.get("competency")
    report["competency"] = competency
    return report


def _expected_answer(question: dict[str, Any]) -> Any:
    if question.get("type") == "multiple_choice":
        return question.get("correct_choice_id")
    return question.get("answer_key")


def _is_correct(question: dict[str, Any], given: Any, expected: Any) -> bool:
    qtype = question.get("type")
    if qtype == "multiple_choice":
        return given == expected
    if qtype == "true_false":
        return _coerce_bool(given) == _coerce_bool(expected)
    if qtype in {"short_answer", "open_ended", "practical"}:
        return _normalize_text(given) == _normalize_text(expected)
    return given == expected


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().casefold()


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "t", "yes", "y", "1"}:
            return True
        if normalized in {"false", "f", "no", "n", "0"}:
            return False
    return None
