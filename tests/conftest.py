from collections.abc import Callable
from collections.abc import Iterable
from interaktiv.accessibilitychecker.testing import FUNCTIONAL_TESTING
from interaktiv.accessibilitychecker.testing import INTEGRATION_TESTING
from pytest_plone import fixtures_factory
from typing import Any
from zope.i18n.config import COMPILE_MO_FILES_KEY

import os
import pytest


pytest_plugins = ["pytest_plone"]

# the .mo files are gitignored, so Zope has to compile them when it loads the ZCML
os.environ[COMPILE_MO_FILES_KEY] = "1"


globals().update(
    fixtures_factory((
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture
def make_answer() -> Callable[..., dict[str, Any]]:
    def factory(
        criterion: str = "KI01",
        result: str = "fail",
        severity: str | None = "serious",
        blocks: Iterable[tuple[str, str]] = (),
    ) -> dict[str, Any]:
        return {
            "criterion": criterion,
            "result": result,
            "severity": severity,
            "affected_blocks": [
                {"block_id": block_id, "hint": hint} for block_id, hint in blocks
            ],
        }

    return factory
