import subprocess


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
