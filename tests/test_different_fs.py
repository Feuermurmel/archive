import os
import subprocess
import zipfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory

from archive.util import mounted_disk_image
from tests.conftest_utils import create_dmg


@pytest.fixture
def different_fs(tmp_path_factory: TempPathFactory) -> Iterator[Path]:
    temp_dir = tmp_path_factory.mktemp("different_fs")
    dmg_path = temp_dir / "image.dmg"
    mount_root = temp_dir / "mount_root"

    # Empty directory to create the disk image from.
    empty_dir = temp_dir / "empty"
    os.mkdir(empty_dir)

    partition_name = "image"
    create_dmg(dmg_path, empty_dir, partition_name)

    with mounted_disk_image(dmg_path, mount_root):
        yield mount_root / partition_name


def test_extract_on_non_root_fs(different_fs: Path) -> None:
    archive_path = different_fs / "test.zip"

    with zipfile.ZipFile(archive_path, mode="w") as zip:
        zip.writestr("foo", "foo")
        zip.writestr("bar", "bar")

    # Try to extract the archive.
    subprocess.check_call(["archive", "-e", str(archive_path)])

    assert (different_fs / "test").is_dir()


def test_archive_on_non_root_fs(different_fs: Path) -> None:
    dir_path = different_fs / "test"

    dir_path.mkdir()
    (dir_path / "foo").write_text("foo")

    # Try to create the archive.
    subprocess.check_call(["archive", str(dir_path)])

    assert (different_fs / "test.zip").is_file()
