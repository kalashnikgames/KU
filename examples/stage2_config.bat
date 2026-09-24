@echo off
cd /d "%~dp0\.."
python -m src.shell --vfs ignored.zip --startup ignored.start ^
  --config examples\config.yaml
