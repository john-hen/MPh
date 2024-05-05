from .client         import Client
from .server         import Server
from collections.abc import Callable
from threading       import Thread
from logging         import Logger
from types           import TracebackType


client: Client | None
server: Server | None
thread: Thread | None
system: str
log:    Logger


def start(
    cores:   int = None,
    version: str = None,
    port:    int = 0,
) -> Client: ...


exit_code: int
exit_function: Callable[[int | None], None]
exception_handler: Callable[
    [type[BaseException], BaseException, TracebackType | None], None
]


def exit_hook(code: int = None): ...


def exception_hook(
    exc_type:      type[BaseException],
    exc_value:     BaseException,
    exc_traceback: TracebackType | None,
): ...


def cleanup(): ...
