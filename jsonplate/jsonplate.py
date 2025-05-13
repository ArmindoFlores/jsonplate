from .lexer import Lexer
from .parser import Parser


def parse(text: str, **kwargs):
    lexer = Lexer(text)
    parser = Parser(lexer.tokenize())
    return parser.parse()
