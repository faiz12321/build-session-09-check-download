"""Makes a made-up 'download' called sample/installer.bin and a damaged copy sample/installer-damaged.bin.

Run only in a new empty lesson folder: python make_sample.py
Setup refuses an existing sample path and exclusively creates new files.
The files hold only repeated text. The damaged copy is the same file with its last 10 bytes cut off,
like a download that stopped early.
"""
import sys
import stat
from pathlib import Path

DATA = (b"made-up installer, not a real program\n" * 2000)


def make(folder):
    folder = Path(folder).absolute()
    if '..' in folder.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for parent in reversed(folder.parents):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Linked/reparse-point parents are unsupported.')
    folder.mkdir(parents=True)
    good = folder / "installer.bin"
    with good.open("xb") as handle:
        handle.write(DATA)
    with (folder / "installer-damaged.bin").open("xb") as handle:
        handle.write(DATA[:-10])
    return good


if __name__ == "__main__":
    try:
        make(Path(__file__).absolute().parent / "sample")
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    print("Made sample/installer.bin and sample/installer-damaged.bin")
    sys.exit(0)
