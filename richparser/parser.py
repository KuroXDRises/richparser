from __future__ import annotations
from .utilities import *


class ParseText:

    def __init__(self):
        self.text = ""
        self.parsed = ""

    def tokenize(self):
        return [t for t in self.text.split("_") if t]

    def open_tag(self, tag, attrs):
        a = attrs_to_str(attrs)
        if tag in SELF_CLOSING or tag == VOID_INPUT:
            return f"<{tag}{a}/>"
        return f"<{tag}{a}>"

    def close_tag(self, tag):
        if tag in SELF_CLOSING or tag == VOID_INPUT:
            return ""
        return f"</{tag}>"

    def tree_parse(self, token, tokens, i):
        tag, attrs, _ = split_token(token)
        allowed = TREE_RULES.get(tag, ())

        items = []
        caption = None

        while i < len(tokens):
            t = tokens[i]
            t_tag_raw = t.split("&")[0].split(":")[0]
            t_tag = TAG_ALIASES.get(t_tag_raw, t_tag_raw)

            if t_tag not in allowed:
                break

            if t_tag in TREE_TAGS:
                html, i = self.tree_parse(t, tokens, i + 1)

                if t_tag == "figcaption":
                    caption = html
                else:
                    items.append(html)
                continue

            c_tag, c_attrs, c_text = split_token(t)

            html = f"{self.open_tag(c_tag, c_attrs)}{c_text or ''}{self.close_tag(c_tag)}"

            if c_tag == "figcaption":
                caption = html
            else:
                items.append(html)

            i += 1

        if caption:
            items.append(caption)

        result = f"{self.open_tag(tag, attrs)}{''.join(items)}{self.close_tag(tag)}"

        return result, i

    def parser(self):
        tokens = self.tokenize()
        i = 0

        while i < len(tokens):
            tok = tokens[i]
            tag_raw = tok.split("&")[0].split(":")[0]
            tag = TAG_ALIASES.get(tag_raw, tag_raw)

            if tag in TREE_TAGS:
                html, i = self.tree_parse(tok, tokens, i + 1)
                self.parsed += html
                continue

            tag, attrs, text = split_token(tok)

            open_ = self.open_tag(tag, attrs)
            close_ = self.close_tag(tag)

            if text is None:
                if i + 1 < len(tokens):
                    next_tok = tokens[i + 1]

                    next_tag_raw = next_tok.split("&")[0].split(":")[0]
                    next_tag = TAG_ALIASES.get(next_tag_raw, next_tag_raw)

                    if next_tag in TREE_TAGS:
                        inner_html, i = self.tree_parse(next_tok, tokens, i + 2)
                    else:
                        n_tag, n_attrs, n_text = split_token(next_tok)
                        inner_html = f"{self.open_tag(n_tag, n_attrs)}{n_text or ''}{self.close_tag(n_tag)}"
                        i += 2
                    self.parsed += f"{open_}{inner_html}{close_}"
                    continue
                else:
                    self.parsed += open_
            else:
                self.parsed += f"{open_}{text}{close_}"

            i += 1


    def get_text(self, text:str)->str:
        self.text = text
        self.parsed = ""
        self.parser()
        return self.parsed