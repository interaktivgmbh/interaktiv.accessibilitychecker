from interaktiv.accessibilitychecker.criteria import CRITERIA
from interaktiv.accessibilitychecker.results import format_result
from typing import Any

import pytest


CRITERION = CRITERIA[0]
BLOCK_IDS = {"block-1", "block-2"}


def check(answers: list[dict[str, Any]]) -> dict[str, Any]:
    return format_result(CRITERION, answers, BLOCK_IDS, "en")


def test_pass_ignores_blocks(make_answer):
    result = check([make_answer(result="pass", blocks=[("block-1", "Hint")])])

    assert result["result"] == "pass"
    assert result["affected_blocks"] == []
    assert result["hints"] == {}
    assert result["unassigned_hints"] == []
    assert "severity" not in result


@pytest.mark.parametrize("block_id", [None, "invented"], ids=["null", "invented"])
def test_hint_without_known_block_is_unassigned(make_answer, block_id):
    blocks = [("block-1", "Real"), (block_id, "Unassigned")]
    result = check([make_answer(blocks=blocks)])

    assert result["affected_blocks"] == ["block-1"]
    assert result["hints"] == {"block-1": "Real"}
    assert result["unassigned_hints"] == ["Unassigned"]


def test_duplicate_block_keeps_first_hint(make_answer):
    blocks = [("block-1", "First"), ("block-1", "Second")]
    result = check([make_answer(blocks=blocks)])

    assert result["affected_blocks"] == ["block-1"]
    assert result["hints"] == {"block-1": "First"}


@pytest.mark.parametrize(
    "answers",
    [
        [],
        [{"criterion": "KI01", "result": "maybe"}],
    ],
    ids=["missing", "invalid"],
)
def test_missing_or_invalid_result_is_incomplete(answers):
    assert check(answers)["result"] == "incomplete"


def test_first_answer_wins(make_answer):
    answers = [make_answer(result="pass"), make_answer(result="fail")]

    assert check(answers)["result"] == "pass"


def test_invalid_severity_is_dropped(make_answer):
    result = check([make_answer(severity="catastrophic")])

    assert "severity" not in result
