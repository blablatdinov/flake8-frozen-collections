# flake8-frozen-collections

Flake8-плагин, который запрещает использование изменяемых `dict` и `set` и требует `frozendict` и `frozenset`.

## Установка

```bash
pip install flake8-frozen-collections
```

## Использование

```bash
flake8 your_project/
```

## Коды ошибок

| Код | Описание |
|-----|----------|
| FCS100 | Используйте `frozendict` вместо `dict` |
| FCS200 | Используйте `frozenset` вместо `set` |

## Что проверяется

- литералы `{...}` и `{key: value}`
- вызовы `dict(...)` и `set(...)`
- dict/set comprehensions
- аннотации типов `dict[...]`, `set[...]`, `dict`, `set`
- проверки `isinstance(..., dict)` и `isinstance(..., set)`

## Пример

```python
# Плохо
mapping: dict[str, int] = {"a": 1}
tags: set[str] = {"x", "y"}

# Хорошо
from frozendict import frozendict

mapping = frozendict({"a": 1})
tags = frozenset({"x", "y"})
```
