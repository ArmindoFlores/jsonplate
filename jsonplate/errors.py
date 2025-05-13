class JSONError(Exception):
    pass

class JSONParserError(JSONError):
    pass

class JSONLexerError(JSONError):
    pass

class JSONTemplaterError(JSONError):
    pass
