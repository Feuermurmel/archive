import argparse
import os
import pathlib
import sys

from archive.archive import archive_file
from archive.extract import extract_file
from archive.util import log, UserError


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-e',
        '--extract',
        action='store_true',
        help='Try to extract an archive instead of creating one.')

    parser.add_argument(
        '-d',
        '--destination-dir',
        type=pathlib.Path,
        help='Place the archive file or extracted files into this directory. '
             'Default to the directory that contains the source.')

    parser.add_argument(
        'source_paths',
        nargs='+',
        type=pathlib.Path)

    return parser.parse_args()


def main(extract, source_paths, destination_dir):
    for i in source_paths:
        source_path = os.path.normpath(i)

        if destination_dir is None:
            destination_dir = os.path.dirname(source_path)

        if extract:
            extract_file(source_path, str(destination_dir))
        else:
            archive_file(source_path, str(destination_dir))

    log('Done.')


def entry_point():
    try:
        main(**vars(parse_args()))
    except KeyboardInterrupt:
        log('Operation interrupted.')
        sys.exit(1)
    except UserError as e:
        log(f'error: {e}')
        sys.exit(2)
