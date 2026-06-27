import re

SELF_CLOSING: set[str] = {
    "img", "video", "audio", "hr", "br",
    "tg-map", "tg-emoji", "tg-time",
}

VOID_INPUT: str = "input"

_INLINE: tuple[str, ...] = (
    "input", "span", "b", "i", "s", "u", "a", "code",
    "img", "br", "tg-spoiler", "tg-math", "tg-emoji", "tg-time",
)

TREE_RULES: dict[str, tuple[str, ...]] = {
    "ul":      ("li",),
    "ol":      ("li",),
    "li":      _INLINE + ("ul", "ol", "p", "pre", "blockquote", "figure"),
    "table":   ("tr",),
    "tr":      ("td", "th"),
    "td":      _INLINE + ("ul", "ol", "p", "figure"),
    "th":      _INLINE + ("ul", "ol", "p", "figure"),

    "tg-collage":   ("img", "video", "figcaption"),
    "tg-slideshow": ("img", "video", "figcaption"),

    "figure":  ("img", "video", "audio", "tg-collage", "tg-slideshow", "figcaption"),

    "details": ("summary",
                "p", "span", "b", "i", "s", "u", "a", "code", "pre",
                "blockquote", "br", "hr", "img",
                "ul", "ol", "table", "figure",
                "tg-spoiler", "tg-math", "tg-math-block",
                "tg-thinking", "tg-map", "tg-emoji", "tg-time"),
}


TREE_TAGS: tuple[str, ...] = tuple(TREE_RULES.keys())


TAG_ALIASES: dict[str, str] = {
    "spoiler":    "tg-spoiler",
    "math":       "tg-math",
    "bmath":      "tg-math-block",
    "map":        "tg-map",
    "emoji":      "tg-emoji",
    "time":       "tg-time",
    "collage":    "tg-collage",
    "slideshow":  "tg-slideshow",
    "thinking":   "tg-thinking",
}



def parse_attrs(raw: str) -> dict[str, str | None]:
    attrs: dict[str, str | None] = {}
    for part in raw.split("&"):
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            attrs[TAG_ALIASES.get(k, k)] = v
        else:
            attrs[TAG_ALIASES.get(part, part)] = None
    return attrs


def attrs_to_str(attrs: dict[str, str | None]) -> str:
    if not attrs:
        return ""
    parts: list[str] = []
    for k, v in attrs.items():
        parts.append(k if v is None else f'{k}="{v}"')
    return " " + " ".join(parts)


def split_token(token: str) -> tuple[str, dict[str, str | None], str | None]:
    colon = re.search(r":(?!//)", token)

    if colon:
        head = token[:colon.start()]
        text: str | None = token[colon.end():] or None
    else:
        head = token
        text = None

    if "&" in head:
        tag_raw, attr_raw = head.split("&", 1)
        attrs = parse_attrs(attr_raw)
    else:
        tag_raw = head
        attrs = {}

    tag = TAG_ALIASES.get(tag_raw, tag_raw)
    return tag, attrs, text

__all__ = [
    "TAG_ALIASES", "TREE_RULES", "VOID_INPUT","parse_attrs",
    "SELF_CLOSING", "TREE_TAGS", "attrs_to_str", "split_token"
]