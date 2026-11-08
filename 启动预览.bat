@echo off
setlocal
cd /d "%~dp0"

set "PY="
python -c "import sys" >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY (
  py -3 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
  echo.
  echo Python 3 was not found.
  echo Install Python 3.10+ from https://www.python.org/downloads/
  echo.
  pause
  exit /b 1
)

echo Starting UI Atlas...
%PY% "serve.py" %1
if errorlevel 1 pause
