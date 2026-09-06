from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _review_evidence_schema_fallback import validate_review_evidence_without_jsonschema
from _util import repo_root

try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover
    jsonschema = None


class ReviewEvidenceSchemaError(RuntimeError):
    pass


def review_evidence_schema_path() -> Path:
    return repo_root() / "scripts" / "sc" / "schemas" / "review-evidence.v1.schema.json"


def load_review_evidence_schema() -> dict[str, Any]:
    path = review_evidence_schema_path()
    if not path.exists():
        raise ReviewEvidenceSchemaError(f"RGE-SCHEMA-000 canonical schema not found: {path}")
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewEvidenceSchemaError(f"RGE-SCHEMA-000 invalid canonical schema JSON: {exc}") from exc
    if not isinstance(schema, dict):
        raise ReviewEvidenceSchemaError("RGE-SCHEMA-000 canonical schema must be an object")
    if jsonschema is not None:
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except jsonschema.SchemaError as exc:
            raise ReviewEvidenceSchemaError(f"RGE-SCHEMA-000 invalid canonical schema contract: {exc.message}") from exc
    return schema


def _format_path(path: list[Any]) -> str:
    value = "$"
    for part in path:
        value += f"[{part}]" if isinstance(part, int) else f".{part}"
    return value


def _primary_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    if jsonschema is None:
        return []
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"RGE-SCHEMA-001 {_format_path(list(error.path))}: {error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda item: (_format_path(list(item.path)), item.message))
    ]


def validate_review_evidence_payload(payload: Any, *, force_fallback: bool = False) -> None:
    schema = load_review_evidence_schema()
    errors = validate_review_evidence_without_jsonschema(payload)
    if not errors and not force_fallback and jsonschema is not None and isinstance(payload, dict):
        errors.extend(_primary_errors(payload, schema))
    if errors:
        details = "\n".join(f"- {item}" for item in errors[:20])
        raise ReviewEvidenceSchemaError(f"review evidence schema validation failed:\n{details}")
