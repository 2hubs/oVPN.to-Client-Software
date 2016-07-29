; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
#include "inno.release"
#define AppName "oVPN.to Client"
#define AppDir "oVPN.to Client for Windows"
#define AppPublisher "oVPN.to Anonymous Services"
#define AppURL "https://oVPN.to"
#define AppExeName "ovpn_client.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
SignTool=signtool1
;SignTool=signtool2
;SignTool=signtool3
SignTool=signtool4
SignedUninstaller=yes
Compression=lzma2/max
;Compression=bzip/9
SolidCompression=yes
AppId={{991F58FC-8D40-4B45-B434-6A10AAC12FBA}
AppName={#AppName}
AppVersion=v{#Version}-gtk3_win64
;AppVersion=v{#Version}-win64
AppMutex={#AppExeName},Global\{#AppExeName}
SetupMutex={#AppDir},Global\{#AppDir}
AppVerName={#AppName} v{#Version}-gtk3_win64
;AppVerName={#AppName} v{#Version}-win64
AppPublisher={#AppPublisher}
AppContact={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL=https://vcp.ovpn.to/?site=support
AppUpdatesURL=https://board.ovpn.to/v4/index.php?thread/57314-ovpn-client-for-windows-beta-binary-releases/&action=firstNew
AppReadmeFile={#AppURL}
VersionInfoVersion=0.{#Version}
AppCopyright=Copyright (C) 2016 oVPN.to
DefaultDirName={pf64}\{#AppDir}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=ovpn_client_v{#Version}-gtk3_win64_setup
;OutputBaseFilename=oVPN.to-Client-v{#Version}-win64-setup
SetupIconFile=else\app_icons\shield_exe.ico
WizardImageFile=else\app_icons\shield_exe_2.bmp
WizardSmallImageFile=else\app_icons\shield_exe.bmp
WizardImageStretch=no
UninstallDisplayIcon={app}\{#AppExeName}
Uninstallable=not IsTaskSelected('portablemode')
DisableDirPage=no
LicenseFile=LICENSE
LanguageDetectionMethod=uilanguage
ShowLanguageDialog=auto

[Tasks]
Name: portablemode; Description: "Portable Mode"; Flags: unchecked

[InstallDelete]
Type: files; Name: "{userdesktop}\oVPN.to Client for Windows.lnk";
Type: files; Name: "{commondesktop}\oVPN.to Client for Windows.lnk";
Type: filesandordirs; Name: {app}\dns\;
Type: filesandordirs; Name: {app}\etc\;
Type: filesandordirs; Name: {app}\lib\;
Type: filesandordirs; Name: {app}\locale\;
Type: filesandordirs; Name: {app}\share\;
Type: filesandordirs; Name: {app}\ico\;
Type: filesandordirs; Name: {app}\Microsoft.VC90.CRT\;
Type: files; Name: {app}\*.dll;
Type: files; Name: {app}\*.pyd;
Type: files; Name: {app}\*.zip;
Type: files; Name: {app}\*.pem;
Type: files; Name: {app}\{#AppExeName};

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
Name: "corsican"; MessagesFile: "compiler:Languages\Corsican.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "greek"; MessagesFile: "compiler:Languages\Greek.isl"
Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "scottishgaelic"; MessagesFile: "compiler:Languages\ScottishGaelic.isl"
Name: "serbiancyrillic"; MessagesFile: "compiler:Languages\SerbianCyrillic.isl"
Name: "serbianlatin"; MessagesFile: "compiler:Languages\SerbianLatin.isl"
Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\*.*"; DestDir: "{app}"; Flags:replacesameversion recursesubdirs

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
;Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runascurrentuser

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: string; ValueName: "{app}\{#AppExeName}"; ValueData: "~ HIGHDPIAWARE"; Flags: noerror uninsdeletevalue