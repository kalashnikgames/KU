"""Параметры запуска и простой YAML-файл с путями."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """Ошибка чтения или структуры конфигурации."""


@dataclass(frozen=True)
class Settings:
    """Итоговые пути, переданные эмулятору."""

    vfs_path: Path | None
    startup_script: Path | None
    config_path: Path | None


def parse_scalar(value):
    """Прочитать строковый скаляр YAML: обычный или в кавычках."""
    if value.startswith('"'):
        try:
            result, position = json.JSONDecoder().raw_decode(value)
        except json.JSONDecodeError as error:
            raise ConfigError(f"неверная строка YAML: {error}") from error
        remainder = value[position:].strip()
    elif value.startswith("'"):
        result, remainder = parse_single_quoted(value)
    else:
        result = value.split(" #", maxsplit=1)[0].strip()
        remainder = ""
    if remainder and not remainder.startswith("#"):
        raise ConfigError("лишний текст после значения YAML")
    if not isinstance(result, str) or not result:
        raise ConfigError("путь должен быть непустой строкой")
    return result


def parse_single_quoted(value):
    """Прочитать одинарные кавычки YAML с удвоенными апострофами."""
    characters = []
    position = 1
    while position < len(value):
        character = value[position]
        if character == "'":
            if value[position + 1:position + 2] == "'":
                characters.append("'")
                position += 2
                continue
            return "".join(characters), value[position + 1:].strip()
        characters.append(character)
        position += 1
    raise ConfigError("незакрытая строка YAML")


def read_yaml(path):
    """Считать YAML-карту из двух допустимых строковых полей."""
    values = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ConfigError(f"не удалось прочитать {path}: {error}") from error
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, raw_value = stripped.partition(":")
        if not separator or key not in ("vfs_path", "startup_script"):
            raise ConfigError(f"{path}:{number}: неверное поле YAML")
        if key in values:
            raise ConfigError(f"{path}:{number}: повтор поля {key}")
        values[key] = parse_scalar(raw_value.strip())
    return values


def resolve_path(value, base):
    """Разрешить относительный путь от указанного каталога."""
    if value is None:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else base / path


def load_settings(argv=None):
    """Прочитать CLI и YAML; поля файла перекрывают поля CLI."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки UNIX")
    parser.add_argument("--vfs", "--vfs-path", dest="vfs_path")
    parser.add_argument("--startup", "--startup-script")
    parser.add_argument("--config", type=Path)
    args = parser.parse_args(argv)
    config_path = args.config.resolve() if args.config else None
    values = read_yaml(config_path) if config_path else {}
    config_base = config_path.parent if config_path else Path.cwd()
    vfs_value = values.get("vfs_path")
    script_value = values.get("startup_script")
    vfs_path = resolve_path(vfs_value, config_base)
    script_path = resolve_path(script_value, config_base)
    if vfs_path is None:
        vfs_path = resolve_path(args.vfs_path, Path.cwd())
    if script_path is None:
        script_path = resolve_path(args.startup, Path.cwd())
    return Settings(vfs_path, script_path, config_path)
