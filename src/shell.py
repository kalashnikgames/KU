"""Минимальная интерактивная оболочка (этап 1)."""

import getpass
import shlex
import socket


def make_prompt():
    """Сформировать приглашение из имени пользователя и имени узла ОС."""
    return f"{getpass.getuser()}@{socket.gethostname()}:~$ "


def execute_line(line):
    """Разобрать строку и исполнить команду-заглушку."""
    try:
        words = shlex.split(line)
    except ValueError as error:
        print(f"shell: ошибка разбора: {error}")
        return True

    if not words:
        return True

    command, *arguments = words
    if command == "exit":
        if arguments:
            print("exit: аргументы не поддерживаются")
            return True
        return False
    if command in ("ls", "cd"):
        print(f"{command}: {arguments!r}")
        return True
    print(f"shell: команда не найдена: {command}")
    return True


def main():
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


if __name__ == "__main__":
    main()
