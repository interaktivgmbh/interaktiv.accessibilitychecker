from dataclasses import dataclass
from interaktiv.accessibilitychecker import _
from zope.i18nmessageid import Message


@dataclass(frozen=True)
class Criterion:
    id: str
    title: Message
    description: Message
    wcag: str
    ai_note: str = ""  # instructions and hints for the AI


CRITERIA = (
    Criterion(
        id="KI01",
        title=_("Alt text matches the image"),
        description=_(
            "The alternative text accurately describes the essential content "
            "of the image."
        ),
        wcag="1.1.1 Non-text Content",
        ai_note=(
            "Only judge non-empty alternative texts and report the ones that "
            "are wrong, misleading or too vague to describe the image. Image "
            'blocks without an "alt" or with an empty one are rendered as '
            "decorative images and belong to KI02."
        ),
    ),
    Criterion(
        id="KI02",
        title=_("Alt text fits the context"),
        description=_(
            "The alternative text conveys the purpose of the image in the "
            "context of the page."
        ),
        wcag="1.1.1 Non-text Content",
        ai_note=(
            'Image blocks without an "alt" or with an empty one are '
            'rendered with alt="" and marked as decorative. Report them if '
            "the image conveys information the page needs, e.g. a chart, an "
            "informative photo or a linked image. An image with a link (href) "
            "needs an alternative text that describes the link target."
        ),
    ),
    Criterion(
        id="KI03",
        title=_("Link texts are meaningful"),
        description=_(
            "Link texts make the purpose of the link clear, at least in their context."
        ),
        wcag="2.4.4 Link Purpose (In Context)",
        ai_note=(
            "Also report link texts that don't match the link target, judged by "
            "the URL. Internal link targets are stored as resolveuid URLs: that "
            "is expected and not an issue, and their target can't be judged."
        ),
    ),
    Criterion(
        id="KI04",
        title=_("Headings are meaningful"),
        description=_("Headings accurately describe the content of their section."),
        wcag="2.4.6 Headings and Labels",
    ),
    Criterion(
        id="KI05",
        title=_("Content is logically structured"),
        description=_("The order and structure of the content are easy to follow."),
        wcag="1.3.2 Meaningful Sequence",
        ai_note=(
            "Judge the page as a whole in block order. Report the blocks "
            "where the structure breaks, e.g. a section that doesn't fit its "
            "heading."
        ),
    ),
    Criterion(
        id="KI06",
        title=_("Instructions don't rely on visual cues"),
        description=_("Instructions don't refer only to colour, shape or position."),
        wcag="1.3.3 Sensory Characteristics",
    ),
)
