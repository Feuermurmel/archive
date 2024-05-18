import os
import subprocess

from archive.util import log
from archive.util import move_to_dest
from archive.util import temp_dir_in_dest_dir


def archive_files(path, dest_dir):
    with temp_dir_in_dest_dir(dest_dir) as temp_dir:
        archive_file = temp_dir / "archive.zip"

        log("Creating archive...")

        def iter_args():
            yield "ditto"
            yield "-c"
            yield "-k"

            if os.path.isdir(path):
                yield "--keepParent"

            yield "--noqtn"
            yield path
            yield archive_file

        subprocess.check_call([*iter_args()])

        move_to_dest(archive_file, dest_dir, os.path.basename(path) + ".zip")

    log("Moving original file to the trash...")

    subprocess.check_call(["trash", path])
