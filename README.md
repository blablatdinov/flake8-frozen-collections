# flake8-frozen-collections

A Flake8 plugin that prohibits the use of mutable `dict` and `set`, requiring `frozendict` and `frozenset` instead.

## Installation

```bash
pip install flake8-frozen-collections
```

## Usage

```bash
flake8 your_project/
```

## Error Codes

| Code  | Description                              |
|-------|------------------------------------------|
| FCS100 | Use `frozendict` instead of `dict`      |
| FCS200 | Use `frozenset` instead of `set`        |

## What Is Checked

- Literals `{...}` and `{key: value}`
- Calls to `dict(...)` and `set(...)`
- dict/set comprehensions
- Type annotations `dict[...]`, `set[...]`, `dict`, `set`
- Checks `isinstance(..., dict)` and `isinstance(..., set)`

## Example

```python
# Bad
mapping: dict[str, int] = {"a": 1}
tags: set[str] = {"x", "y"}

# Good
from frozendict import frozendict

mapping = frozendict({"a": 1})
tags = frozenset({"x", "y"})
```
