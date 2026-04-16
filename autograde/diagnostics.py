from __future__ import annotations

from collections import defaultdict
from typing import Any


def build_diagnostic_report(exam: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    by_tag = defaultdict(lambda: {"correct": 0, "total": 0})
    total = len(results)
    correct = 0

    question_index = {q["id"]: q for q in exam.get("questions", [])}

    for result in results:
        question = question_index.get(result["question_id"], {})
        tags = question.get("tags", [])
        if result.get("correct"):
            correct += 1
        for tag in tags:
            by_tag[tag]["total"] += 1
            if result.get("correct"):
                by_tag[tag]["correct"] += 1

    competency = exam.get("competency")
    score_pct = round((correct / total * 100.0), 2) if total else 0.0
    strengths: list[str] = []
    weaknesses: list[str] = []

    if score_pct >= 80:
        strengths.append(competency or "overall performance")
    elif score_pct < 60:
        weaknesses.append(competency or "overall performance")

    topic_breakdown = {
        tag: {
            "accuracy": round((bucket["correct"] / bucket["total"] * 100.0), 2) if bucket["total"] else 0.0,
            "correct": bucket["correct"],
            "total": bucket["total"],
        }
        for tag, bucket in by_tag.items()
    }

    weak_topics = [tag for tag, data in topic_breakdown.items() if data["total"] and data["accuracy"] < 70]
    strong_topics = [tag for tag, data in topic_breakdown.items() if data["total"] and data["accuracy"] >= 85]
    strengths.extend(strong_topics[:3])
    weaknesses.extend(weak_topics[:3])

    return {
        "competency": competency,
        "score_percentage": score_pct,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "topic_breakdown": topic_breakdown,
    }
