import dataclasses
from typing import Dict, List, Optional, Union

from .errors import JSONParserError
from .lexer import Token, TokenType


@dataclasses.dataclass(frozen=True)
class JSONVariable:
    name: str

JSONIntermediateArray = List["JSONIntermediateValue"]
JSONIntermediateObject = Dict[Union[str, JSONVariable], "JSONIntermediateValue"]
JSONIntermediateValue = Union[JSONVariable, str, float, int, bool, None, JSONIntermediateArray, JSONIntermediateObject]

class Parser:
    def __init__(self, tokens: List[Token], template_mode: bool = True):
        self.tokens = tokens
        self.length = len(tokens)
        self.index = 0
        self.contents: JSONIntermediateValue = None
        self.template_mode = template_mode

    @staticmethod
    def _expecting_message(token_types: List[TokenType]):
        if len(token_types) == 1:
            return token_types[0]
        elif len(token_types) == 2:
            return "or ".join(token_types)
        return f"one of: {', '.join(token_types)}"

    def consume(self, token_types: List[TokenType], optional: bool = False) -> Optional[Token]:
        if self.index >= self.length:
            if optional:
                return None
            raise JSONParserError(f"Was expecting {self._expecting_message(token_types)}, instead found EOF")
        if self.tokens[self.index].type in token_types:
            self.index += 1
            return self.tokens[self.index-1]
        if optional:
            return None
        raise JSONParserError(f"Was expecting {self._expecting_message(token_types)}, instead found {self.tokens[self.index].type}")

    def parse_json(self) -> JSONIntermediateValue:
        self.consume(["WHITESPACE"], True)
        self.contents = self.parse_value()
        self.consume(["WHITESPACE"], True)
        if self.index < self.length:
            raise JSONParserError(f"Expected EOF, found {self.tokens[self.index]}")
        return self.contents
    
    def parse_value(self) -> JSONIntermediateValue:
        self.consume(["WHITESPACE"], True)
        to_consume = [
            "STRING",
            "NUMBER",
            "OPEN_BRACKET",
            "OPEN_PARENTHESIS",
            "LITERAL",
        ]
        if self.template_mode:
            to_consume.append("KEY")

        consumed = self.consume(to_consume)
        result = None
        if consumed.type == "STRING":
            result = consumed.content[1:-1]
        elif consumed.type == "NUMBER":
            number = float(consumed.content)
            number = int(number) if number.is_integer() else number
            result = number
        elif consumed.type == "OPEN_BRACKET":
            self.index -= 1
            result = self.parse_object()
        elif consumed.type == "OPEN_PARENTHESIS":
            self.index -= 1
            result = self.parse_array()
        elif consumed.type == "LITERAL":
            result = True if consumed.content == "true" else (False if consumed.content == "false" else None)
        elif consumed.type == "KEY":
            result = JSONVariable(consumed.content)

        self.consume(["WHITESPACE"], True)
        return result
    
    def parse_array(self) -> JSONIntermediateArray:
        self.consume(["OPEN_PARENTHESIS"])
        result = []
        while True:
            self.consume(["WHITESPACE"], True)
            end = self.consume(["CLOSE_PARENTHESIS"], True)
            if end is not None:
                self.index -= 1
                break
            result.append(self.parse_value())
            comma = self.consume(["COMMA"], True)
            if comma is None:
                break
        self.consume(["CLOSE_PARENTHESIS"])
        return result
    
    def parse_object(self) -> JSONIntermediateObject:
        self.consume(["OPEN_BRACKET"])
        result = {}
        while True:
            self.consume(["WHITESPACE"], True)
            end = self.consume(["CLOSE_BRACKET"], True)
            if end is not None:
                self.index -= 1
                break
            to_consume = ["STRING"]
            if self.template_mode:
                to_consume.append("KEY")
            consumed = self.consume(to_consume)
            if consumed.type == "STRING":
                key = consumed.content[1:-1]
            else:
                key = JSONVariable(consumed.content)
            self.consume(["WHITESPACE"], True)
            self.consume(["COLON"])
            value = self.parse_value()
            result[key] = value
            comma = self.consume(["COMMA"], True)
            if comma is None:
                break

        self.consume(["CLOSE_BRACKET"])
        return result

    def parse(self, ) -> JSONIntermediateValue:
        self.contents = None
        self.index = 0
        try:
            return self.parse_json()
        except JSONParserError as e:
            raise JSONParserError(*e.args) from None
