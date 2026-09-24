"""Проверки настройки и стартового сценария."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from src.config import ConfigError, load_settings
from src.shell import CommandError, run_startup


class ConfigTests(unittest.TestCase):
    """Проверить приоритеты и ошибки файлов."""

    def test_yaml_overrides_cli(self):
        """Пути в YAML имеют приоритет и отсчитываются от файла."""
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.yaml"
            config.write_text(
                'vfs_path: "from_file.zip" # comment\n'
                "startup_script: 'run file.start' # comment\n",
                encoding="utf-8",
            )
            settings = load_settings([
                "--vfs", "from_cli.zip",
                "--startup", "from_cli.start",
                "--config", str(config),
            ])
            self.assertEqual(settings.vfs_path, config.parent / "from_file.zip")
            self.assertEqual(
                settings.startup_script,
                config.parent / "run file.start",
            )

    def test_missing_config(self):
        """Отсутствующий файл конфигурации вызывает явную ошибку."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.yaml"
            with self.assertRaises(ConfigError):
                load_settings(["--config", str(path)])

    def test_startup_dialogue_and_error(self):
        """Сценарий показывает команды и сообщает номер ошибочной строки."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.start"
            path.write_text(
                "# comment\necho 'two words'\nwrong\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(CommandError, ":3:"):
                    run_startup(path)
            self.assertIn("two words", output.getvalue())
            self.assertNotIn("# comment", output.getvalue())


if __name__ == "__main__":
    unittest.main()
