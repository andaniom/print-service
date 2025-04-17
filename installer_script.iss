[Setup]
AppPublisher=Ecalyptus
AppPublisherURL=http://www.ecalyptus.healthcare
AppName=Ecalyptus Printer Manager
AppVersion=1.0.2
DefaultDirName={pf}\Ecalyptus Printer Manager
DefaultGroupName=Ecalyptus Printer Manager
OutputDir=.
OutputBaseFilename=EcalyptusPrinterInstaller
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\app.ico
SetupIconFile=app.ico
DisableProgramGroupPage=yes
LicenseFile=license.txt

[Files]
; Include the main executable
Source: "dist\Ecalyptus Printer Manager.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include additional files
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "local.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ecal-printer-api.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "backend.log"; DestDir: "{app}"; Flags: ignoreversion
Source: "GSPRINT\*"; DestDir: "{app}\GSPRINT"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "GHOSTSCRIPT\*"; DestDir: "{app}\GHOSTSCRIPT"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\Ecalyptus Printer Manager"; Filename: "{app}\Ecalyptus Printer Manager.exe"; IconFilename: "{app}\app.ico"
; Desktop shortcut
Name: "{commondesktop}\Ecalyptus Printer Manager"; Filename: "{app}\Ecalyptus Printer Manager.exe"; IconFilename: "{app}\app.ico"

[Run]
; Run the application after installation
Filename: "{app}\Ecalyptus Printer Manager.exe"; Description: "Run Ecalyptus Printer Manager"; Flags: nowait postinstall skipifsilent

[Registry]
; Add to startup (optional)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
      ValueType: string; ValueName: "EcalyptusPrinterManager"; \
      ValueData: "{app}\Ecalyptus Printer Manager.exe"; Flags: uninsdeletevalue

[UninstallDelete]
; Remove local.db on uninstallation
Type: files; Name: "{app}\local.db"
