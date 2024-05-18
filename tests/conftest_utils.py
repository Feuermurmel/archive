import subprocess
from pathlib import Path


def create_dmg(dmg_path: Path, src_dir: Path, partition_name: str) -> None:
    subprocess.check_call(
        [
            "hdiutil",
            "create",
            "-volname",
            partition_name,
            "-srcfolder",
            f"{src_dir}",
            "-ov",
            "-format",
            "UDRW",
            f"{dmg_path}",
        ]
    )
