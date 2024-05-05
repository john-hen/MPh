from pathlib import Path
from logging import Logger


system:  str
log:     Logger
options: dict[str, str | bool | float]


def option(
    name:  str = None,
    value: str | bool | float | None = None,
) -> None | str | bool | float: ...


def location() -> Path: ...


def load(file: Path = None): ...


def save(file: Path = None): ...
