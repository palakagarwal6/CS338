@echo off

set "install=n"

set /p install= Install necessary modules? (y/[n])
if "%install%"=="y" (
	call "%~dp0\scripts\install.bat"
)

python.exe "%~dp0\main.py"