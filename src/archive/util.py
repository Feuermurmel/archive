import contextlib
import itertools
import os
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


class UserError(Exception):
    def __init__(self, message: str, *args: object):
        super().__init__(message.format(*args))


def _find_unused_name(base_path: str) -> str:
    base_path, base_name = os.path.split(base_path)
    base_name, ext = os.path.splitext(base_name)

    for i in itertools.count(1):
        if i == 1:
            base_name_count = base_name
        else:
            base_name_count = "{}-{}".format(base_name, i)

        name = base_name_count + ext
        path = os.path.join(base_path, name)

        if not os.path.exists(path):
            return path

    assert False


@contextlib.contextmanager
def temp_dir_in_dest_dir(dest_dir: str | Path) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(
        prefix="archive.", dir=dest_dir, suffix=".tmp"
    ) as temp_dir:
        yield Path(temp_dir)


def move_to_dest(source_path: Path, dest_dir: str, dest_name: str) -> None:
    move_dest = _find_unused_name(os.path.join(dest_dir, dest_name))

    log(f"Moving final file to {move_dest}...")

    os.rename(source_path, move_dest)


@contextlib.contextmanager
def mounted_disk_image(
    image_path: str | Path, mount_root: str | Path, *, writable: bool = False
) -> Iterator[None]:
    log(f"Mounting {image_path}...")

    def iter_args() -> Iterator[str | Path]:
        yield "hdiutil"
        yield "mount"

        if writable:
            yield "-readonly"

        yield "-nobrowse"
        yield "-mountroot"
        yield mount_root
        yield image_path

    # Blindly accepting any license agreement.
    subprocess.run([*iter_args()], input="Y\n", encoding="utf-8", check=True)

    try:
        yield
    finally:
        log("Unmounting image...")

        for i in os.listdir(mount_root):
            mount_path = os.path.join(mount_root, i)

            # So we won't get confused if unmounting a partition also
            # unmounts other partitions.
            if os.path.exists(mount_path):
                subprocess.check_call(["hdiutil", "detach", mount_path])
