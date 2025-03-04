@echo off
:: Clear the screen
cls

:: Set variables
set "APP_NAME=Ecalyptus Printer"
set "DIST_PATH=dist"
set "BUILD_PATH=build"
set "INSTALLER_SCRIPT=installer_script.iss"

echo Building the application api with PyInstaller...

:: Remove previous build and dist directories
if exist "%BUILD_PATH%" rmdir /s /q "%BUILD_PATH%"
if exist "%DIST_PATH%" rmdir /s /q "%DIST_PATH%"

:: Use PyInstaller to create the executable

pyinstaller --onefile -F api/api.py --clean --noconsole  
echo Building the application view with PyInstaller...
pyinstaller --onefile --add-data "dist/api.exe:." --add-data "view:view" --add-data "print.exe:." --add-data "app.ico:." --icon "app.ico" --noconsole --name "Ecalyptus Printer" main.py

if %errorlevel% neq 0 (
    echo PyInstaller build failed!
    pause
    exit /b %errorlevel%
)

echo PyInstaller build succeeded!

:: Copy necessary files if required
:: xcopy assets "%DIST_PATH%\assets" /s /i /y

echo Creating the installer with Inno Setup...

:: Run Inno Setup to create the installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%INSTALLER_SCRIPT%"

if %errorlevel% neq 0 (
    echo Inno Setup build failed!
    pause
    exit /b %errorlevel%
)

echo Installer created successfully!

pause