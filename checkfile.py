"""Check a downloaded file against a published SHA-256 checksum. It only reads the file.

Usage:  python checkfile.py FILE EXPECTED_SHA256
A match is strong evidence the file has the same content as the file the checksum was made from.
It is not an absolute guarantee, and it does not show who made the file or that it is safe.
"""
import hashlib
import stat
from pathlib import Path

def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path





import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def clean(expected):
    """Tidy a pasted checksum. Raise ValueError if it is not 64 hex characters."""
    text = expected.strip().lower()
    if text.startswith("sha256:"):
        text = text[7:].strip()
    if not HEX64.match(text):
        raise ValueError("The expected checksum must be 64 characters from 0-9 and a-f (SHA-256). "
                         f"Yours has {len(text)} characters.")
    return text


def file_sha256(path):
    digest = hashlib.sha256()
    with open(safe_input(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv):
    if len(argv) != 2:
        print("Usage: python checkfile.py FILE EXPECTED_SHA256")
        return 2
    try:
        want = clean(argv[1])
        got = file_sha256(argv[0])
    except ValueError as error:
        print(error)
        return 2
    except FileNotFoundError:
        print(f"Could not find {argv[0]}")
        return 2
    except OSError as error:
        print(f"Could not read {argv[0]}: {error.strerror or error}")
        return 2
    print(f"File:     {argv[0]}")
    print(f"Expected: {want}")
    print(f"Actual:   {got}")
    if got == want:
        print("MATCH: the file has the SHA-256 you gave.")
        return 0
    print("NO MATCH: the file does not have the SHA-256 you gave. It may be damaged, incomplete or a different file. Do not use it until you know which.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
