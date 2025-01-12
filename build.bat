@echo off
rem Define variables
set PYINSTALLER=pyinstaller
set SCRIPT=src\main.py
set OUTPUT_DIR=dist
set TEMP_DIR=temp

rem Create temp directory for spec and build files
if not exist %TEMP_DIR% mkdir %TEMP_DIR%

rem Build the executable
echo Building executable with PyInstaller...
%PYINSTALLER% --onefile %SCRIPT% --specpath %TEMP_DIR% --workpath %TEMP_DIR% --distpath %OUTPUT_DIR%

rem Cleanup temp directory
if exist %TEMP_DIR% (
    rmdir /s /q %TEMP_DIR%
)

rem Check if the build was successful
if exist %OUTPUT_DIR% (
    echo Build completed successfully. Check the %OUTPUT_DIR% directory for the executable.
) else (
    echo Build failed. Please check for errors.
)

pause
