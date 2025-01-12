@echo off
echo Cleaning up build artifacts...

rem Remove the dist folder
if exist dist (
    rmdir /s /q dist
    echo Removed dist folder.
) else (
    echo No dist folder to remove.
)

rem Remove build.log if it exists
if exist build.log (
    del /q build.log
    echo Removed build log.
) else (
    echo No build log to remove.
)

echo Cleanup completed.
pause
