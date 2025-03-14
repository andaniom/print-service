@echo off
:: Clear the screen
cls

:: Set application variables
set "APP_NAME=Ecalyptus Printer Manager"
set "APP_VERSION=1.0.1"
set "DIST_PATH=dist"
set "BUILD_PATH=build"
set "INSTALLER_SCRIPT=installer_script.iss"
set "VERSION_FILE_API=version_files\version_api_info.txt"
set "VERSION_FILE_VIEW=version_files\version_view_info.txt"

:: Ensure version_files directory exists
if not exist "version_files" (
    echo Creating version_files directory...
    mkdir "version_files"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create version_files directory!
        pause
        exit /b 1
    )
)

:: Main script execution
call :main
exit /b %errorlevel%

:main
    :: Ensure version files exist
    call :ensure_version_file "%VERSION_FILE_API%" "ecal-printer-api" "ecal-printer-api.exe"
    call :ensure_version_file "%VERSION_FILE_VIEW%" "%APP_NAME%" "%APP_NAME%.exe"

    :: Clean previous builds
    call :clean_builds

    :: Install dependencies
    call :install_dependencies

    :: Build executables with PyInstaller
    call :build_executables

    :: Verify Inno Setup exists
    call :verify_inno_setup

    :: Create the installer
    call :create_installer

    :: Success message
    echo Build and installer creation succeeded!
    pause
    exit /b 0

:ensure_version_file
    :: Args: %1=output_file, %2=app_name, %3=exe_name
    echo Checking for %~1...
    if not exist "%~1" (
        echo Creating %~1 with default content...
        call :generate_version_file "%~1" "%~2" "%~3"
    )
    exit /b

:clean_builds
    echo Cleaning previous builds...
    if exist "%BUILD_PATH%" rmdir /s /q "%BUILD_PATH%"
    if exist "%DIST_PATH%" rmdir /s /q "%DIST_PATH%"
    exit /b

:install_dependencies
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b %errorlevel%
    )
    exit /b

:build_executables
    echo Building executables with PyInstaller...
    pyinstaller --onefile -F api/api.py --clean --noconsole --name "ecal-printer-api"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to build ecal-printer-api!
        pause
        exit /b %errorlevel%
    )

    pyinstaller --onefile --add-data dist/ecal-printer-api.exe:." --add-data "view:view" --add-data "app.ico:." --icon "app.ico" --noconsole --name "%APP_NAME%" main.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to build %APP_NAME%!
        pause
        exit /b %errorlevel%
    )
    exit /b

:verify_inno_setup
    echo Verifying Inno Setup installation...
    if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        echo ERROR: Inno Setup not found! Please install it to proceed.
        pause
        exit /b 1
    )
    exit /b

:create_installer
    echo Creating the installer with Inno Setup...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%INSTALLER_SCRIPT%"
    if %errorlevel% neq 0 (
        echo ERROR: Inno Setup build failed!
        pause
        exit /b %errorlevel%
    )
    exit /b

:generate_version_file
    :: Args: %1=output_file, %2=app_name, %3=exe_name
    echo Generating version info file at: %~1...

    :: Verify the directory path is accessible
    for %%F in ("%~1") do (
        if not exist "%%~dpF" (
            echo ERROR: Directory %%~dpF does not exist!
            pause
            exit /b 1
        )
    )

    :: Write the version info file
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
        echo                  StringStruct(u'FileDescription', u'%~2'),
        echo                  StringStruct(u'FileVersion', u'%APP_VERSION%'),
        echo                  StringStruct(u'InternalName', u'%~2'),
        echo                  StringStruct(u'OriginalFilename', u'%~3'),
        echo                  StringStruct(u'ProductName', u'%~2'),
        echo                  StringStruct(u'ProductVersion', u'%APP_VERSION%')])
        echo             ]),
        echo         VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
        echo     ]
        echo )
    ) > "%~1"

    :: Verify the file was created
    if not exist "%~1" (
        echo ERROR: Failed to create version info file: %~1
        pause
        exit /b 1
    )
    echo Successfully created version info file: %~1
    exit /b