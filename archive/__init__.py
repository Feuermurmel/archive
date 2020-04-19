import argparse
import os
import pathlib
import sys

from archive.compress import archive_file
from archive.extract import extract_file
from archive.util import log, UserError


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-e',
        '--extract',
        action='store_true')

    parser.add_argument(
        'source_paths',
        nargs='+',
        type=pathlib.Path)

    return parser.parse_args()


def extract_command(source_path):
    extract_file(os.path.normpath(source_path))


def compress_command(source_path):
    archive_file(os.path.normpath(source_path))


def main(extract, source_paths):
    for i in source_paths:
        source_path = os.path.normpath(i)

        if extract:
            extract_file(source_path)
        else:
            archive_file(source_path)


def entry_point():
    try:
        main(**vars(parse_args()))
    except KeyboardInterrupt:
        log('Operation interrupted.')
        sys.exit(1)
    except UserError as e:
        log(f'error: {e}')
        sys.exit(2)
