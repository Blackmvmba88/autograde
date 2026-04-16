# AutoGrade

Multimodal exam evaluation engine.

Define once, render anywhere, evaluate consistently.

- OMR / paper exams
- Web quizzes
- Open responses
- Simulation-ready items

## Core Idea

AutoGrade separates evaluation into three layers:

- Content: what is asked
- Modality: how it is answered
- Evaluation: how it is graded

That lets the same exam schema travel across paper, web, and future simulation workflows without rewriting the assessment logic each time.

## Quick Demo

```bash
python -m autograde.cli validate examples/exam_math_v1.json
python -m autograde.cli render examples/exam_math_v1.json --to omr
python -m autograde.cli grade --exam examples/exam_math_v1.json --responses examples/responses_math_v1.json
```

## Install

```bash
pip install -e .
```

## CLI

```bash
autograde validate examples/exam_math_v1.json
autograde generate --template examples/exam_math_v1.json --out generated_exam.json
autograde grade --exam examples/exam_math_v1.json --responses examples/responses_math_v1.json
autograde render examples/exam_math_v1.json --to web
```

## Example Exam

`examples/exam_math_v1.json` is a minimal multiple-choice exam built to validate the full pipeline.

## Features

- Schema-based exam validation
- Exam normalization during generation
- Multi-type grading for multiple choice, true/false, short answer, open ended, and practical items
- Target-aware exam rendering for `omr`, `web`, `pdf`, and `simulation`
- Diagnostic summary by competency and tagged topics

## Roadmap

- [x] exam schema
- [x] CLI foundation
- [x] validation
- [x] grading
- [x] render layer
- [ ] OMR image ingestion
- [ ] richer rubrics for free-response grading
- [ ] visual PDF export
- [ ] browser UI

## Notes

- The current renderer returns structured JSON, not final design assets.
- Free-response grading is deterministic today and intentionally conservative.
- `examples/responses_math_v1.json` is a suggested next fixture for local testing.
