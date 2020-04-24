import itertools
import os
import subprocess
import sys


def log(message):
    print(message, file=sys.stderr, flush=True)


class UserError(Exception):
    def __init__(self, message, *args):
        super().__init__(message.format(*args))


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


def move_to_dest(source_dir, dest_dir, base_name):
    move_dest = find_unused_name(os.path.join(dest_dir, base_name))

    log(f'Moving final file to {move_dest} ...')

    os.rename(source_dir, move_dest)
