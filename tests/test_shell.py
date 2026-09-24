"""Проверки первого этапа."""

import contextlib
import io
import unittest

from src.shell import execute_line


class ShellTests(unittest.TestCase):
    """Проверить разбор и поведение команд прототипа."""

    def run_line(self, line):
        """Вернуть результат исполнения и напечатанный текст."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            running = execute_line(line)
        return running, output.getvalue()

    def test_quoted_arguments(self):
        """Кавычки группируют слова в один аргумент."""
        running, output = self.run_line('echo "two words" plain')
        self.assertTrue(running)
        self.assertEqual(output, "two words plain\n")

    def test_bad_quote(self):
        """Ошибка кавычек не прерывает цикл команд."""
        running, output = self.run_line('cd "missing')
        self.assertTrue(running)
        self.assertIn("ошибка разбора", output)

    def test_unknown_and_exit(self):
        """Неизвестная команда сообщает об ошибке; exit завершает цикл."""
        self.assertIn("команда не найдена", self.run_line("bad")[1])
        self.assertFalse(self.run_line("exit")[0])


if __name__ == "__main__":
    unittest.main()
