from interaktiv.accessibilitychecker.blocks import Block
from interaktiv.accessibilitychecker.criteria import CRITERIA
from interaktiv.accessibilitychecker.images import get_images
from interaktiv.aiclient.types import Prompt
from plone.dexterity.content import DexterityContent
from typing import Any

import json


SYSTEM_PROMPT = """\
You review the content of a web page for accessibility issues. You support
editors: you point out possible issues and explain why they matter, but you
never suggest a fix or a rewritten text. The editors decide themselves.

## The page data

You get the page title, the page description and the page's blocks as JSON,
in the order they are rendered. Every block has an "id" (its UUID) and an
"@type". Blocks can contain nested blocks in "blocks", in rendered order too.
Text blocks of type "slate" store their content as a tree in "value".

A block of type "title" renders the page title as the main heading (H1), a
block of type "description" renders the page description. Their values are
in the page data, not in the block. Findings about the title or description
belong to the UUID of that block. Without a title block, the page has no H1.

Images of image blocks follow the JSON, each labelled with its block UUID.

## Criteria

Check every one of these criteria:

{criteria}

## Results

Return exactly one result per criterion, also for criteria that pass.

- "result": "pass" if there is no issue, "fail" if there is one, and
  "incomplete" if you can't judge it reliably, e.g. because an image is
  missing. If a criterion doesn't apply to the page at all, it passes.
- "affected_blocks": one entry per block with an issue, each block only
  once. Only use UUIDs from the page data. Empty for "pass".
  - "block_id": the UUID of the block. Use null only if the issue doesn't
    belong to any block, e.g. it concerns the page as a whole. If an issue
    spans several blocks, add one entry per block instead.
  - "hint": one or two short sentences that explain why this block doesn't
    meet the criterion, referring to its concrete content. Only about this
    block. No fixes and no suggested wording. Write it in this language:
    {language}.
- "severity": how much the issue affects users, null for "pass".
  - "critical": the content is unusable or wrong for affected users
  - "serious": important information is lost or misleading
  - "moderate": the content is understandable, but only with effort
  - "minor": a small issue that hardly affects understanding
"""


def format_criteria() -> str:
    return "\n".join(
        f"- {criterion.id}: {criterion.title} (WCAG {criterion.wcag}) - "
        f"{criterion.description} "
        f"{criterion.ai_note}".strip()
        for criterion in CRITERIA
    )


def construct_prompt(
    context: DexterityContent, blocks: list[Block], language: str
) -> Prompt:
    system_prompt = SYSTEM_PROMPT.format(criteria=format_criteria(), language=language)

    page = {
        "title": context.title,
        "description": context.description,
        "blocks": blocks,
    }
    content: list[dict[str, Any]] = [
        {"type": "text", "text": json.dumps(page, ensure_ascii=False)}
    ]

    for block_id, data_url in get_images(context, blocks):
        content.append({"type": "text", "text": f"Image of block {block_id}:"})
        content.append({"type": "image_url", "image_url": {"url": data_url}})

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]
