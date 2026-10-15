"""Makes a made-up 'download' called sample/installer.bin and a damaged copy sample/installer-damaged.bin.

Run: python make_sample.py
The files hold only repeated text. The damaged copy is the same file with its last 10 bytes cut off,
like a download that stopped early.
"""
import sys
from pathlib import Path

DATA = (b"made-up installer, not a real program\n" * 2000)


def make(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    good = folder / "installer.bin"
    good.write_bytes(DATA)
    (folder / "installer-damaged.bin").write_bytes(DATA[:-10])
    return good


if __name__ == "__main__":
    make(Path(__file__).resolve().parent / "sample")
    print("Made sample/installer.bin and sample/installer-damaged.bin")
    sys.exit(0)
