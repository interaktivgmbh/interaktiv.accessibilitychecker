from plone.dexterity.content import DexterityContent
from typing import Any


Block = dict[str, Any]


def get_blocks(context: DexterityContent) -> list[Block]:
    return sort_blocks(context.blocks, context.blocks_layout)


def sort_blocks(
    blocks: dict[str, Block], blocks_layout: dict[str, list[str]]
) -> list[Block]:
    result: list[Block] = []
    for block_id in blocks_layout.get("items", []):
        if block_id not in blocks:
            continue

        block: Block = {"id": block_id, **blocks[block_id]}

        if "blocks" in block:
            block["blocks"] = sort_blocks(
                block["blocks"], block.pop("blocks_layout", {})
            )

        result.append(block)
    return result


def get_block_ids(blocks: list[Block]) -> set[str]:
    block_ids: set[str] = set()

    for block in blocks:
        block_ids.add(block["id"])
        block_ids.update(get_block_ids(block.get("blocks", [])))

    return block_ids
