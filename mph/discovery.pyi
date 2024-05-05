from pathlib import Path
from logging import Logger


log:           Logger
system:        str
architectures: dict[str, list[str]]


def parse(version: str) -> tuple[str, int, int, int, int]: ...


def search_registry() -> list[Path]: ...


def search_disk() -> list[Path]: ...


def lookup_comsol() -> Path: ...


def find_backends() -> list[dict[str, str | int | Path]]: ...


def backend(version: str = None) -> dict[str, str | int | Path]: ...
