@echo off
:: Clear the screen
cls

:: Set variables
set "APP_NAME=Ecalyptus Printer"
set "APP_VERSION=1.0.0"
set "DIST_PATH=dist"
set "BUILD_PATH=build"
set "INSTALLER_SCRIPT=installer_script.iss"

echo Cleaning previous builds...
if exist "%BUILD_PATH%" rmdir /s /q "%BUILD_PATH%"
if exist "%DIST_PATH%" rmdir /s /q "%DIST_PATH%"

echo Installing dependencies...
pip install -r requirement.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies!
    pause
    exit /b %errorlevel%
)

echo Building the application API with PyInstaller...
pyinstaller --onefile -F api/api.py --add-data "print.exe:." --clean --noconsole --name "ecal-printer-api"
if %errorlevel% neq 0 (
    echo API build failed!
    pause
    exit /b %errorlevel%
)

echo Building the application view with PyInstaller...
pyinstaller --onefile --add-data "dist/ecal-printer-api.exe:." --add-data "view:view" --add-data "app.ico:." --icon "app.ico" --noconsole --name "%APP_NAME% %APP_VERSION%" main.py
if %errorlevel% neq 0 (
    echo View build failed!
    pause
    exit /b %errorlevel%
)

echo Creating the installer with Inno Setup...
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo Inno Setup not found!
    pause
    exit /b 1
)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%INSTALLER_SCRIPT%"
if %errorlevel% neq 0 (
    echo Inno Setup build failed!
    pause
    exit /b %errorlevel%
)

echo Build and installer creation succeeded!
pause
