import os
import tempfile

from archive.util import command, move_to_dest, log


def archive_file(path):
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_file = os.path.join(temp_dir, 'archive.zip')

        log('Creating archive ...')

        def args():
            yield 'ditto'
            yield '-c'
            yield '-k'

            if os.path.isdir(path):
                yield '--keepParent'

            yield '--noqtn'
            yield path
            yield archive_file

        command(*args())

        move_to_dest(archive_file, os.path.dirname(path), os.path.basename(path) + '.zip')

    log('Moving original file to the trash ...')

    command('trash', path)

    log('Done.')
