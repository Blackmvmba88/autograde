from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from autograde.schema import dump_exam, load_exam, normalize_exam, validate_exam_structure


DEFAULT_EXAM: dict[str, Any] = {
    "id": "exam-1",
    "title": "Nuevo examen",
    "subject": "general",
    "level": "high_school",
    "difficulty": "medium",
    "competency": "reasoning",
    "format": "quiz",
    "description": "",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "questions": [
        {
            "id": "q1",
            "type": "multiple_choice",
            "prompt": "Escribe tu primera pregunta.",
            "points": 1,
            "tags": [],
            "choices": [
                {"id": "a", "text": "Opcion 1"},
                {"id": "b", "text": "Opcion 2"},
            ],
            "correct_choice_id": "a",
        }
    ],
}

TEMPLATES: dict[str, dict[str, Any]] = {
    "multiple_choice": {
        **deepcopy(DEFAULT_EXAM),
        "id": "mcq-template",
        "title": "Plantilla Multiple Choice",
        "format": "omr",
        "questions": [
            {
                "id": "q1",
                "type": "multiple_choice",
                "prompt": "Pregunta de opción múltiple",
                "points": 1,
                "tags": [],
                "choices": [
                    {"id": "a", "text": "Opcion A"},
                    {"id": "b", "text": "Opcion B"},
                ],
                "correct_choice_id": "a",
            }
        ],
    },
    "mixed": {
        **deepcopy(DEFAULT_EXAM),
        "id": "mixed-template",
        "title": "Plantilla Mixta",
        "format": "quiz",
        "questions": [
            {
                "id": "q1",
                "type": "multiple_choice",
                "prompt": "Pregunta de opción múltiple",
                "points": 1,
                "tags": [],
                "choices": [
                    {"id": "a", "text": "Opcion A"},
                    {"id": "b", "text": "Opcion B"},
                ],
                "correct_choice_id": "a",
            },
            {
                "id": "q2",
                "type": "short_answer",
                "prompt": "Respuesta corta",
                "points": 1,
                "tags": [],
                "answer_key": "respuesta",
            },
        ],
    },
    "open": {
        **deepcopy(DEFAULT_EXAM),
        "id": "open-template",
        "title": "Plantilla Abierta",
        "format": "open",
        "questions": [
            {
                "id": "q1",
                "type": "open_ended",
                "prompt": "Pregunta abierta",
                "points": 1,
                "tags": [],
                "answer_key": "respuesta esperada",
            }
        ],
    },
}


def run_authoring(path: str | Path | None = None, exam: dict[str, Any] | None = None) -> int:
    output_path = Path(path) if path else None
    exam_state = deepcopy(exam) if exam is not None else deepcopy(DEFAULT_EXAM)
    if output_path and output_path.exists():
        exam_state = load_exam(output_path)
        print(f"Cargado: {output_path}")
    elif output_path:
        print(f"Nuevo examen. Guardado por defecto en: {output_path}")
    else:
        print("Nuevo examen creado en memoria.")

    try:
        while True:
            print("\n=== AutoGrade Authoring ===")
            print(f"ID: {exam_state.get('id', '')} | Titulo: {exam_state.get('title', '')} | Preguntas: {len(exam_state.get('questions', []))}")
            print("1) Editar metadatos")
            print("2) Agregar pregunta")
            print("3) Editar pregunta")
            print("4) Eliminar pregunta")
            print("5) Duplicar pregunta")
            print("6) Mover pregunta")
            print("7) Validar")
            print("8) Ver JSON")
            print("9) Guardar")
            print("10) Guardar y salir")
            print("11) Salir sin guardar")
            choice = _prompt("Opcion", default="5")

            if choice == "1":
                _edit_metadata(exam_state)
            elif choice == "2":
                exam_state.setdefault("questions", []).append(_create_question(exam_state))
            elif choice == "3":
                _edit_question(exam_state)
            elif choice == "4":
                _delete_question(exam_state)
            elif choice == "5":
                _duplicate_question(exam_state)
            elif choice == "6":
                _move_question(exam_state)
            elif choice == "7":
                _print_validation(exam_state)
            elif choice == "8":
                print(json.dumps(normalize_exam(exam_state), indent=2, ensure_ascii=False))
            elif choice == "9":
                _save_exam(exam_state, output_path)
            elif choice == "10":
                _save_exam(exam_state, output_path)
                return 0
            elif choice == "11":
                return 0
            else:
                print("Opcion no valida.")
    except EOFError:
        print("Modo interactivo requiere una terminal con entrada.")
        return 1


def _edit_metadata(exam: dict[str, Any]) -> None:
    exam["id"] = _prompt("ID", exam.get("id", ""))
    exam["title"] = _prompt("Titulo", exam.get("title", ""))
    exam["subject"] = _prompt("Materia", exam.get("subject", ""))
    exam["level"] = _prompt_choice("Nivel", exam.get("level", "high_school"), ["primary", "high_school", "university", "specialization"])
    exam["difficulty"] = _prompt_choice("Dificultad", exam.get("difficulty", "medium"), ["easy", "medium", "hard", ""])
    exam["competency"] = _prompt_choice("Competencia", exam.get("competency", "reasoning"), ["memory", "reasoning", "execution", "analysis", ""])
    exam["format"] = _prompt_choice("Formato", exam.get("format", "quiz"), ["omr", "quiz", "open", "simulation"])
    exam["description"] = _prompt("Descripcion", exam.get("description", ""))
    exam["time_limit_minutes"] = _prompt_int("Tiempo limite (min)", int(exam.get("time_limit_minutes", 30)))
    exam["passing_score"] = _prompt_float("Puntaje aprobatorio", float(exam.get("passing_score", 70)))


def _create_question(exam: dict[str, Any] | None = None) -> dict[str, Any]:
    next_index = len(exam.get("questions", [])) + 1 if exam else 1
    question = {
        "id": _prompt("Pregunta ID", f"q{next_index}"),
        "type": _prompt_choice("Tipo", "multiple_choice", ["multiple_choice", "short_answer", "true_false", "open_ended", "practical"]),
        "prompt": _prompt("Prompt", ""),
        "points": _prompt_float("Puntos", 1.0),
        "tags": _prompt_list("Tags (separados por coma)", []),
    }
    if question["type"] == "multiple_choice":
        question["choices"] = _create_choices()
        question["correct_choice_id"] = _prompt("ID de la opcion correcta", question["choices"][0]["id"] if question["choices"] else "a")
    else:
        question["answer_key"] = _prompt("Answer key", "")
    return question


def _create_choices() -> list[dict[str, Any]]:
    choices: list[dict[str, Any]] = []
    print("Agrega al menos 2 opciones. Deja ID vacio para terminar cuando ya tengas suficientes.")
    while True:
        choice_id = _prompt("Choice ID", "")
        choice_text = _prompt("Choice texto", "")
        if not choice_id and len(choices) >= 2:
            break
        if not choice_id or not choice_text:
            print("La opcion requiere ID y texto.")
            continue
        choices.append({"id": choice_id, "text": choice_text})
    return choices


def _edit_question(exam: dict[str, Any]) -> None:
    questions = exam.get("questions", [])
    if not questions:
        print("No hay preguntas.")
        return
    _print_questions(questions)
    index = _prompt_int("Numero de pregunta", 1) - 1
    if index < 0 or index >= len(questions):
        print("Indice fuera de rango.")
        return
    question = questions[index]
    question["id"] = _prompt("Pregunta ID", question.get("id", ""))
    question["type"] = _prompt_choice("Tipo", question.get("type", "multiple_choice"), ["multiple_choice", "short_answer", "true_false", "open_ended", "practical"])
    question["prompt"] = _prompt("Prompt", question.get("prompt", ""))
    question["points"] = _prompt_float("Puntos", float(question.get("points", 1)))
    question["tags"] = _prompt_list("Tags (separados por coma)", question.get("tags", []))
    if question["type"] == "multiple_choice":
        question["choices"] = _create_choices()
        question["correct_choice_id"] = _prompt("ID de la opcion correcta", question["choices"][0]["id"] if question["choices"] else "a")
        question.pop("answer_key", None)
    else:
        question["answer_key"] = _prompt("Answer key", str(question.get("answer_key", "")))
        question.pop("choices", None)
        question.pop("correct_choice_id", None)


def _delete_question(exam: dict[str, Any]) -> None:
    questions = exam.get("questions", [])
    if not questions:
        print("No hay preguntas.")
        return
    _print_questions(questions)
    index = _prompt_int("Numero de pregunta a eliminar", 1) - 1
    if 0 <= index < len(questions):
        removed = questions.pop(index)
        print(f"Eliminada: {removed.get('id')}")
    else:
        print("Indice fuera de rango.")


def _duplicate_question(exam: dict[str, Any]) -> None:
    questions = exam.get("questions", [])
    if not questions:
        print("No hay preguntas.")
        return
    _print_questions(questions)
    index = _prompt_int("Numero de pregunta a duplicar", 1) - 1
    if 0 <= index < len(questions):
        copied = deepcopy(questions[index])
        copied["id"] = _prompt("Nuevo ID", f"{copied.get('id', 'q')}_copy")
        questions.insert(index + 1, copied)
        print(f"Duplicada: {copied.get('id')}")
    else:
        print("Indice fuera de rango.")


def _move_question(exam: dict[str, Any]) -> None:
    questions = exam.get("questions", [])
    if len(questions) < 2:
        print("Hace falta al menos 2 preguntas.")
        return
    _print_questions(questions)
    index = _prompt_int("Numero de pregunta a mover", 1) - 1
    direction = _prompt_choice("Direccion", "up", ["up", "down"])
    if not (0 <= index < len(questions)):
        print("Indice fuera de rango.")
        return
    if direction == "up" and index > 0:
        questions[index - 1], questions[index] = questions[index], questions[index - 1]
    elif direction == "down" and index < len(questions) - 1:
        questions[index + 1], questions[index] = questions[index], questions[index + 1]
    else:
        print("No se puede mover en esa direccion.")


def _print_validation(exam: dict[str, Any]) -> None:
    candidate = normalize_exam(exam)
    errors = validate_exam_structure(candidate)
    if errors:
        print("Errores:")
        for error in errors:
            print(f"- {error}")
        return
    print("Exam valido.")


def _save_exam(exam: dict[str, Any], output_path: Path | None) -> None:
    if output_path is None:
        raw = _prompt("Ruta de salida", "exam.json")
        output_path = Path(raw)
    normalized = normalize_exam(exam)
    errors = validate_exam_structure(normalized)
    if errors:
        print("No se puede guardar. Corrige primero:")
        for error in errors:
            print(f"- {error}")
        return
    dump_exam(normalized, output_path)
    print(f"Guardado en {output_path}")


def _print_questions(questions: list[dict[str, Any]]) -> None:
    for index, question in enumerate(questions, start=1):
        print(f"{index}) {question.get('id', '')} [{question.get('type', '')}] {question.get('prompt', '')}")


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default != "" else ""
    value = input(f"{label}{suffix}: ").strip()
    return value if value else default


def _prompt_choice(label: str, default: str, choices: list[str]) -> str:
    choice_list = ", ".join(choice for choice in choices if choice != "")
    while True:
        value = _prompt(f"{label} ({choice_list})", default)
        if value in choices:
            return value
        print("Opcion invalida.")


def _prompt_int(label: str, default: int) -> int:
    while True:
        value = _prompt(label, str(default))
        try:
            return int(value)
        except ValueError:
            print("Ingresa un entero valido.")


def _prompt_float(label: str, default: float) -> float:
    while True:
        value = _prompt(label, str(default))
        try:
            return float(value)
        except ValueError:
            print("Ingresa un numero valido.")


def _prompt_list(label: str, default: list[str]) -> list[str]:
    value = _prompt(label, ", ".join(default))
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def load_template(name: str) -> dict[str, Any]:
    if name not in TEMPLATES:
        raise KeyError(name)
    return deepcopy(TEMPLATES[name])
