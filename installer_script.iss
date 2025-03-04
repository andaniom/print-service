[Setup]
AppPublisher=Ecalyptus
AppPublisherURL=http://www.ecalyptus.healthcare
AppName=Ecalyptus Printer
AppVersion=1.0
DefaultDirName={pf}\Ecalyptus Printer
DefaultGroupName=Ecalyptus Printer
OutputDir=.
OutputBaseFilename=EcalyptusPrinterInstaller
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\app.ico
SetupIconFile=app.ico

[Files]
; Include the PyInstaller executable
Source: "dist\Ecalyptus Printer.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include additional files and folders
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion
; Include additional files and folders
Source: "local.db"; DestDir: "{app}"; Flags: ignoreversion
; Include additional files and folders
Source: "dist/api.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include additional files and folders
Source: "backend.log"; DestDir: "{app}"; Flags: ignoreversion
; Include additional files and folders
Source: "print.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create a shortcut in the Start Menu
Name: "{group}\Ecalyptus Printer"; Filename: "{app}\Ecalyptus Printer.exe"; IconFilename: "{app}\app.ico"
; Create a desktop shortcut (optional)
Name: "{commondesktop}\Ecalyptus Printer"; Filename: "{app}\Ecalyptus Printer.exe"; IconFilename: "{app}\app.ico"

[Run]
; Optionally run the application after installation
Filename: "{app}\Ecalyptus Printer.exe"; Description: "Run Ecalyptus Printer"; Flags: nowait postinstall skipifsilent