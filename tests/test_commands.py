"""Проверки команд на виртуальном дереве."""

import contextlib
import io
import unittest

from src.commands import CommandError, ShellSession
from src.vfs import VFS


class CommandTests(unittest.TestCase):
    """Проверить навигацию, поиск и сообщения об ошибках."""

    def setUp(self):
        """Создать небольшое дерево непосредственно в памяти."""
        vfs = VFS()
        vfs.directories.update({"/home", "/home/user", "/home/user/docs"})
        vfs.files["/home/user/docs/note.txt"] = "aGVsbG8="
        vfs.files["/home/user/.hidden"] = ""
        self.session = ShellSession(vfs)

    def capture(self, command, arguments):
        """Получить текст команды без терминала."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.session.execute(command, arguments)
        return output.getvalue()

    def test_cd_and_ls(self):
        """cd меняет каталог, ls показывает его содержимое."""
        self.capture("cd", ["/home/user"])
        self.assertEqual(self.session.cwd, "/home/user")
        self.assertEqual(self.capture("ls", []), "docs\n")
        self.assertIn(".hidden", self.capture("ls", ["-a"]))
        self.assertIn("drw-r--r--", self.capture("ls", ["-l"]))
        self.capture("cd", ["docs"])
        self.assertEqual(self.session.cwd, "/home/user/docs")

    def test_find_echo_who(self):
        """Поиск по имени и текстовые команды дают ожидаемый вывод."""
        self.assertEqual(
            self.capture("find", ["/home", "-name", "*.txt"]),
            "/home/user/docs/note.txt\n",
        )
        self.assertEqual(self.capture("echo", ["hello", "world"]),
                         "hello world\n")
        self.assertTrue(self.capture("who", []).strip())

    def test_invalid_paths_and_options(self):
        """Ошибочные пути и флаги не меняют сеанс."""
        with self.assertRaises(CommandError):
            self.session.execute("cd", ["/missing"])
        with self.assertRaises(CommandError):
            self.session.execute("ls", ["-z"])
        with self.assertRaises(CommandError):
            self.session.execute("find", ["/missing"])
        self.assertEqual(self.session.cwd, "/")


if __name__ == "__main__":
    unittest.main()
