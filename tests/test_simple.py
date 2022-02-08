import shutil
import subprocess

import pytest


def test_round_trip_zip(tmp_path):
    dir_path = tmp_path / 'test'
    archive_path = tmp_path / 'test.zip'

    dir_path.mkdir()

    (dir_path / 'foo').write_text('foo')
    (dir_path / 'bar').write_text('bar')

    # Create an archive from the directory.
    subprocess.check_call(['archive', str(dir_path)])

    assert not dir_path.exists()
    assert archive_path.exists()

    # Extract the created archive again.
    subprocess.check_call(['archive', '-e', str(archive_path)])

    assert not archive_path.exists()
    assert (dir_path / 'foo').read_text() == 'foo'
    assert (dir_path / 'bar').read_text() == 'bar'


def test_dmg(tmp_path):
    src_path = tmp_path / 'src'
    src_path.mkdir()

    (src_path / 'foo').write_text('foo')
    (src_path / 'bar').write_text('bar')

    archive_path = tmp_path / 'image.dmg'
    partition_name = 'Root Partition Name'

    # Create a .dmg image.
    subprocess.check_call(
        ['hdiutil', 'create', '-volname', partition_name, '-srcfolder', str(src_path), '-ov', '-format', 'UDZO', str(archive_path)])

    # Extract the image.
    subprocess.check_call(['archive', '-e', str(archive_path)])

    # Check that the files exist under the right paths.
    assert (tmp_path / partition_name / 'foo').read_text() == 'foo'
    assert (tmp_path / partition_name / 'bar').read_text() == 'bar'


@pytest.mark.parametrize('compressed', [False, True])
def test_tar(tmp_path, compressed):
    src_path = tmp_path / 'src'
    src_path.mkdir()

    (src_path / 'foo').write_text('foo')
    (src_path / 'bar').write_text('bar')

    if compressed:
        archive_path = tmp_path / 'archive.tar.gz'

        # Create a .tar file.
        subprocess.check_call(['tar', '-c', '-j', '-f', str(archive_path), 'src'], cwd=tmp_path)
    else:
        archive_path = tmp_path / 'archive.tar'

        # Create a .tar file.
        subprocess.check_call(['tar', '-c', '-f', str(archive_path), 'src'], cwd=tmp_path)

    shutil.rmtree(src_path)

    # Extract the image.
    subprocess.check_call(['archive', '-e', str(archive_path)])

    # Check that the files exist under the right paths.
    assert (src_path / 'foo').read_text() == 'foo'
    assert (src_path / 'bar').read_text() == 'bar'
