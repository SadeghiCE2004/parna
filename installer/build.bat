@echo off
setlocal
pushd "%~dp0\.."

set "SPEC_FILE="
for %%F in (*.spec) do if exist "%%~fF" set "SPEC_FILE=%%~fF"

if not defined SPEC_FILE (
    echo No PyInstaller spec file found in the project root.
    popd
    exit /b 1
)

python -m PyInstaller --noconfirm --clean --distpath dist --workpath build "%SPEC_FILE%"
set "BUILD_STATUS=%ERRORLEVEL%"
popd
exit /b %BUILD_STATUS%