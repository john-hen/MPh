"""Lints the code for style errors and runs the static type checker."""

from subprocess import run
from pathlib import Path

root = Path(__file__).resolve().parent.parent

print('Linting the code for style errors.')
run(['flake8'], cwd=root, check=True)


print('Checking that type stubs are complete.')
run(
    ['stubtest', '--mypy-config-file', 'pyproject.toml', 'mph'],
    cwd=root, check=True,
)

print('Checking that type annotations are correct.')
run(['mypy'], cwd=root, check=True)
