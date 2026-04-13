[Setup]
; App Information
AppName=ARYA OS
AppVersion=1.0
AppPublisher=Abhijeet Mishra
AppPublisherURL=http://abhijeetmishra.info/

; Destination Folder (Usually C:\Program Files\ARYA OS)
DefaultDirName={autopf}\ARYA OS
DefaultGroupName=ARYA OS

; Output Installer Name/Location
OutputDir=D:\Jarvis\Output
OutputBaseFilename=ARYA_OS_Setup_v1.0
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=D:\Jarvis\arya_logo_alt.ico

; Ask for desktop shortcut
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; THIS IS THE CRITICAL LINE: It grabs everything PyInstaller generated
Source: "D:\Jarvis\dist\ARYA OS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu Shortcut
Name: "{group}\ARYA OS"; Filename: "{app}\ARYA OS.exe"
Name: "{group}\{cm:UninstallProgram,ARYA OS}"; Filename: "{uninstallexe}"

; Desktop Shortcut
Name: "{autodesktop}\ARYA OS"; Filename: "{app}\ARYA OS.exe"; Tasks: desktopicon

[Run]
; Option to launch ARYA OS immediately after installing
Filename: "{app}\ARYA OS.exe"; Description: "Launch ARYA OS"; Flags: nowait postinstall skipifsilent runascurrentuser
