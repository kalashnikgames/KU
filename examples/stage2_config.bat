@echo off
cd /d "%~dp0\.."
python -m tests.make_fixtures minimal examples\sample.zip
python -m src.shell --vfs ignored.zip --startup ignored.start ^
  --config examples\config.yaml
del examples\sample.zip
