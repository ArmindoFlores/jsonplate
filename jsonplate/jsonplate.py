from typing import Callable

from .lexer import Lexer
from .parser import Parser
from .templater import JSONValue, Templater


def parse(text: str, **kwargs) -> JSONValue:
    lexer = Lexer(text)
    parser = Parser(lexer.tokenize())
    templater = Templater(parser.parse())
    return templater.format(**kwargs)

def parse_static(text: str) -> JSONValue:
    lexer = Lexer(text)
    parser = Parser(lexer.tokenize(), template_mode=False)
    return parser.parse()

def load_template(text: str) -> Callable[..., JSONValue]:
    lexer = Lexer(text)
    parser = Parser(lexer.tokenize(), template_mode=True)
    templater = Templater(parser.parse())

    def render(**kwargs) -> JSONValue:
        return templater.format(**kwargs)

    return render
