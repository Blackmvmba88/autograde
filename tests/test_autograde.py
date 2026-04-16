from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from autograde.cli import main
from autograde.grading import grade_exam
from autograde.schema import load_exam, normalize_exam, validate_exam_structure


class AutoGradeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.exam_path = Path("examples/exam_math_v1.json")
        self.responses_path = Path("examples/responses_math_v1.json")

    def test_validate_sample_exam(self) -> None:
        exam = load_exam(self.exam_path)
        self.assertEqual(validate_exam_structure(exam), [])

    def test_normalize_fills_missing_scoring(self) -> None:
        exam = load_exam(self.exam_path)
        exam.pop("scoring", None)
        normalized = normalize_exam(exam)
        self.assertEqual(normalized["scoring"]["mode"], "points_per_question")
        self.assertEqual(normalized["scoring"]["max_points"], 1)

    def test_grade_sample_response(self) -> None:
        exam = load_exam(self.exam_path)
        responses = load_exam(self.responses_path)
        report = grade_exam(exam, responses)
        self.assertEqual(report["score"], 1.0)
        self.assertEqual(report["percentage"], 100.0)
        self.assertTrue(report["results"][0]["correct"])

    def test_cli_validate_command(self) -> None:
        exit_code = main(["validate", str(self.exam_path)])
        self.assertEqual(exit_code, 0)

    def test_cli_generate_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "generated.json"
            exit_code = main(["generate", "--template", str(self.exam_path), "--out", str(out_path)])
            self.assertEqual(exit_code, 0)
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertIn("scoring", data)
            self.assertEqual(data["scoring"]["max_points"], 1)

    def test_cli_author_command(self) -> None:
        exit_code = main(["author"])
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
