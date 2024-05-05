from .model          import Model
from jpype           import JClass
from pathlib         import Path
from collections.abc import Iterator
from logging         import Logger


log:     Logger
modules: dict[str, str]


class Client:

    version: str
    standalone: bool
    port: int | None
    host: str
    java: JClass

    def __init__(
        self,
        cores:   int | None = None,
        version: str | None = None,
        port:    int | None = None,
        host:    str        = ...,
    ): ...

    def __contains__(self, item: str | Model) -> bool: ...

    def __iter__(self) -> Iterator[Model]: ...

    def __truediv__(self, name: str): ...

    @property
    def cores(self) -> int: ...

    def models(self) -> list[Model]: ...

    def names(self) -> list[str]: ...

    def files(self) -> list[Path]: ...

    def modules(self) -> list[str]: ...

    def load(self, file: Path) -> Model: ...

    def caching(self, state: bool | None = None) -> None | bool: ...

    def create(self, name: str | None = None) -> Model: ...

    def remove(self, model: Model): ...

    def clear(self): ...

    def connect(self, port: int, host: str = ...): ...

    def disconnect(self): ...
