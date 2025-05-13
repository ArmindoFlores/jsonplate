import dataclasses
import re
from typing import Dict, List, Literal, Tuple


TokenType = Literal["WHITESPACE", "STRING", "OPEN_BRACKET", "CLOSE_BRACKET", "OPEN_PARENTHESIS", "CLOSE_PARENTHESIS", "COMMA", "COLON", "NUMBER", "LITERAL", "KEY"]

@dataclasses.dataclass
class Span:
    start: Tuple[int, int]
    end: Tuple[int, int]

@dataclasses.dataclass
class Token:
    type: TokenType
    span: Span
    content: str

class Lexer:
    WHITESPACE_REGEX = re.compile(r"^[ \n\r\t]+")
    NUMBER_REGEX = re.compile(r"^[-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][-+]?\d+)?")
    OPEN_BRACKET_REGEX = re.compile(r"^\{")
    CLOSE_BRACKET_REGEX = re.compile(r"^\}")
    OPEN_PARENTHESIS_REGEX = re.compile(r"^\[")
    CLOSE_PARENTHESIS_REGEX = re.compile(r"^\]")
    COMMA_REGEX = re.compile(r"^,")
    COLON_REGEX = re.compile(r"^:")
    STRING_REGEX = re.compile(r'^"(?:[^"\\]|(?:\\["\\\/bfnrt])|(?:\\u[0-9a-fA-F]{4}))*"')
    LITERAL_REGEX = re.compile(r"true|false|null")
    KEY_REGEX = re.compile(r"^[a-zA-Z_]+[a-zA-Z_0-9]*")
    
    TOKENS: Dict[TokenType, re.Pattern] = {
        "WHITESPACE": WHITESPACE_REGEX,
        "NUMBER": NUMBER_REGEX,
        "OPEN_BRACKET": OPEN_BRACKET_REGEX,
        "CLOSE_BRACKET": CLOSE_BRACKET_REGEX,
        "OPEN_PARENTHESIS": OPEN_PARENTHESIS_REGEX,
        "CLOSE_PARENTHESIS": CLOSE_PARENTHESIS_REGEX,
        "COMMA": COMMA_REGEX,
        "COLON": COLON_REGEX,
        "STRING": STRING_REGEX,
        "LITERAL": LITERAL_REGEX,
        "KEY": KEY_REGEX,
    }

    def __init__(self, text: str):
        self.text = text

    @staticmethod
    def count_lines_and_columns(text: str):
        if not text:
            return (0, 0)
        
        line_count = 1
        last_newline_pos = -1
        i = 0
        length = len(text)
        
        while i < length:
            if text[i] == "\r" and i + 1 < length and text[i + 1] == "\n":
                line_count += 1
                last_newline_pos = i + 1
                i += 2
            elif text[i] == "\n" or text[i] == "\r":
                line_count += 1
                last_newline_pos = i
                i += 1
            else:
                i += 1
        
        if length > 0 and (text[-1] == "\n" or text[-1] == "\r" or 
                        (text[-1] == "\n" and length >= 2 and text[-2] == "\r")):
            line_count -= 1
            chars_after = 0
        else:
            chars_after = length - (last_newline_pos + 1) if last_newline_pos != -1 else length
        
        return (line_count, chars_after)

    def tokenize(self) -> List[Token]:
        tokens = []

        index = 0
        line = 1
        column = 1
        while index < len(self.text):
            found = False
            for token_type, token_regex in self.TOKENS.items():
                token_match = token_regex.match(self.text[index:])
                if token_match is None:
                    continue
                found = True

                new_lines = 0
                if token_type == "WHITESPACE":
                    new_lines, new_columns = self.count_lines_and_columns(token_match.string)
                else:
                    new_columns = token_match.end()

                tokens.append(
                    Token(
                        type=token_type,
                        span=Span(
                            start=(line, column),
                            end=(line+new_lines, column+new_columns)
                        ),
                        content=self.text[index:index+token_match.end()]
                    )
                )
                line += new_lines
                column += new_columns
                index += token_match.end()
                break
            if not found:
                raise ValueError(f"Can't parse token: {self.text[index]!r}")

        return tokens
