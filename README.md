# AutoGrade

AutoGrade es una base modular para generar, exportar y calificar evaluaciones.

## Primer alcance

- `exam.schema.json` como contrato único del examen
- CLI para generar, validar y calificar
- base lista para sumar OMR, PDF y web UI

## Comandos

```bash
autograde validate path/to/exam.json
autograde generate --template path/to/exam.json --out generated_exam.json
autograde grade --exam path/to/exam.json --responses path/to/responses.json
```

