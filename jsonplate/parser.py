from typing import List

from .lexer import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.length = len(tokens)
        self.index = 0
        self.contents = None

    @staticmethod
    def _expecting_message(token_types: List[TokenType]):
        if len(token_types) == 1:
            return token_types[0]
        elif len(token_types) == 2:
            return "or ".join(token_types)
        return f"one of: {', '.join(token_types)}"

    def consume(self, token_types: List[TokenType], optional = False):
        if self.index >= self.length:
            if optional:
                return None
            raise ValueError(f"Was expecting {self._expecting_message(token_types)}, instead found EOF")
        if self.tokens[self.index].type in token_types:
            self.index += 1
            return self.tokens[self.index-1]
        if optional:
            return None
        raise ValueError(f"Was expecting {self._expecting_message(token_types)}, instead found {self.tokens[self.index].type}")

    def parse_json(self):
        self.consume(["WHITESPACE"], True)
        self.contents = self.parse_value()
        self.consume(["WHITESPACE"], True)
        if self.index < self.length:
            raise ValueError(f"Expected EOF, found {self.tokens[self.index]}")
        return self.contents
    
    def parse_value(self):
        self.consume(["WHITESPACE"], True)
        consumed = self.consume([
            "STRING",
            "NUMBER",
            "OPEN_BRACKET",
            "OPEN_PARENTHESIS",
            "LITERAL",
        ])
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
        self.consume(["WHITESPACE"], True)
        return result
    
    def parse_array(self):
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
    
    def parse_object(self):
        self.consume(["OPEN_BRACKET"])
        result = {}
        while True:
            self.consume(["WHITESPACE"], True)
            end = self.consume(["CLOSE_BRACKET"], True)
            if end is not None:
                self.index -= 1
                break
            key = self.consume(["STRING"]).content[1:-1]
            self.consume(["WHITESPACE"], True)
            self.consume(["COLON"])
            value = self.parse_value()
            result[key] = value
            comma = self.consume(["COMMA"], True)
            if comma is None:
                break

        self.consume(["CLOSE_BRACKET"])
        return result

    def parse(self):
        return self.parse_json()
