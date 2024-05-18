# archive

Command line tool for macOS which makes it easy to extract and create archived files.

`archive <path>` creates a ZIP archive (using `ditto` to include macOS-specific meta-data) at `<path>.zip` and moves the original file or directory to the macOS trash.

`archive -e <path>.<ext>` extracts the archive to a file or directory at `<path>` and moves the original file or directory to the macOS trash. Extracting is supported for some archive types supported by `ditto` and `tar` and some disk image types supported by `hdiutil`. This includes ZIP and (optionally compressed TAR) archives and ISO- and DMG-images (including their sparse variants).

While extracting, all the uninteresting top-level files are ignored. This includes invisible files and alias files. If only one top-level object remains, it is placed directly in the destination directory instead of creating a containing directory. This is especially useful to extract downloaded disk images for software distributions where the disk image only contains the application plus an alias to the _Applications_ directory. Extracting such a disk image which result in only the Application being placed in the destination directory.

While extracting, it also safeguards against archive files which contain more than item in the root directory. For those archives, an additional directory with the name of the archive is created to contain those items.


## Development Setup

```
pre-commit install
make venv
```
