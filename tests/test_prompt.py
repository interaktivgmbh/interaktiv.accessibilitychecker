from interaktiv.accessibilitychecker.prompt import construct_prompt
from plone.dexterity.content import DexterityContent
from unittest import mock


def test_images_follow_their_block_label():
    context = DexterityContent(title="Page", description="")
    images = [
        ("image-1", "data:image/png;base64,AAA"),
        ("image-2", "data:image/png;base64,BBB"),
    ]

    with mock.patch(
        "interaktiv.accessibilitychecker.prompt.get_images", return_value=images
    ):
        prompt = construct_prompt(context, [], "en")

    assert prompt[1]["content"][1:] == [
        {"type": "text", "text": "Image of block image-1:"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAA"}},
        {"type": "text", "text": "Image of block image-2:"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,BBB"}},
    ]
