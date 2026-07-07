from collections.abc import Callable
from typing import TypeAlias

import ast
import pytest

from flake8_frozen_collections.plugin import Plugin

_PLUGIN_RUN_T: TypeAlias = Callable[
    [str], list[tuple[int, int, str]],
]


@pytest.fixture
def plugin_run() -> _PLUGIN_RUN_T:
    """Fixture for easy run plugin."""

    def _plugin_run(code: str) -> list[tuple[int, int, str]]:
        plugin = Plugin(ast.parse(code))
        return [
            (viol[0], viol[1], viol[2])
            for viol in plugin.run()
        ]

    return _plugin_run


@pytest.mark.parametrize(
    ('code', 'expected'),
    [
        ('x = {"a": 1}', [(1, 4, 'FCS100 use frozendict instead of dict')]),
        ('x = {}', [(1, 4, 'FCS100 use frozendict instead of dict')]),
        ('x = dict(a=1)', [(1, 4, 'FCS100 use frozendict instead of dict')]),
        ('x = {k: v for k, v in items}', [(1, 4, 'FCS100 use frozendict instead of dict')]),
        ('x: dict[str, int] = {}', [
            (1, 3, 'FCS100 use frozendict instead of dict'),
            (1, 20, 'FCS100 use frozendict instead of dict'),
        ]),
        ('def f(x: dict) -> dict: ...', [
            (1, 9, 'FCS100 use frozendict instead of dict'),
            (1, 18, 'FCS100 use frozendict instead of dict'),
        ]),
        ('isinstance(x, dict)', [(1, 0, 'FCS100 use frozendict instead of dict')]),
        ('isinstance(x, (dict, list))', [(1, 0, 'FCS100 use frozendict instead of dict')]),
    ],
)
def test_dict_violations(
    plugin_run: _PLUGIN_RUN_T,
    code: str,
    expected: list[tuple[int, int, str]],
) -> None:
    assert plugin_run(code) == expected


@pytest.mark.parametrize(
    ('code', 'expected'),
    [
        ('x = {1, 2}', [(1, 4, 'FCS200 use frozenset instead of set')]),
        ('x = set()', [(1, 4, 'FCS200 use frozenset instead of set')]),
        ('x = set([1, 2])', [(1, 4, 'FCS200 use frozenset instead of set')]),
        ('x = {i for i in range(3)}', [(1, 4, 'FCS200 use frozenset instead of set')]),
        ('x: set[int] = set()', [
            (1, 3, 'FCS200 use frozenset instead of set'),
            (1, 14, 'FCS200 use frozenset instead of set'),
        ]),
        ('isinstance(x, set)', [(1, 0, 'FCS200 use frozenset instead of set')]),
    ],
)
def test_set_violations(
    plugin_run: _PLUGIN_RUN_T,
    code: str,
    expected: list[tuple[int, int, str]],
) -> None:
    assert plugin_run(code) == expected


@pytest.mark.parametrize(
    'code',
    [
        'from frozendict import frozendict',
        'x = frozendict({"a": 1})',
        'x = frozenset({1, 2})',
        'x = frozenset([1, 2])',
        'x: frozenset[int] = frozenset()',
    ],
)
def test_allowed_code(plugin_run: _PLUGIN_RUN_T, code: str) -> None:
    assert plugin_run(code) == []


def test_union_argument_type(plugin_run):
    code = '\n'.join([
        'def foo(val: dict | None):',
        '    pass',
    ])
    assert plugin_run(code) == [(1, 13, 'FCS100 use frozendict instead of dict')]


def test_optional_argument_type(plugin_run):
    code = '\n'.join([
        'def foo(val: Optional[dict]):',
        '    pass',
    ])
    assert plugin_run(code) == [(1, 22, 'FCS100 use frozendict instead of dict')]


def test_union_return_type(plugin_run):
    code = '\n'.join([
        'def foo() -> dict | None:',
        '    pass',
    ])
    assert plugin_run(code) == [(1, 13, 'FCS100 use frozendict instead of dict')]


def test_optional_return_type(plugin_run):
    code = '\n'.join([
        'def foo() -> Optional[dict]:',
        '    pass',
    ])
    assert plugin_run(code) == [(1, 22, 'FCS100 use frozendict instead of dict')]
