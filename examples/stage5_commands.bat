@echo off
cd /d "%~dp0\.."
set "IMAGE=%TEMP%\kis_stage5_deep.zip"
python -m tests.make_fixtures deep "%IMAGE%"
python -m src.shell --vfs "%IMAGE%" --startup examples\stage5.start
python -m src.shell --vfs "%IMAGE%" --startup examples\stage5_error.start
del "%IMAGE%"
