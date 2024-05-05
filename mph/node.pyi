from .model          import Model
from jpype           import JBoolean, JInt, JDouble, JString, JArray, JClass
from numpy.typing    import NDArray, ArrayLike
from numpy           import int_
from pathlib         import Path
from logging         import Logger
from collections.abc import Sequence, Iterator
from typing          import Self, Literal


log: Logger


class Node:

    model:  Model
    groups: dict[str, str]
    alias:  dict[str, str]
    path:   Sequence[str]

    def __init__(self, model: Model, path: str | Node | None = None): ...

    def __eq__(self, other: object) -> bool: ...

    def __truediv__(self, other: str) -> Self: ...

    def __contains__(self, node: Node) -> bool: ...

    def __iter__(self) -> Iterator[Self]: ...

    @property
    def java(self) -> JClass: ...

    def name(self) -> str: ...

    def tag(self) -> str: ...

    def type(self) -> str: ...

    def parent(self) -> Node: ...

    def children(self) -> list[Self]: ...

    def is_root(self) -> bool: ...

    def is_group(self) -> bool: ...

    def exists(self) -> bool: ...

    def comment(self, text: str = None) -> str | None: ...

    def problems(self) -> list[dict[str, str | Node]]: ...

    def rename(self, name: str): ...

    def retag(self, tag: str): ...

    def property(
        self,
        name: str,
        value: Node | bool | float | str | Path | ArrayLike | None = None,
    ) -> None | Node | bool | float | str | Path | ArrayLike: ...

    def properties(self) -> dict[
        str,
        Node | bool | float | str | Path | ArrayLike
    ]: ...

    def select(
        self,
        entity: Literal['all'] | Node | Sequence[int] | int | None,
    ): ...

    def selection(self) -> Node | NDArray[int_] | None: ...

    def toggle(
        self,
        action: Literal[
            'flip',
            'enable', 'disable',
            'on', 'off',
            'activate', 'deactivate'] = ...,
    ): ...

    def run(self): ...

    def import_(self, file: Path): ...

    def create(self, *arguments: list[str], name: str = None): ...

    def remove(self): ...


def parse(string: str) -> tuple[str, ...]: ...


def join(path: tuple[str, ...]) -> str: ...


def escape(name: str) -> str: ...


def unescape(name: str) -> str: ...


def load_patterns() -> dict[str, str]: ...


def feature_path(node: Node) -> Sequence[str]: ...


def tag_pattern(feature_path: Sequence[str]): ...


def cast(
    value: Node | bool | float | str | Path | ArrayLike
) -> JBoolean | JInt | JDouble | JString | JArray: ...


def get(
    java: JClass,
    name: str,
) -> (Node | bool | float | str | Path | ArrayLike): ...


def tree(node: Node | Model, max_depth: int = None): ...


def inspect(java: JClass | Node | Model): ...
