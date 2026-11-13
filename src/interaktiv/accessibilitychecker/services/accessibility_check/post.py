from AccessControl import Unauthorized
from interaktiv.accessibilitychecker import logger
from interaktiv.accessibilitychecker.blocks import get_block_ids
from interaktiv.accessibilitychecker.blocks import get_blocks
from interaktiv.accessibilitychecker.criteria import CRITERIA
from interaktiv.accessibilitychecker.prompt import construct_prompt
from interaktiv.accessibilitychecker.results import format_result
from interaktiv.accessibilitychecker.results import RESPONSE_FORMAT
from interaktiv.aiclient.client import AIClient
from interaktiv.aiclient.interfaces import IAIClient
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from typing import Any
from zope.component import getUtility

import json


class PostAccessibilityCheck(Service):
    def reply(self) -> list[dict[str, Any]] | dict[str, Any]:
        # RunAICheck isn't bound to the workflow, so also require edit rights
        # in the current state
        if not api.user.has_permission("Modify portal content", obj=self.context):
            raise Unauthorized()

        ai_client: AIClient = getUtility(IAIClient)

        language = json_body(self.request).get("language")
        available_languages = api.portal.get_registry_record(
            "plone.available_languages"
        )

        if language not in available_languages:
            language = api.portal.get_current_language(context=self.context)

        blocks = get_blocks(self.context)
        prompt = construct_prompt(self.context, blocks, language)

        response = ai_client.call(
            prompt,
            response_format=RESPONSE_FORMAT,
            # only route to providers that support structured output
            extra_body={"provider": {"require_parameters": True}},
        )

        if not response:
            logger.error("No response from the AI")
            return self.reply_no_content(status=502)

        try:
            answers = json.loads(response)["results"]
        except (ValueError, KeyError, TypeError):
            logger.error(f"Invalid AI response: {response!r}")
            return self.reply_no_content(status=502)

        block_ids = get_block_ids(blocks)

        return [
            format_result(criterion, answers, block_ids, language)
            for criterion in CRITERIA
        ]
