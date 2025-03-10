@echo off
:: Clear the screen
cls

:: Set variables
set "APP_NAME=Ecalyptus Printer Manager"
set "APP_VERSION=1.0.0"
set "DIST_PATH=dist"
set "BUILD_PATH=build"
set "INSTALLER_SCRIPT=installer_script.iss"
set "SIGNTOOL_PATH=C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe"
set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

:: Function to check error level and exit if failed
:check_error
if %errorlevel% neq 0 (
    echo Error occurred. Exiting with code %errorlevel%.
    pause
    exit /b %errorlevel%
)
goto :eof

echo Cleaning previous builds...
if exist "%BUILD_PATH%" rmdir /s /q "%BUILD_PATH%"
if exist "%DIST_PATH%" rmdir /s /q "%DIST_PATH%"

echo Installing dependencies...
pip install -r requirement.txt
call :check_error

echo Building the application API with PyInstaller...
pyinstaller --onefile --version-file=version_info.txt -F api/api.py --add-data "print.exe:." --clean --noconsole --name "ecal-printer-api"
call :check_error

echo Building the application view with PyInstaller...
pyinstaller --onefile --version-file=version_info.txt --add-data "dist/ecal-printer-api.exe:." --add-data "view:view" --add-data "app.ico:." --icon "app.ico" --noconsole --name "%APP_NAME%" main.py
call :check_error

echo Signing the application...
if not exist "%SIGNTOOL_PATH%" (
    echo SignTool not found at "%SIGNTOOL_PATH%".
    pause
    exit /b 1
)
"%SIGNTOOL_PATH%" sign /a /tr http://timestamp.digicert.com /td sha256 /fd sha256 /d "%APP_NAME%" /du "http://www.ecalyptus.healthcare" /n "Ecalyptus" "%DIST_PATH%\ecal-printer-api.exe"
call :check_error

echo Creating the installer with Inno Setup...
if not exist "%INNO_SETUP_PATH%" (
    echo Inno Setup not found at "%INNO_SETUP_PATH%".
    pause
    exit /b 1
)
"%INNO_SETUP_PATH%" "%INSTALLER_SCRIPT%"
call :check_error

echo Build and installer creation succeeded!
pause
exit /b 0
