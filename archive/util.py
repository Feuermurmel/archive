import itertools
import contextlib
import os
import sys
import subprocess
import tempfile


def log(message):
    print(message, file=sys.stderr, flush=True)


class UserError(Exception):
    def __init__(self, message, *args):
        super().__init__(message.format(*args))


def _find_unused_name(base_path):
    base_path, base_name = os.path.split(base_path)
    base_name, ext = os.path.splitext(base_name)

    for i in itertools.count(1):
        if i == 1:
            base_name_count = base_name
        else:
            base_name_count = '{}-{}'.format(base_name, i)

        name = base_name_count + ext
        path = os.path.join(base_path, name)

        if not os.path.exists(path):
            return path


def temp_dir_in_dest_dir(dest_dir):
    return tempfile.TemporaryDirectory(prefix='archive.', dir=dest_dir, suffix='.tmp')


def move_to_dest(source_path, dest_dir, dest_name):
    move_dest = _find_unused_name(os.path.join(dest_dir, dest_name))

    log(f'Moving final file to {move_dest} ...')

    os.rename(source_path, move_dest)


@contextlib.contextmanager
def mounted_disk_image(image_path, mount_root, *, writable=False):
    log(f'Mounting {image_path} ...')

    def iter_args():
        yield 'hdiutil'
        yield 'mount'

        if writable:
            yield '-readonly'

        yield '-nobrowse'
        yield '-mountroot'
        yield mount_root
        yield image_path

    # Blindly accepting any license agreement.
    subprocess.check_output(
        [*iter_args()],
        input='Y\n',
        encoding='utf-8',
        capture_output=False)

    try:
        yield
    finally:
        log('Unmounting image ...')

        for i in os.listdir(mount_root):
            mount_path = os.path.join(mount_root, i)

            # So we won't get confused if unmounting a partition also
            # unmounts other partitions.
            if os.path.exists(mount_path):
                subprocess.check_call(['hdiutil', 'detach', mount_path])
