import ast
from collections.abc import Generator, Iterable
from typing import final

_DICT_ERROR = "FCS100 use frozendict instead of dict"
_SET_ERROR = "FCS200 use frozenset instead of set"
_FROZEN_CONSTRUCTORS = frozenset({"frozendict", "frozenset"})


def _is_dict_type(node: ast.expr) -> bool:
    if isinstance(node, ast.Name) and node.id == "dict":
        return True
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        return node.value.id == "dict"
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
        return node.value.attr == "Dict"
    return False


def _is_set_type(node: ast.expr) -> bool:
    if isinstance(node, ast.Name) and node.id == "set":
        return True
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        return node.value.id == "set"
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
        return node.value.attr == "Set"
    return False


def _iter_isinstance_types(node: ast.expr) -> Iterable[ast.expr]:
    if isinstance(node, ast.Tuple):
        yield from node.elts
    else:
        yield node


def _set_parent_links(node: ast.AST) -> None:
    for child in ast.iter_child_nodes(node):
        setattr(child, "_parent", node)
        _set_parent_links(child)


def _is_type_annotation(node: ast.AST) -> bool:
    parent = getattr(node, "_parent", None)
    if isinstance(parent, ast.arg):
        return parent.annotation is node
    if isinstance(parent, ast.AnnAssign):
        return parent.annotation is node
    if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return parent.returns is node
    if isinstance(parent, ast.BinOp):
        return _is_type_annotation(parent)
    if isinstance(parent, ast.Subscript):
        return _is_type_annotation(parent)
    return False


@final
class FrozenCollectionsVisitor(ast.NodeVisitor):
    """Visitor that forbids mutable dict and set in favor of frozen alternatives."""

    def __init__(self) -> None:
        self.problems: list[tuple[int, int, str]] = []
        self._frozen_ctor_depth = 0

    def visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            setattr(child, "_parent", node)
        super().visit(node)

    def _report(self, node: ast.expr, message: str) -> None:
        self.problems.append((node.lineno, node.col_offset, message))

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in _FROZEN_CONSTRUCTORS:
                self._frozen_ctor_depth += 1
                self.generic_visit(node)
                self._frozen_ctor_depth -= 1
                return
            if node.func.id == "dict":
                self._report(node, _DICT_ERROR)
            elif node.func.id == "set":
                self._report(node, _SET_ERROR)
            elif node.func.id == "isinstance" and len(node.args) >= 2:
                for type_node in _iter_isinstance_types(node.args[1]):
                    if _is_dict_type(type_node):
                        self._report(node, _DICT_ERROR)
                    elif _is_set_type(type_node):
                        self._report(node, _SET_ERROR)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in _FROZEN_CONSTRUCTORS:
                self._frozen_ctor_depth += 1
                self.generic_visit(node)
                self._frozen_ctor_depth -= 1
                return
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "dict":
                    self._report(node, _DICT_ERROR)
                elif node.func.value.id == "set":
                    self._report(node, _SET_ERROR)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        if self._frozen_ctor_depth == 0:
            self._report(node, _DICT_ERROR)
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:
        if self._frozen_ctor_depth == 0:
            self._report(node, _SET_ERROR)
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        if self._frozen_ctor_depth == 0:
            self._report(node, _DICT_ERROR)
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        if self._frozen_ctor_depth == 0:
            self._report(node, _SET_ERROR)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if _is_type_annotation(node):
            if _is_dict_type(node):
                self._report(node, _DICT_ERROR)
            elif _is_set_type(node):
                self._report(node, _SET_ERROR)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        parent = getattr(node, "_parent", None)
        if isinstance(parent, ast.Subscript) and parent.value is node:
            self.generic_visit(node)
            return
        if _is_type_annotation(node):
            if node.id == "dict":
                self._report(node, _DICT_ERROR)
            elif node.id == "set":
                self._report(node, _SET_ERROR)
        self.generic_visit(node)


@final
class Plugin:
    """Flake8 plugin."""

    name = "flake8-frozen-collections"
    version = "0.1.0"

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree
        _set_parent_links(tree)

    def run(self) -> Generator[tuple[int, int, str, type], None, None]:
        visitor = FrozenCollectionsVisitor()
        visitor.visit(self._tree)
        for line, col, message in visitor.problems:
            yield (line, col, message, type(self))
