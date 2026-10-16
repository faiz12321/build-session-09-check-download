import contextlib
import hashlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import checkfile
import make_sample

ABC = hashlib.sha256(b"abc").hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "f.bin"
        self.path.write_bytes(b"abc")

    def run_main(self, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = checkfile.main(args)
        return code, buf.getvalue()


class CleanTests(unittest.TestCase):
    def test_accepts_upper_case_spaces_and_prefix(self):
        self.assertEqual(checkfile.clean("  " + ABC.upper() + "\n"), ABC)
        self.assertEqual(checkfile.clean("sha256:" + ABC), ABC)

    def test_refuses_wrong_length_or_characters(self):
        for bad in ["", "abc", ABC[:-1], ABC + "0", "g" * 64, ABC[:32] + " " + ABC[33:]]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    checkfile.clean(bad)


class HashTests(Base):
    def test_known_value(self):
        self.assertEqual(checkfile.file_sha256(self.path), ABC)

    def test_empty_file(self):
        self.path.write_bytes(b"")
        self.assertEqual(checkfile.file_sha256(self.path), hashlib.sha256(b"").hexdigest())

    def test_file_bigger_than_one_chunk(self):
        data = os.urandom(3 * 1024 * 1024 + 17)
        self.path.write_bytes(data)
        self.assertEqual(checkfile.file_sha256(self.path), hashlib.sha256(data).hexdigest())


class MainTests(Base):
    def test_match(self):
        code, out = self.run_main([str(self.path), ABC])
        self.assertEqual(code, 0)
        self.assertIn("MATCH:", out)
        self.assertNotIn("NO MATCH", out)

    def test_one_changed_byte_does_not_match(self):
        self.path.write_bytes(b"abd")
        code, out = self.run_main([str(self.path), ABC])
        self.assertEqual(code, 1)
        self.assertIn("NO MATCH", out)

    def test_truncated_file_does_not_match(self):
        self.path.write_bytes(b"ab")
        self.assertEqual(self.run_main([str(self.path), ABC])[0], 1)

    def test_bad_checksum_is_refused_before_reading(self):
        code, out = self.run_main([str(self.path), "123"])
        self.assertEqual(code, 2)
        self.assertIn("64 characters", out)

    def test_missing_file_and_folder_and_usage(self):
        self.assertEqual(self.run_main([str(Path(self.tmp.name) / "no"), ABC])[0], 2)
        self.assertEqual(self.run_main([self.tmp.name, ABC])[0], 2)
        self.assertEqual(self.run_main([])[0], 2)

    def test_sample_files(self):
        good = make_sample.make(Path(self.tmp.name) / "new-sample")
        want = hashlib.sha256(good.read_bytes()).hexdigest()
        self.assertEqual(self.run_main([str(good), want])[0], 0)
        self.assertEqual(self.run_main([str(good.with_name("installer-damaged.bin")), want])[0], 1)

    def test_file_not_changed(self):
        before = (self.path.read_bytes(), os.stat(self.path).st_mtime_ns)
        self.run_main([str(self.path), ABC])
        self.assertEqual(before, (self.path.read_bytes(), os.stat(self.path).st_mtime_ns))


class SetupSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sample = self.root / 'sample'

    def test_existing_folder_preserves_nested_bytes_and_metadata(self):
        (self.sample / 'nested').mkdir(parents=True)
        keep = self.sample / 'nested' / 'keep.bin'
        keep.write_bytes(b'KEEP')
        before = (keep.read_bytes(), keep.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, (keep.read_bytes(), keep.stat().st_mtime_ns))
        self.assertEqual(sorted(p.relative_to(self.sample).as_posix() for p in self.sample.rglob('*')), ['nested','nested/keep.bin'])

    def test_existing_file_preserved(self):
        self.sample.write_bytes(b'KEEP')
        before = (self.sample.read_bytes(), self.sample.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, (self.sample.read_bytes(), self.sample.stat().st_mtime_ns))

    def test_repeat_setup_preserves_generated_bytes_and_metadata(self):
        make_sample.make(self.sample)
        before = {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.sample.iterdir()}
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.sample.iterdir()})

    def test_cli_refuses_without_replacing(self):
        import shutil, subprocess, sys
        script = self.root / 'make_sample.py'
        shutil.copyfile(Path(__file__).resolve().parent / 'make_sample.py', script)
        self.sample.mkdir()
        keep = self.sample / 'keep'
        keep.write_bytes(b'KEEP')
        result = subprocess.run([sys.executable,str(script)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertIn('Nothing was replaced or deleted',result.stderr)
        self.assertEqual(keep.read_bytes(),b'KEEP')


if __name__ == "__main__":
    unittest.main()
