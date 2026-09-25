"""Интерактивная оболочка с настройками и стартовым сценарием."""

import getpass
import shlex
import socket

from src.config import ConfigError, load_settings
from src.vfs import VFS, VfsError


class CommandError(Exception):
    """Ошибка команды, о которой следует сообщить пользователю."""


def make_prompt():
    """Сформировать приглашение из имени пользователя и имени узла ОС."""
    return f"{getpass.getuser()}@{socket.gethostname()}:~$ "


def execute_line(line, strict=False):
    """Разобрать строку и исполнить команду-заглушку."""
    try:
        words = shlex.split(line, comments=True)
    except ValueError as error:
        report_error(f"ошибка разбора: {error}", strict)
        return True

    if not words:
        return True

    command, *arguments = words
    if command == "exit":
        if arguments:
            report_error("exit: аргументы не поддерживаются", strict)
            return True
        return False
    if command in ("ls", "cd"):
        print(f"{command}: {arguments!r}")
        return True
    report_error(f"команда не найдена: {command}", strict)
    return True


def report_error(message, strict):
    """Напечатать ошибку или передать ее стартовому сценарию."""
    if strict:
        raise CommandError(message)
    print(f"shell: {message}")


def run_startup(path):
    """Исполнить сценарий, показывая ввод и вывод как в диалоге."""
    error_flag = False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise CommandError(f"не удалось прочитать сценарий {path}: {error}") \
            from error
    for number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        print(f"{make_prompt()}{line}")
        try:
            if not execute_line(line, strict=True):
                return False
        except CommandError as error:
            print("error: ", error)
            error_flag = True
    if error_flag:
        raise CommandError(f"error in startup script")
    return True


def run_repl():
    """Читать команды до exit или конца входного потока."""
    while True:
        try:
            line = input(make_prompt())
        except EOFError:
            print()
            return
        except KeyboardInterrupt:
            print()
            continue
        if not execute_line(line):
            return


def main(argv=None):
    """Прочитать настройки, выполнить сценарий и открыть REPL."""
    try:
        settings = load_settings(argv)
    except ConfigError as error:
        print(f"config: {error}")
        return 1
    print(f"config: {settings.config_path}")
    print(f"vfs: {settings.vfs_path}")
    print(f"startup: {settings.startup_script}")
    if settings.vfs_path:
        try:
            vfs = VFS.from_zip(settings.vfs_path)
        except VfsError as error:
            print(f"vfs: {error}")
            return 1
        message = vfs.motd()
        if message is not None:
            print(message, end="" if message.endswith("\n") else "\n")
    if settings.startup_script:
        try:
            if not run_startup(settings.startup_script):
                return 0
        except CommandError:
            print(f"Ошибка в стартовом скрипте.")
    run_repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
