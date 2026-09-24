"""Создать временные ZIP-образы для демонстрационных BAT-сценариев."""

import argparse
import zipfile


FIXTURES = {
    "minimal": {"motd": "Добро пожаловать!\n"},
    "files": {
        "motd": "Образ с файлами\n",
        "readme.txt": "Текстовый файл\n",
        "bin.dat": b"\x00\xff\x01",
    },
    "deep": {
        "motd": "Глубокий образ\n",
        "home/user/projects/notes.txt": "Три уровня каталогов\n",
        "home/user/projects/data.bin": b"\x00\x10\xff",
    },
}


def make_fixture(kind, path):
    """Записать выбранный пример для локального запуска."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in FIXTURES[kind].items():
            data = content.encode("utf-8") if isinstance(content, str) else content
            archive.writestr(name, data)


def main():
    """Прочитать вид образа и целевой путь из CLI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=FIXTURES)
    parser.add_argument("path")
    args = parser.parse_args()
    make_fixture(args.kind, args.path)


if __name__ == "__main__":
    main()
