from interaktiv.accessibilitychecker.blocks import get_block_ids
from interaktiv.accessibilitychecker.blocks import sort_blocks


BLOCKS = {
    "text": {"@type": "slate"},
    "grid": {
        "@type": "gridBlock",
        "blocks": {
            "right": {"@type": "image"},
            "left": {"@type": "slate"},
        },
        "blocks_layout": {"items": ["left", "right"]},
    },
    "title": {"@type": "title"},
}
LAYOUT = {"items": ["title", "grid", "text", "deleted"]}


def test_sort_blocks():
    blocks = sort_blocks(BLOCKS, LAYOUT)
    grid = blocks[1]

    assert [block["id"] for block in blocks] == ["title", "grid", "text"]
    assert [block["id"] for block in grid["blocks"]] == ["left", "right"]
    assert "blocks_layout" not in grid


def test_get_block_ids_includes_nested():
    blocks = sort_blocks(BLOCKS, LAYOUT)

    assert get_block_ids(blocks) == {"title", "grid", "left", "right", "text"}
