import sys
import os
import tempfile
import subprocess
import itertools

from archive.util import UserError


def log(msg, *args):
    if args:
        msg = msg.format(*args)

    print(msg, file=sys.stderr)


def command(*args, input=None):
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    res, _ = proc.communicate(input)

    if proc.returncode:
        args_str = ' '.join(args)

        raise UserError(f'Command failed: {args_str}')

    return res


def find_unused_name(base_path):
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


def move_to_dest(source_path, dest_dir, dest_base_name):
    move_dest = find_unused_name(os.path.join(dest_dir, dest_base_name))

    print(source_path, '->', move_dest)

    os.rename(source_path, move_dest)


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

        move_to_dest(archive_file, os.path.dirname(path),
                     os.path.basename(path) + '.zip')

    log('Moving original file to the trash ...')

    command('trash', path)

    log('Done.')
