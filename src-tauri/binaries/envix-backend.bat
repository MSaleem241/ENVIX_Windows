@echo off
rem Launch the Python backend for ENVIX
set "SCRIPT_DIR=%~dp0..\\..\\backend"
python "%SCRIPT_DIR%\\api_server.py" %*
