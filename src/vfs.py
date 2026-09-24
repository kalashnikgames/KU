"""Виртуальная файловая система, загружаемая из ZIP в память."""

import base64
import io
import posixpath
import zipfile
from pathlib import Path


class VfsError(Exception):
    """Ошибка образа виртуальной файловой системы."""


class VFS:
    """Хранить пути и base64-содержимое файлов только в памяти."""

    def __init__(self):
        """Создать пустой корень."""
        self.directories = {"/"}
        self.files = {}

    @classmethod
    def from_zip(cls, path):
        """Прочитать ZIP, не распаковывая его на диск."""
        try:
            archive_bytes = Path(path).read_bytes()
            archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
            with archive:
                vfs = cls()
                for entry in archive.infolist():
                    vfs.add_entry(entry, archive)
                return vfs
        except (OSError, zipfile.BadZipFile, RuntimeError) as error:
            raise VfsError(f"не удалось прочитать VFS {path}: {error}") from error

    def add_entry(self, entry, archive):
        """Добавить безопасный путь из ZIP и его родительские каталоги."""
        raw = entry.filename.replace("\\", "/")
        parts = raw.strip("/").split("/")
        if raw.startswith("/") or any(part in ("", ".", "..") for part in parts):
            raise VfsError(f"недопустимый путь в ZIP: {raw}")
        path = "/" + "/".join(parts)
        parent = posixpath.dirname(path)
        while parent not in self.directories:
            self.directories.add(parent)
            parent = posixpath.dirname(parent)
        if path in self.files:
            raise VfsError(f"повтор пути в ZIP: {path}")
        if entry.is_dir():
            self.directories.add(path)
        else:
            if path in self.directories:
                raise VfsError(f"файл совпадает с каталогом: {path}")
            data = archive.read(entry)
            self.files[path] = base64.b64encode(data).decode("ascii")

    def read_bytes(self, path):
        """Получить исходные байты файла из base64-представления."""
        if path not in self.files:
            raise VfsError(f"файл не найден: {path}")
        return base64.b64decode(self.files[path])

    def motd(self):
        """Вернуть текст корневого motd или None, если файла нет."""
        if "/motd" not in self.files:
            return None
        return self.read_bytes("/motd").decode("utf-8", errors="replace")
