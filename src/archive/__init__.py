import argparse
import sys
from enum import Enum
from pathlib import Path

from archive.archive import archive_files
from archive.compress import apply_compression
from archive.extract import extract_archive
from archive.util import UserError
from archive.util import log


class Mode(Enum):
    archive = "archive"
    extract = "extract"
    compress = "compress"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-e",
        "--extract",
        action="store_const",
        dest="mode",
        const=Mode.extract,
        default=Mode.archive,
        help="Try to extract an archive instead of creating one.",
    )

    parser.add_argument(
        "--fs-compress",
        action="store_const",
        dest="mode",
        const=Mode.compress,
        help="Apply APFS file compression to the files.",
    )

    parser.add_argument(
        "-d",
        "--destination-dir",
        type=Path,
        help="Place the archive file or extracted files into this directory. "
        "Default to the directory that contains the source.",
    )

    parser.add_argument("source_paths", nargs="+", type=Path)

    return parser.parse_args()


def main(mode: Mode, source_paths: list[Path], destination_dir: Path | None) -> None:
    for i in source_paths:
        source_path = i.resolve()

        if destination_dir is None:
            destination_dir = source_path.parent

        if mode is Mode.extract:
            extract_archive(str(source_path), str(destination_dir))
        elif mode is Mode.archive:
            archive_files(str(source_path), str(destination_dir))
        else:
            assert mode is Mode.compress

            apply_compression(source_path)

    log("Done.")


def entry_point() -> None:
    try:
        main(**vars(parse_args()))
    except KeyboardInterrupt:
        log("Operation interrupted.")
        sys.exit(1)
    except UserError as e:
        log(f"error: {e}")
        sys.exit(2)
