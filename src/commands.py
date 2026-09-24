"""Команды оболочки и текущий каталог виртуальной системы."""

import fnmatch
import getpass
import os
import posixpath
import socket

from src.vfs import VFS


class CommandError(Exception):
    """Ошибка команды, видимая пользователю."""


def os_user():
    """Получить учетное имя ОС с запасным способом для фонового запуска."""
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()


class ShellSession:
    """Хранить VFS и текущий каталог на протяжении диалога."""

    def __init__(self, vfs=None):
        """Создать сеанс в виртуальном корне."""
        self.vfs = vfs if vfs is not None else VFS()
        self.cwd = "/"

    def resolve(self, text):
        """Преобразовать путь оболочки в абсолютный путь VFS."""
        if text == "~":
            return "/"
        if text.startswith("~/"):
            text = text[1:]
        source = text if text.startswith("/") else posixpath.join(self.cwd, text)
        return posixpath.normpath(source)

    def require_exists(self, path):
        """Сообщить об отсутствии виртуального пути."""
        if path not in self.vfs.directories and path not in self.vfs.files:
            raise CommandError(f"нет такого файла или каталога: {path}")

    def children(self, directory):
        """Вернуть имена непосредственных потомков каталога."""
        prefix = directory.rstrip("/") + "/"
        paths = self.vfs.directories | self.vfs.files.keys()
        return sorted(
            path[len(prefix):] for path in paths
            if path != directory
            and path.startswith(prefix)
            and "/" not in path[len(prefix):]
        )

    def execute(self, command, arguments):
        """Направить команду ее обработчику и вернуть признак продолжения."""
        if command == "exit":
            if arguments:
                raise CommandError("exit: аргументы не поддерживаются")
            return False
        handlers = {
            "ls": self.ls,
            "cd": self.cd,
            "find": self.find,
            "who": self.who,
            "echo": self.echo,
        }
        if command not in handlers:
            raise CommandError(f"команда не найдена: {command}")
        handlers[command](arguments)
        return True

    def ls(self, arguments):
        """Показать файлы и каталоги; поддержать -a и -l."""
        options, targets = self.split_options(arguments, "al")
        targets = targets or ["."]
        for index, text in enumerate(targets):
            path = self.resolve(text)
            self.require_exists(path)
            if len(targets) != 1:
                print(f"{path}:")
            if path in self.vfs.files:
                self.print_entry(path, posixpath.basename(path), options)
            else:
                names = self.children(path)
                if "a" in options:
                    names = [".", ".."] + names
                for name in names:
                    if name.startswith(".") and "a" not in options:
                        continue
                    child = self.resolve(posixpath.join(path, name))
                    self.print_entry(child, name, options)
            if index != len(targets) - 1:
                print()

    def print_entry(self, path, name, options):
        """Показать краткую или расширенную строку ls."""
        if "l" in options:
            kind = "d" if path in self.vfs.directories else "-"
            size = 0 if kind == "d" else len(self.vfs.read_bytes(path))
            print(f"{kind}rw-r--r-- {size:>8} {name}")
        else:
            print(name)

    def cd(self, arguments):
        """Перейти в существующий каталог VFS."""
        if len(arguments) > 1:
            raise CommandError("cd: требуется не более одного пути")
        path = self.resolve(arguments[0] if arguments else "~")
        self.require_exists(path)
        if path not in self.vfs.directories:
            raise CommandError(f"cd: не каталог: {path}")
        self.cwd = path

    def find(self, arguments):
        """Найти пути рекурсивно, при необходимости по шаблону имени."""
        path_text = "."
        pattern = None
        position = 0
        if arguments and arguments[0] != "-name":
            path_text = arguments[0]
            position = 1
        if arguments[position:]:
            if len(arguments[position:]) != 2:
                raise CommandError("find: используйте [путь] [-name шаблон]")
            if arguments[position] != "-name":
                raise CommandError("find: поддерживается только -name")
            pattern = arguments[position + 1]
        path = self.resolve(path_text)
        self.require_exists(path)
        paths = sorted(self.vfs.directories | self.vfs.files.keys())
        for candidate in paths:
            inside = candidate == path or candidate.startswith(path.rstrip("/") + "/")
            matches = pattern is None or fnmatch.fnmatchcase(
                posixpath.basename(candidate), pattern
            )
            if inside and matches:
                print(candidate)

    def who(self, arguments):
        """Показать реального пользователя и узел текущего сеанса."""
        if arguments:
            raise CommandError("who: аргументы не поддерживаются")
        print(f"{os_user()}  {socket.gethostname()}")

    def echo(self, arguments):
        """Напечатать аргументы; -n подавляет перевод строки."""
        no_newline = bool(arguments and arguments[0] == "-n")
        words = arguments[1:] if no_newline else arguments
        print(" ".join(words), end="" if no_newline else "\n")

    @staticmethod
    def split_options(arguments, allowed):
        """Разделить короткие флаги и пути команды."""
        options = set()
        targets = []
        for argument in arguments:
            if argument.startswith("-") and argument != "-":
                for option in argument[1:]:
                    if option not in allowed:
                        raise CommandError(f"неизвестный флаг: -{option}")
                    options.add(option)
            else:
                targets.append(argument)
        return options, targets
