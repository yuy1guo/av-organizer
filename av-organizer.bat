@echo off
REM AV Organizer - Quick Launch Script
REM Usage: av-organizer.bat [directory] [options]

SET PYTHON3="C:\Users\郭羽仪\AppData\Local\Programs\Python\Python312\python.exe"
SET SCRIPT="C:\Users\郭羽仪\.config\opencode\skill\av-organizer\scripts\simple_organizer.py"

IF "%~1"=="" (
    echo Usage: av-organizer.bat ^<directory^> [--dry-run] [--first-only]
    echo.
    echo Examples:
    echo   av-organizer.bat "E:\迅雷下载" --dry-run
    echo   av-organizer.bat "E:\迅雷下载" --first-only
    echo   av-organizer.bat "E:\迅雷下载"
    exit /b 1
)

%PYTHON3% %SCRIPT% %*
