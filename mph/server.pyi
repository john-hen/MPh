from subprocess import Popen
from logging    import Logger
from typing     import Literal


log: Logger


class Server:

    version: str
    cores:   int | None
    port:    int | None
    process: Popen[str]

    def __init__(
        self,
        cores:     int = None,
        version:   str = None,
        port:      int = None,
        multi:     bool | Literal['on', 'off'] | None = None,
        timeout:   int = 60,
        arguments: list[str] = None,
    ): ...

    def running(self) -> bool: ...

    def stop(self, timeout: int = 20): ...


def parse_port(line: str) -> str | None: ...
