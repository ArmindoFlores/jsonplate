# jsonplate

**jsonplate** is a lightweight, standards-compliant JSON templating engine for Python. It enables dynamic generation of JSON by allowing parameter substitution in values, keys, and strings.


## 🔧 Features

- ✅ **Spec-compliant JSON parser**
- 🧩 **Parameter substitution** in:
  - Object **keys**
  - Object or array **values**
  - String literals via `{{variable}}` syntax
- 🧱 **Reusable templates** via `load_template`
- 🔍 **Variable introspection** via `variable_names`
- 🚫 **No logic blocks, loops, or control flow**


## 📦 Installation

Install via [PyPI](https://pypi.org/project/jsonplate/):

```bash
pip install jsonplate
```

## 🚀 Usage
### Simple Usage

```python
import jsonplate

template = '''
{
    "{{greeting_key}}": "Hello, {{name}}!",
    "values": [1, 2, 3, param_value],
    "config": {
        "enabled": true,
        param_key: 123
    }
}
'''

result = jsonplate.parse(
    template,
    greeting_key="message",
    name="Alice",
    param_value=42,
    param_key="threshold"
)

print(result)
```

**Output:**

```json
{
    "message": "Hello, Alice!",
    "values": [1, 2, 3, 42],
    "config": {
        "enabled": true,
        "threshold": 123
    }
}
```

### Reusable Templates
You can parse once and render multiple times with different parameters:

```python
template = jsonplate.load_template('{"user": "{{name}}"}')

template(name="Alice")  # {"user": "Alice"}
template(name="Bob")    # {"user": "Bob"}
```


## ⚠️ Errors
All parsing and templating errors inherit from the base `jsonplate.errors.JSONError` class.

You may specifically catch:

* `JSONTemplaterError`: raised when template substitution fails

* `JSONParserError`: raised when a syntax violation is encountered

* `JSONLexerError`: raised when tokenization fails
