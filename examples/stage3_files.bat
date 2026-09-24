@echo off
cd /d "%~dp0\.."
set "IMAGE=%TEMP%\kis_stage3_files.zip"
python -m tests.make_fixtures files "%IMAGE%"
echo exit | python -m src.shell --vfs "%IMAGE%"
del "%IMAGE%"
