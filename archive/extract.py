#! /usr/bin/env python3

import sys
import os
import tempfile
import subprocess
import itertools
import shutil

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
    """
    Find and return an unused path in the same directory and same extension
    as the given path, but maybe with a number added to the base name.
    """

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

    log('Moving extracted files to {} ...', move_dest)

    os.rename(source_dir, move_dest)


def is_alias(path):
    return int(command('GetFileInfo', '-aa', path).decode()) == 1


def is_invisible(path):
    return int(command('GetFileInfo', '-av', path).decode()) == 1


def extract_disk_image(image_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        mount_root = os.path.join(temp_dir, 'mounts')
        copy_root = os.path.join(temp_dir, 'extracted')

        os.mkdir(mount_root)
        os.mkdir(copy_root)

        try:
            log('Mounting {} ...', image_path)

            # Blindly accepting any license agreement.
            command('hdiutil', 'mount', '-readonly', '-nobrowse', '-mountroot',
                    mount_root, image_path, input='Y\n'.encode())

            partitions = os.listdir(mount_root)

            for i in partitions:
                mount_path = os.path.join(mount_root, i)
                copy_path = os.path.join(copy_root, i)

                os.mkdir(copy_path)

                log('Copying partition {} ...', i)

                for j in os.listdir(mount_path):
                    member_path = os.path.join(mount_path, j)

                    # Ignore all the crap put into the average disk image.
                    if j.startswith('.') or os.path.islink(
                            member_path) or is_alias(
                            member_path) or is_invisible(member_path):
                        log('Skipping {}', j)
                    else:
                        command('ditto', member_path,
                                os.path.join(copy_path, j))

            log('Moving items to destination folder ...')

            if len(partitions) > 1:
                move_source = copy_root
                _, move_dest_name = os.path.splitext(
                    os.path.basename(image_path))
            else:
                partition, = partitions
                partition_path = os.path.join(copy_root, partition)
                members = os.listdir(partition_path)

                if not members:
                    raise UserError('The partition is empty.')
                elif len(members) > 1:
                    move_source = partition_path
                    move_dest_name = partition
                else:
                    member, = members
                    move_source = os.path.join(partition_path, member)
                    move_dest_name = member

            move_to_dest(move_source, os.path.dirname(image_path),
                         move_dest_name)
        finally:
            log('Unmounting image ...')

            for i in os.listdir(mount_root):
                mount_path = os.path.join(mount_root, i)

                # So we won't get confused if unmounting a partition also
                # unmounts other partitions.
                if os.path.exists(mount_path):
                    command('hdiutil', 'detach', mount_path)


def prepare_contents(extract_dir):
    def fn():
        for i in os.listdir(extract_dir):
            if i.startswith('.'):
                log('Removing {}', i)

                path = os.path.join(extract_dir, i)

                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
            else:
                yield i

    return list(fn())


def extract_zip_archive(archive_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extracted')

        os.mkdir(extract_dir)

        log('Extracting file {} ...', archive_path)

        command('ditto', '-x', '-k', archive_path, extract_dir)

        contents = prepare_contents(extract_dir)

        if len(contents) > 1:
            move_source = extract_dir
            move_dest_name, _ = os.path.splitext(os.path.basename(archive_path))
        else:
            content, = contents

            move_source = os.path.join(extract_dir, content)
            move_dest_name = content

        move_to_dest(move_source, os.path.dirname(archive_path), move_dest_name)


def extract_tar_archive(archive_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extracted')

        os.mkdir(extract_dir)

        log('Extracting file {} ...', archive_path)

        command('tar', '-x', '-C', extract_dir, '-f', archive_path)

        contents = prepare_contents(extract_dir)

        if len(contents) > 1:
            move_source = extract_dir
            move_dest_name, _ = os.path.splitext(os.path.basename(archive_path))
        else:
            content, = contents

            move_source = os.path.join(extract_dir, content)
            move_dest_name = content

        move_to_dest(move_source, os.path.dirname(archive_path), move_dest_name)


# FIXME: Convert all extraction function into classes to reuse common parts by inheritance.
def extract_tar_gz_archive(archive_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        decompress_file = os.path.join(temp_dir, 'decompressed')
        extract_dir = os.path.join(temp_dir, 'extracted')

        log('Decompressing file {} ...', archive_path)

        command('bash', '-c', 'gzip -d < "$0" > "$1"', archive_path,
                decompress_file)

        os.mkdir(extract_dir)

        log('Extracting file ...')

        command('tar', '-x', '-C', extract_dir, '-f', decompress_file)

        contents = prepare_contents(extract_dir)

        if len(contents) > 1:
            move_source = extract_dir
            move_dest_name, _ = os.path.splitext(os.path.basename(archive_path))
        else:
            content, = contents

            move_source = os.path.join(extract_dir, content)
            move_dest_name = content

        move_to_dest(move_source, os.path.dirname(archive_path), move_dest_name)


def get_handler(path):
    handlers = [
        (extract_zip_archive, '.zip .jar'),
        (extract_tar_gz_archive, '.tar.gz .tgz'),
        (extract_disk_image, '.iso .dmg .sparseimage .sparsebundle')]

    for handler, extensions in handlers:
        for extension in extensions.split():
            if path.endswith(extension):
                return handler

    raise UserError(f'Unknown file type: {path}')


def extract_file(path):
    get_handler(path)(path)

    log('Moving original file to the trash ...')

    command('trash', path)

    log('Done.')