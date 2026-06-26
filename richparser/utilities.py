import re

SELF_CLOSING = {
    "img", "video", "audio", "hr", "br",
    "tg-map", "tg-emoji", "tg-time",
}

VOID_INPUT = "input"

TREE_RULES = {
    "ul": ("li",),
    "ol": ("li",),
    "table": ("tr",),
    "tr": ("td", "th"),

    "tg-collage": ("img", "video", "figcaption"),
    "tg-slideshow": ("img", "video", "figcaption"),

    "figure": ("img", "video", "audio", "tg-collage", "tg-slideshow", "figcaption"),
}

TREE_TAGS = tuple(TREE_RULES.keys())

TAG_ALIASES = {
    "spoiler": "tg-spoiler",
    "math": "tg-math",
    "bmath": "tg-math-block",
    "map": "tg-map",
    "emoji": "tg-emoji",
    "time": "tg-time",
    "collage": "tg-collage",
    "slideshow": "tg-slideshow",
    "thinking": "tg-thinking"
}

def parse_attrs(raw: str) -> dict:
    attrs = {}
    for part in raw.split("&"):
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            attrs[TAG_ALIASES.get(k, k)] = v
        else:
            attrs[TAG_ALIASES.get(part, part)] = None
    return attrs


def attrs_to_str(attrs: dict) -> str:
    if not attrs:
        return ""
    parts = []
    for k, v in attrs.items():
        if v is None:
            parts.append(k)
        else:
            parts.append(f'{k}="{v}"')
    return " " + " ".join(parts)


def split_token(token: str):
    colon = re.search(r":(?!//)", token)

    if colon:
        head = token[:colon.start()]
        text = token[colon.end():] or None
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
    "TAG_ALIASES", "TREE_RULES", "VOID_INPUT",
    "SELF_CLOSING", "TREE_TAGS", "attrs_to_str", "split_token"
]