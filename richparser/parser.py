from __future__ import annotations

from .utilities import *

class ParseText:
    def __init__(self) -> None:
        self.text: str = ""
        self.parsed: str = ""

    def open_tag(self, tag: str, attrs: dict[str, str | None]) -> str:
        a = attrs_to_str(attrs)
        if tag in SELF_CLOSING or tag == VOID_INPUT:
            return f"<{tag}{a}/>"
        return f"<{tag}{a}>"

    def close_tag(self, tag: str) -> str:
        if tag in SELF_CLOSING or tag == VOID_INPUT:
            return ""
        return f"</{tag}>"

    def tree_parse(
        self,
        token: str,
        tokens: list[str],
        i: int,
    ) -> tuple[str, int]:
        tag, attrs, inline_text = split_token(token)
        allowed = TREE_RULES.get(tag, ())

        # If the token itself carries text (e.g. "li:some text"), treat it as
        # the leading text node so child elements can still follow it.
        items: list[str] = [inline_text] if inline_text else []
        caption: str | None = None
        summary: str | None = None

        while i < len(tokens):
            t = tokens[i]

            # A leading "-" is an explicit break: stop consuming into this tree.
            # The token is left in place (with "-" stripped) for the outer loop.
            if t.startswith("-"):
                tokens[i] = t[1:]   # strip the marker so callers parse it normally
                break

            t_tag_raw = t.split("&")[0].split(":")[0]
            t_tag = TAG_ALIASES.get(t_tag_raw, t_tag_raw)

            if t_tag not in allowed:
                break

            if t_tag in TREE_TAGS:
                html, i = self.tree_parse(t, tokens, i + 1)

                if t_tag == "figcaption":
                    caption = html
                elif t_tag == "summary":
                    summary = html
                else:
                    items.append(html)
                continue

            c_tag, c_attrs, c_text = split_token(t)
            html = f"{self.open_tag(c_tag, c_attrs)}{c_text or ''}{self.close_tag(c_tag)}"

            if c_tag == "figcaption":
                caption = html
            elif c_tag == "summary":
                summary = html
            else:
                items.append(html)

            i += 1

        if caption:
            items.append(caption)
        if summary:
            items.insert(0, summary)

        result = f"{self.open_tag(tag, attrs)}{''.join(items)}{self.close_tag(tag)}"
        return result, i

    def _parse_inner(self, tokens: list[str], i: int) -> tuple[str, int]:
        tok = tokens[i]
        tag, attrs, text = split_token(tok)

        open_ = self.open_tag(tag, attrs)
        close_ = self.close_tag(tag)

        if tag in TREE_TAGS:
            return self.tree_parse(tok, tokens, i + 1)

        if text is not None:
            return f"{open_}{text}{close_}", i + 1
        
        if i + 1 < len(tokens):
            inner, next_i = self._parse_inner(tokens, i + 1)
            return f"{open_}{inner}{close_}", next_i

        return open_, i + 1

    def parser(self) -> None:
        tokens = self.tokenize()
        i = 0
        while i < len(tokens):
            html, i = self._parse_inner(tokens, i)
            self.parsed += html

    def tokenize(self) -> list[str]:
        import re
        parts = re.split(r"([_\-])", self.text)
        tokens: list[str] = []
        sep = "_"
        for part in parts:
            if part in ("_", "-"):
                sep = part
            elif part:
                tokens.append(("-" + part) if sep == "-" else part)
                sep = "_"
        return tokens

    def get_text(self, text: str) -> str:
        self.text = text
        self.parsed = ""
        self.parser()
        return self.parsed

__all__ = ["ParseText"]