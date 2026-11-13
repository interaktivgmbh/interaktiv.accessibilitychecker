from collections.abc import Callable
from interaktiv.accessibilitychecker.images import get_image_data_url
from interaktiv.accessibilitychecker.images import get_images
from io import BytesIO
from PIL import Image
from plone import api
from plone.namedfile.file import NamedBlobImage

import base64
import pytest


# file signatures ("magic numbers") the image data starts with
JPEG_SIGNATURE = b"\xff\xd8"
PNG_SIGNATURE = b"\x89PNG"

SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
    b'<rect width="10" height="10" fill="red"/>'
    b"</svg>"
)


def make_jpeg() -> bytes:
    data = BytesIO()
    Image.new("RGB", (20, 20), "red").save(data, "JPEG")
    return data.getvalue()


@pytest.fixture
def make_image(portal) -> Callable[[bytes, str], str]:
    def factory(data: bytes, filename: str) -> str:
        with api.env.adopt_roles(["Manager"]):
            image = api.content.create(
                container=portal,
                type="Image",
                title=filename,
                image=NamedBlobImage(data=data, filename=filename),
            )
        return f"../resolveuid/{image.UID()}"

    return factory


def decode(data_url: str) -> bytes:
    return base64.b64decode(data_url.split(",", 1)[1])


def test_jpeg(portal, make_image):
    data_url = get_image_data_url(portal, make_image(make_jpeg(), "photo.jpg"))

    assert data_url.startswith("data:image/jpeg;base64,")
    assert decode(data_url).startswith(JPEG_SIGNATURE)


def test_svg_is_converted_to_png(portal, make_image):
    data_url = get_image_data_url(portal, make_image(SVG, "icon.svg"))

    assert data_url.startswith("data:image/png;base64,")
    assert decode(data_url).startswith(PNG_SIGNATURE)


def test_unknown_uid(portal):
    assert get_image_data_url(portal, "../resolveuid/doesnotexist") is None


def test_get_images_includes_nested(portal, make_image):
    url = make_image(make_jpeg(), "photo.jpg")
    blocks = [
        {"id": "text", "@type": "slate"},
        {"id": "empty", "@type": "image"},
        {
            "id": "grid",
            "@type": "gridBlock",
            "blocks": [{"id": "image", "@type": "image", "url": url}],
        },
    ]

    images = get_images(portal, blocks)

    assert [block_id for block_id, _ in images] == ["image"]
