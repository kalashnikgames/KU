@echo off
cd /d "%~dp0\.."
set "IMAGE=%TEMP%\kis_stage4_deep.zip"
python -m tests.make_fixtures deep "%IMAGE%"
python -m src.shell --vfs "%IMAGE%" --startup examples\stage4.start
python -m src.shell --vfs "%IMAGE%" --startup examples\stage4_error.start
del "%IMAGE%"
