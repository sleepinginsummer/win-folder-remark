; Inno Setup Script for Folder Remark

[Setup]
AppName=Folder Remark
AppVersion=0.1.0
DefaultDirName={pf}\FolderRemark
DefaultGroupName=Folder Remark
UninstallDisplayIcon={app}\remark.ico
SetupIconFile=D:\share\project\rust-project\folder-remark-rust\assets\remark.ico
OutputDir=.
OutputBaseFilename=FolderRemarkSetup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\share\project\rust-project\folder-remark-rust\target\release\folder-remark-rust.exe"; DestDir: "{app}"; DestName: "folder-remark.exe"; Flags: ignoreversion
Source: "D:\share\project\rust-project\folder-remark-rust\assets\remark.ico"; DestDir: "{app}"; DestName: "remark.ico"; Flags: ignoreversion

[Icons]
Name: "{group}\Folder Remark"; Filename: "{app}\folder-remark.exe"; IconFilename: "{app}\remark.ico"
Name: "{group}\Uninstall Folder Remark"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Folder Remark"; Filename: "{app}\folder-remark.exe"; IconFilename: "{app}\remark.ico"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: "Directory\shell\FolderRemark"; ValueType: string; ValueName: ""; ValueData: "Add Folder Remark"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\FolderRemark"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\remark.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\FolderRemark\command"; ValueType: string; ValueName: ""; ValueData: """{app}\folder-remark.exe"" ""%V"""; Flags: uninsdeletekey

[CustomMessages]
ContextMenuTitle=Add Folder Remark
