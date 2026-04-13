; -----------------------------------------------------------------
;  ARYA OS v2.0 NEURAL CORE - INNO SETUP SCRIPT
; -----------------------------------------------------------------
[Setup]
AppId={{ARYA-OS-V2-NEURAL-CORE-PRIME-2026}}
AppName=ARYA OS
AppVersion=2.0
AppPublisher=Abhijeet Mishra
DefaultDirName={autopf}\ARYA_OS
DefaultGroupName=ARYA OS
OutputDir=.
OutputBaseFilename=ARYA_OS_v2_Setup
SetupIconFile=arya_logo_alt.ico
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Source is the PyInstaller output
Source: "dist\ARYA_OS_v2.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ARYA OS"; Filename: "{app}\ARYA_OS_v2.exe"
Name: "{group}\{cm:UninstallProgram,ARYA OS}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ARYA OS"; Filename: "{app}\ARYA_OS_v2.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ARYA_OS_v2.exe"; Description: "{cm:LaunchProgram,ARYA OS}"; Flags: nowait postinstall skipifsilent runascurrentuser
