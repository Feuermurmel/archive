import itertools
import pathlib
import sys


def log(message):
    print(message, file=sys.stderr, flush=True)


class UserError(Exception):
    def __init__(self, message, *args):
        super().__init__(message.format(*args))


def find_unused_name(path: pathlib.Path):
    """
    Find and return an unused path in the same directory and same extension
    as the given path, but maybe with a number added to the base name.
    """

    for i in itertools.count(1):
        if i == 1:
            new_name = path.stem
        else:
            new_name = f'{path.stem}-{i}'

        new_path = path.with_name(new_name + path.suffix)

        if not new_path.exists() and not new_path.is_symlink():
            return new_path
