import re
from functools import cached_property
from typing import Dict, List, Union

from .errors import JSONError, JSONTemplaterError
from .parser import (JSONIntermediateArray, JSONIntermediateObject,
                     JSONIntermediateValue, JSONVariable)

JSONArray = List["JSONValue"]
JSONObject = Dict[str, "JSONValue"]
JSONValue = Union[str, float, int, bool, None, JSONArray, JSONObject]

class Templater:
    STRING_TEMPLATE_REGEX = re.compile(r"(?<!\\)\{\{\s*([a-zA-Z_]+[a-zA-Z_0-9]*)\s*\}\}")

    def __init__(self, json_value: JSONIntermediateValue):
        self.value = json_value
        self.context = {}

    @cached_property
    def variable_names(self):
        raise NotImplementedError

    def get_template_value(self, key: str):
        value = self.context.get(key, ...)
        if value == ...:
            raise JSONTemplaterError(f"Template variable '{key}' is not defined")
        return value
    
    def format_object(self, value: JSONIntermediateObject) -> JSONObject:
        return {
            str(self.format_value(k)): self.format_value(v) for k, v in value.items()
        }
    
    def format_array(self, value: JSONIntermediateArray) -> JSONArray:
        return [self.format_value(v) for v in value]
    
    def format_string(self, value: str) -> str:
        return self.STRING_TEMPLATE_REGEX.sub(lambda match: f"{self.get_template_value(match.group(1))!s}", value)

    def format_variable(self, value: JSONVariable) -> JSONObject:
        return self.get_template_value(value.name)
    
    def format_value(self, value: JSONIntermediateValue) -> JSONValue:
        if isinstance(value, dict):
            return self.format_object(value)
        if isinstance(value, list):
            return self.format_array(value)
        if isinstance(value, str):
            return self.format_string(value)
        if isinstance(value, JSONVariable):
            return self.format_variable(value)
        return value

    def format(self, **kwargs: JSONValue) -> JSONValue:
        self.context = kwargs
        try:
            return self.format_value(self.value)
        except JSONError as e:
            raise JSONTemplaterError(*e.args) from None