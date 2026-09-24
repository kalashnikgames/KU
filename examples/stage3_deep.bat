@echo off
cd /d "%~dp0\.."
set "IMAGE=%TEMP%\kis_stage3_deep.zip"
python -m tests.make_fixtures deep "%IMAGE%"
python -m src.shell --vfs "%IMAGE%" --startup examples\stage3.start
python -m src.shell --vfs "%IMAGE%" --startup examples\stage3_error.start
del "%IMAGE%"
