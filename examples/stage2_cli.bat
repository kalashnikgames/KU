@echo off
cd /d "%~dp0\.."
python -m src.shell --vfs examples\sample.zip --startup examples\stage2.start
