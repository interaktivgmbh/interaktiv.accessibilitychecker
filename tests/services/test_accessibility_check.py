from collections.abc import Callable
from collections.abc import Iterator
from interaktiv.accessibilitychecker.criteria import CRITERIA
from interaktiv.aiclient.client import AIClient
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.dexterity.content import DexterityContent
from unittest import mock

import json
import pytest
import requests
import transaction


@pytest.fixture
def page(functional_portal) -> DexterityContent:
    setRoles(functional_portal, TEST_USER_ID, ["Manager"])

    for role in ("Editor", "Contributor", "Reviewer"):
        api.user.create(
            email=f"{role.lower()}@example.org",
            username=role.lower(),
            password=TEST_USER_PASSWORD,
            roles=(role,),
        )

    page = api.content.create(
        container=functional_portal, type="Document", id="page", title="Page"
    )

    page.blocks = {"text": {"@type": "slate"}}
    page.blocks_layout = {"items": ["text"]}

    api.user.create(
        email="author@example.org", username="author", password=TEST_USER_PASSWORD
    )
    api.user.grant_roles(username="author", obj=page, roles=["Editor"])
    transaction.commit()

    return page


@pytest.fixture
def session(request_factory, page) -> Callable[..., requests.Session]:
    def factory(username: str | None = None) -> requests.Session:
        if username is None:
            return request_factory()
        return request_factory(basic_auth=(username, TEST_USER_PASSWORD))

    return factory


@pytest.fixture
def ai_response(make_answer) -> Iterator[mock.MagicMock]:
    answers = [make_answer(c.id, "pass", None) for c in CRITERIA]

    with mock.patch.object(
        AIClient, "call", return_value=json.dumps({"results": answers})
    ) as call:
        yield call


def test_editor_gets_one_result_per_criterion(session, ai_response):
    response = session("editor").post("/page/@accessibility-check", json={})

    assert response.status_code == 200
    assert [r["criterion"] for r in response.json()] == [c.id for c in CRITERIA]


@pytest.mark.parametrize("username", [None, "contributor", "reviewer"])
def test_without_edit_permission(session, ai_response, username):
    response = session(username).post("/page/@accessibility-check", json={})

    assert response.status_code == 401
    ai_response.assert_not_called()


@pytest.mark.parametrize(
    "content", [None, "not json", '{"foo": []}'], ids=["none", "invalid", "no-results"]
)
def test_invalid_ai_response(session, content):
    with mock.patch.object(AIClient, "call", return_value=content):
        response = session("editor").post("/page/@accessibility-check", json={})

    assert response.status_code == 502
    assert response.content == b""


def test_invalid_language_falls_back(functional_portal, session, ai_response):
    api.portal.set_registry_record("plone.default_language", "de")
    api.portal.set_registry_record("plone.available_languages", ["de", "en"])
    transaction.commit()

    response = session("editor").post(
        "/page/@accessibility-check", json={"language": "xx"}
    )

    assert response.json()[0]["title"] == "Alternativtext passt zum Bild"


@pytest.mark.parametrize(
    "username, expected", [("author", True), ("contributor", False)]
)
def test_ai_check_action(session, username, expected):
    actions = session(username).get("/page/@actions").json()
    ids = [action["id"] for action in actions.get("object_accessibility_checker", [])]

    assert ("ai_check" in ids) is expected
