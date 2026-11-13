from interaktiv.accessibilitychecker import logger
from interaktiv.accessibilitychecker.blocks import Block
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.content import DexterityContent
from plone.restapi.deserializer.utils import path2uid
from plone.restapi.serializer.utils import RESOLVEUID_RE

import base64
import cairosvg


def get_images(context: DexterityContent, blocks: list[Block]) -> list[tuple[str, str]]:
    images: list[tuple[str, str]] = []

    for block in blocks:
        if block.get("@type") == "image" and block.get("url"):
            data_url = get_image_data_url(context, block["url"])

            if data_url:
                images.append((block["id"], data_url))

        images.extend(get_images(context, block.get("blocks", [])))
    return images


def get_image_data_url(context: DexterityContent, url: str) -> str | None:
    match = RESOLVEUID_RE.match(path2uid(context, url))

    if match is None:
        return None

    image = uuidToObject(match.group(1))

    if image is None or getattr(image, "image", None) is None:
        return None

    # OpenRouter doesn't accept svgs, and Plone can't scale them
    if image.image.contentType == "image/svg+xml":
        try:
            png = cairosvg.svg2png(bytestring=image.image.data, output_width=800)
        except Exception:
            logger.warning(f"Could not convert svg: {image.absolute_url()}")
            return None

        return to_data_url(png, "image/png")

    scale = image.restrictedTraverse("@@images").scale("image", scale="large")

    if scale is None:
        return None

    return to_data_url(scale.data.data, scale.data.contentType)


def to_data_url(data: bytes, content_type: str) -> str:
    return f"data:{content_type};base64,{base64.b64encode(data).decode()}"
