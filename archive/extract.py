import functools
import os
import shutil
import subprocess
import tempfile

from archive.util import UserError, move_to_dest, log, mounted_disk_image


def is_alias(path):
    return int(subprocess.check_output(['GetFileInfo', '-aa', path], encoding='utf-8')) == 1


def is_invisible(path):
    return int(subprocess.check_output(['GetFileInfo', '-av', path], encoding='utf-8')) == 1


def copy_compress_to_dest(source_path, dest_dir, dest_name):
    log(f'Applying filesystem compression ...')

    with tempfile.TemporaryDirectory(prefix='archive.', dir=dest_dir) as temp_dir:
        copy_dest = os.path.join(temp_dir, 'copy')

        subprocess.check_call(['ditto', '--hfsCompression', source_path, copy_dest])
        move_to_dest(copy_dest, dest_dir, dest_name)


def extract_disk_image(image_path, destination_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        mount_root = os.path.join(temp_dir, 'mounts')
        copy_root = os.path.join(temp_dir, 'extracted')

        os.mkdir(mount_root)
        os.mkdir(copy_root)

        with mounted_disk_image(image_path, mount_root):
            partitions = os.listdir(mount_root)

            for i in partitions:
                mount_path = os.path.join(mount_root, i)
                copy_path = os.path.join(copy_root, i)

                os.mkdir(copy_path)

                log(f'Copying partition {i} ...')

                for j in os.listdir(mount_path):
                    member_path = os.path.join(mount_path, j)

                    # Ignore all the crap put into the average disk image.
                    if j.startswith('.') or os.path.islink(member_path) or is_alias(member_path) or is_invisible(member_path):
                        log(f'Skipping {j}')
                    else:
                        subprocess.check_call(
                            ['ditto', member_path, os.path.join(copy_path, j)])

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

            copy_compress_to_dest(move_source, destination_dir, move_dest_name)


def prepare_contents(extract_dir):
    def fn():
        for i in os.listdir(extract_dir):
            if i.startswith('.'):
                log(f'Removing {i}')

                path = os.path.join(extract_dir, i)

                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
            else:
                yield i

    return list(fn())


def extract_zip_archive(archive_path, destination_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extracted')

        os.mkdir(extract_dir)

        log(f'Extracting file {archive_path} ...')

        subprocess.check_call(
            ['ditto', '-x', '-k', archive_path, extract_dir])

        contents = prepare_contents(extract_dir)

        if len(contents) > 1:
            move_source = extract_dir
            move_dest_name, _ = os.path.splitext(os.path.basename(archive_path))
        else:
            content, = contents

            move_source = os.path.join(extract_dir, content)
            move_dest_name = content

        copy_compress_to_dest(move_source, destination_dir, move_dest_name)


def extract_tar_archive(archive_path, destination_dir, *, compression_arg=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extracted')

        os.mkdir(extract_dir)

        log(f'Extracting file {archive_path} ...')

        def iter_args():
            yield from ['tar', '-x', '-C', extract_dir, '-f', archive_path]

            if compression_arg is not None:
                yield compression_arg

        subprocess.check_call([*iter_args()])

        contents = prepare_contents(extract_dir)

        if len(contents) > 1:
            move_source = extract_dir
            move_dest_name, _ = os.path.splitext(os.path.basename(archive_path))
        else:
            content, = contents

            move_source = os.path.join(extract_dir, content)
            move_dest_name = content

        copy_compress_to_dest(move_source, destination_dir, move_dest_name)


def get_handler(path):
    handlers = [
        ('.zip .jar', extract_zip_archive),
        ('.tar', extract_tar_archive),
        ('.tar.gz .tgz', functools.partial(extract_tar_archive, compression_arg='-z')),
        ('.iso .dmg .sparseimage .sparsebundle', extract_disk_image)]

    for extensions, handler in handlers:
        for extension in extensions.split():
            if path.endswith(extension):
                return handler

    raise UserError(f'Unknown file type: {path}')


def extract_file(path, destination_dir):
    get_handler(path)(path, destination_dir)

    log('Moving original file to the trash ...')

    subprocess.check_call(['trash', path])

    log('Done.')
