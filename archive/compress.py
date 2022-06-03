import contextlib
import os
import subprocess
from pathlib import Path

from archive.util import log, temp_dir_in_dest_dir


@contextlib.contextmanager
def _open_dir(name, parent_fd=None):
    fd = os.open(name, os.O_RDONLY, dir_fd=parent_fd)

    try:
        yield fd
    finally:
        os.close(fd)


def _merge_directory_into_fn(src_fd, dest_fd):
    for i in os.scandir(src_fd):
        if i.is_dir(follow_symlinks=False):
            with _open_dir(i.name, src_fd) as other_child_fd, \
                    _open_dir(i.name, dest_fd) as dest_child_fd:
                _merge_directory_into_fn(other_child_fd, dest_child_fd)
        else:
            os.rename(i.name, i.name, src_dir_fd=src_fd, dst_dir_fd=dest_fd)


def apply_compression(path: Path):
    log(f'Applying file system compression...')

    with temp_dir_in_dest_dir(path.parent) as temp_dir:
        copy_dest = temp_dir / 'copy'

        subprocess.check_call(['ditto', '--hfsCompression', path, copy_dest])

        if copy_dest.is_dir() and not copy_dest.is_symlink():
            log(f'Moving compressed files into {path}...')

            with _open_dir(path) as dest_fd, _open_dir(copy_dest) as copy_fd:
                _merge_directory_into_fn(copy_fd, dest_fd)
        else:
            log(f'Moving compressed file to {path}...')

            os.rename(copy_dest, path)
