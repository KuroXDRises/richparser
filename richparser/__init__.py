from .parser import ParseText

def parse(text:str)->str:
    return ParseText().get_text(text)

__all__ = ["parse"]