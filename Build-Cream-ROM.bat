@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Build-Cream-ROM.ps1"
set "BUILD_EXIT=%ERRORLEVEL%"
echo.
pause
exit /b %BUILD_EXIT%
