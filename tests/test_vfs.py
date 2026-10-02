"""Проверки ZIP-образа и данных в памяти."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from src.vfs import VFS, VfsError


class VfsTests(unittest.TestCase):
    """Проверить загрузку дерева без распаковки на диск."""

    def test_motd_and_binary(self):
        """Текст motd и двоичные данные восстанавливаются без потерь."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("motd", "Привет!\n")
                archive.writestr("a/b/c.bin", b"\x00\xff")
            vfs = VFS.from_zip(path)
            self.assertEqual(vfs.motd(), "Привет!\n")
            self.assertEqual(vfs.read_bytes("/a/b/c.bin"), b"\x00\xff")
            self.assertIn("/a/b", vfs.directories)
            self.assertFalse((Path(directory) / "a").exists())

    def test_reject_traversal(self):
        """Путь выхода из VFS отклоняется при загрузке."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../escape", "bad")
            with self.assertRaises(VfsError):
                VFS.from_zip(path)


if __name__ == "__main__":
    unittest.main()
