import os
import subprocess
import tempfile

from archive.util import move_to_dest, log


def archive_file(path, destination_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_file = os.path.join(temp_dir, 'archive.zip')

        log('Creating archive ...')

        def iter_args():
            yield 'ditto'
            yield '-c'
            yield '-k'

            if os.path.isdir(path):
                yield '--keepParent'

            yield '--noqtn'
            yield path
            yield archive_file

        subprocess.check_call([*iter_args()])

        move_to_dest(archive_file, destination_dir, os.path.basename(path) + '.zip')

    log('Moving original file to the trash ...')

    subprocess.check_call(['trash', path])

    log('Done.')
