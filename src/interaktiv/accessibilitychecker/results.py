from interaktiv.accessibilitychecker.criteria import CRITERIA
from interaktiv.accessibilitychecker.criteria import Criterion
from typing import Any
from zope.i18n import translate


RESULTS = ("pass", "fail", "incomplete")
SEVERITIES = ("minor", "moderate", "serious", "critical")

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "accessibility_check",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion": {
                                "type": "string",
                                "enum": [criterion.id for criterion in CRITERIA],
                            },
                            "result": {
                                "type": "string",
                                "enum": list(RESULTS),
                            },
                            "severity": {
                                "type": ["string", "null"],
                                "enum": [*SEVERITIES, None],
                            },
                            "affected_blocks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "block_id": {"type": ["string", "null"]},
                                        "hint": {"type": "string"},
                                    },
                                    "required": ["block_id", "hint"],
                                    "additionalProperties": False,
                                },
                            },
                        },
                        "required": [
                            "criterion",
                            "result",
                            "severity",
                            "affected_blocks",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["results"],
            "additionalProperties": False,
        },
    },
}


def format_result(
    criterion: Criterion,
    answers: list[dict[str, Any]],
    block_ids: set[str],
    language: str,
) -> dict[str, Any]:
    # the schema can't enforce one result per criterion, so the AI may repeat
    # or skip one: the first answer wins, a missing one becomes "incomplete"
    answer = next((a for a in answers if a.get("criterion") == criterion.id), {})
    status = answer.get("result")

    # fallback in case a provider ignores the strict schema
    if status not in RESULTS:
        status = "incomplete"

    # a passed criterion shows no blocks, even if the AI lists some
    hints: dict[str, str] = {}
    unassigned_hints: list[str] = []
    if status != "pass":
        hints, unassigned_hints = get_hints(answer, block_ids)

    check_result = {
        "criterion": criterion.id,
        "title": translate(criterion.title, target_language=language),
        "description": translate(criterion.description, target_language=language),
        "result": status,
        "affected_blocks": list(hints.keys()),
        "hints": hints,
        "unassigned_hints": unassigned_hints,
    }

    if status != "pass" and answer.get("severity") in SEVERITIES:
        check_result["severity"] = answer["severity"]

    return check_result


def get_hints(
    answer: dict[str, Any], block_ids: set[str]
) -> tuple[dict[str, str], list[str]]:
    # the AI can invent block IDs or repeat one, which would break the block
    # links and React keys in the frontend: keep the first hint per real block
    hints: dict[str, str] = {}
    unassigned_hints: list[str] = []

    for block in answer.get("affected_blocks", []):
        block_id = block.get("block_id")
        hint = block.get("hint", "")

        if block_id not in block_ids:
            unassigned_hints.append(hint)
        elif block_id not in hints:
            hints[block_id] = hint

    return hints, unassigned_hints
