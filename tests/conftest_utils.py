import subprocess


def create_dmg(dmg_path, src_dir, partition_name):
    subprocess.check_call(
        ['hdiutil', 'create', '-volname', partition_name, '-srcfolder', f'{src_dir}', '-ov', '-format', 'UDRW', f'{dmg_path}'])
