# Check a downloaded file against its SHA-256 checksum

A small read-only Python tool built step by step. Give it a file and the SHA-256 checksum a publisher lists, and it says whether the file has that SHA-256. It only reads the file.

## Run it

    python make_sample.py                                  # makes made-up files in sample/
    python checkfile.py sample/installer.bin CHECKSUM      # replace CHECKSUM with the 64-character value
    python -m unittest -v                                  # 16 temporary-fixture tests

On Windows, if `python` is not found, use `py`. The lesson shows the exact checksum for the made-up file.

## Files

- `checkfile.py` - the tool
- `make_sample.py` - makes a made-up file and a damaged copy
- `test_checkfile.py` - tests

## Setup safety and evidence

Setup creates only a new sample folder and exclusively writes its fictional byte files. It refuses any existing path rather than resetting or replacing data. Start in a new empty lesson folder. The .bin files contain repeated text, not real installers. Four new setup collision/repeat tests preserve bytes and modification times, including nested unrelated data. The checker is unchanged. Source paths can follow links. Reports expose paths; keep private output private.

Two Windows and two Ubuntu recordings pass all 16 tests. Each pair differs only in unittest time. Displays use the first Windows recording. Version and test-name rendering can differ between platforms. The recorder creates the visible first/final file versions in its unique temporary folder and removes only that folder. Setup itself refuses a repeat run.

## Notes

- A match means the file has the SHA-256 you typed. It does not show the checksum is trustworthy (get it from a source you trust, not only the page that hosts the file), and it does not show the file is safe.
- Only SHA-256 is checked. Python's hashlib documentation says some algorithms, including MD5 and SHA-1, have known hash collision weaknesses (https://docs.python.org/3/library/hashlib.html).
- Capitals, surrounding spaces and a leading `sha256:` are tidied. Anything that is not 64 characters from 0-9 and a-f is refused.
- Microsoft documents a PowerShell command, Get-FileHash (https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash). It was not run for this lesson, so no claim is made that it matches on your PC.
- Tested only on made-up files and small test files, not on real installers or very large files. Python 3.10 (Linux) and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. Not tested on a Windows 10 or 11 desktop.
- The practice files are made up. Educational example, no warranty. Use at your own risk.
- Code is MIT licensed (see LICENSE). Python is a separate project with its own license; this repository does not include it.
