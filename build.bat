@echo off
:: Clear the screen
cls

:: Set variables
set "APP_NAME=Ecalyptus Printer Manager"
set "APP_VERSION=1.0.0"
set "DIST_PATH=dist"
set "BUILD_PATH=build"
set "INSTALLER_SCRIPT=installer_script.iss"
set "VERSION_FILE=version_info.txt"
set "VERSION_FILE_API=version_api_info.txt"

:: Clear old builds
echo Cleaning previous builds...
if exist "%BUILD_PATH%" rmdir /s /q "%BUILD_PATH%"
if exist "%DIST_PATH%" rmdir /s /q "%DIST_PATH%"

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies!
    pause
    exit /b %errorlevel%
)

:: Create version api info file
echo Generating version info file...
(
    echo # UTF-8 version resource file
    echo VSVersionInfo(
    echo     ffi=FixedFileInfo(
    echo         filevers=(1, 0, 0, 0),
    echo         prodvers=(1, 0, 0, 0),
    echo         mask=0x3f,
    echo         flags=0x0,
    echo         OS=0x4,
    echo         fileType=0x1,
    echo         subtype=0x0,
    echo         date=(0, 0)
    echo     ),
    echo     kids=[
    echo         StringFileInfo(
    echo             [
    echo             StringTable(
    echo                 u'040904b0',
    echo                 [StringStruct(u'CompanyName', u'Ecalyptus'),
    echo                  StringStruct(u'FileDescription', u'ecal-printer-api'),
    echo                  StringStruct(u'FileVersion', u'%APP_VERSION%'),
    echo                  StringStruct(u'InternalName', u'ecal-printer-api'),
    echo                  StringStruct(u'OriginalFilename', u'ecal-printer-api.exe'),
    echo                  StringStruct(u'ProductName', u'ecal-printer-api'),
    echo                  StringStruct(u'ProductVersion', u'%APP_VERSION%')])
    echo             ]),
    echo         VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    echo     ]
    echo )
) > "%VERSION_FILE_API%"

:: Create version info file
echo Generating version info file...
(
    echo # UTF-8 version resource file
    echo VSVersionInfo(
    echo     ffi=FixedFileInfo(
    echo         filevers=(1, 0, 0, 0),
    echo         prodvers=(1, 0, 0, 0),
    echo         mask=0x3f,
    echo         flags=0x0,
    echo         OS=0x4,
    echo         fileType=0x1,
    echo         subtype=0x0,
    echo         date=(0, 0)
    echo     ),
    echo     kids=[
    echo         StringFileInfo(
    echo             [
    echo             StringTable(
    echo                 u'040904b0',
    echo                 [StringStruct(u'CompanyName', u'Ecalyptus'),
    echo                  StringStruct(u'FileDescription', u'%APP_NAME%'),
    echo                  StringStruct(u'FileVersion', u'%APP_VERSION%'),
    echo                  StringStruct(u'InternalName', u'%APP_NAME%'),
    echo                  StringStruct(u'OriginalFilename', u'%APP_NAME%.exe'),
    echo                  StringStruct(u'ProductName', u'%APP_NAME%'),
    echo                  StringStruct(u'ProductVersion', u'%APP_VERSION%')])
    echo             ]),
    echo         VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    echo     ]
    echo )
) > "%VERSION_FILE%"

:: Build the API with PyInstaller
echo Building the application API with PyInstaller...
pyinstaller --onefile -F api/api.py --clean --noconsole --name "ecal-printer-api" --version-file "%VERSION_FILE_API%"
if %errorlevel% neq 0 (
    echo API build failed!
    pause
    exit /b %errorlevel%
)

:: Build the View with PyInstaller
echo Building the application view with PyInstaller...
pyinstaller --onefile ^
--add-data "dist/ecal-printer-api.exe;." ^
--add-data "view;view" ^
--add-data "app.ico;." ^
--icon "app.ico" --noconsole ^
--name "%APP_NAME%" ^
--version-file "%VERSION_FILE%" ^
main.py
if %errorlevel% neq 0 (
    echo View build failed!
    pause
    exit /b %errorlevel%
)

:: Verify Inno Setup exists
echo Checking for Inno Setup...
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo Inno Setup not found! Please install it to proceed.
    pause
    exit /b 1
)

:: Create the installer
echo Creating the installer with Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%INSTALLER_SCRIPT%"
if %errorlevel% neq 0 (
    echo Inno Setup build failed!
    pause
    exit /b %errorlevel%
)

echo Build and installer creation succeeded!
pause
