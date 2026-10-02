@echo off
cd /d "%~dp0\.."
set "IMAGE=%TEMP%\kis_stage3_minimal.zip"
python -m tests.make_fixtures minimal "%IMAGE%"
python -m src.shell --vfs "%IMAGE%" --startup examples\stage3.start
del "%IMAGE%"
