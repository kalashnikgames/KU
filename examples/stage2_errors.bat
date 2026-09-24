@echo off
cd /d "%~dp0\.."
python -m src.shell --config examples\missing.yaml
python -m src.shell --startup examples\missing.start
