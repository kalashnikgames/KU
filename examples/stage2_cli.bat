@echo off
cd /d "%~dp0\.."
python -m tests.make_fixtures minimal examples\sample.zip
python -m src.shell --vfs examples\sample.zip --startup examples\stage2.start
del examples\sample.zip
