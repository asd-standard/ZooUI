@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   ZooUI Windows Build Script
echo ============================================
echo.

REM ---- Verify windeps ----
if not exist "%~dp0windeps\libvips-42.dll" (
    echo [ERROR] windeps\libvips-42.dll not found!
    echo.
    echo Download vips-dev-w64 from:
    echo   https://github.com/libvips/libvips/releases
    echo Place libvips-42.dll in packaging\windeps\
    echo.
    exit /b 1
)

if not exist "%~dp0windeps\pdftoppm.exe" (
    echo [ERROR] windeps\pdftoppm.exe not found!
    echo.
    echo Download Poppler for Windows from:
    echo   https://github.com/oschwartz10612/poppler-windows/releases
    echo Place pdftoppm.exe in packaging\windeps\
    echo.
    exit /b 1
)

echo [OK] Native dependencies found.

REM ---- Install PyInstaller if needed ----
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller.
        exit /b 1
    )
)

REM ---- Build ----
echo.
echo [INFO] Building zooui.exe (this may take several minutes)...
echo.

pushd "%~dp0.."
pyinstaller "packaging\zooui.spec" --clean --noconfirm
set BUILD_RESULT=%errorlevel%
popd

if %BUILD_RESULT% neq 0 (
    echo.
    echo [ERROR] Build failed with exit code %BUILD_RESULT%.
    exit /b %BUILD_RESULT%
)

echo.
echo ============================================
echo   Build complete!
echo   Output: dist\zooui.exe
echo ============================================

exit /b 0
